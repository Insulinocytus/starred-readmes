"""Mirror README.md of every public starred repo into github.com/<owner>/<repo>.md."""
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

TOKEN = os.environ["GH_TOKEN"]
ROOT = Path(__file__).resolve().parents[2]  # repo root (.github/scripts/sync.py)
OUT = ROOT / "github.com"
BATCH = 50
RETRIES = 2


def request(url, data=None, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": accept,
        "User-Agent": "starred-readmes",
    })
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == RETRIES or e.code not in (403, 429, 500, 502, 503, 504):
                raise
        except (OSError, http.client.HTTPException):  # network drop, timeout, truncated body
            if attempt == RETRIES:
                raise
        time.sleep(10 * (attempt + 1))


def graphql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    res = json.loads(request("https://api.github.com/graphql", body))
    # NOT_FOUND = repo vanished after listing; treat as "no file" rather than a failure.
    errors = [e for e in res.get("errors", []) if e.get("type") != "NOT_FOUND"]
    if errors:
        sys.exit(f"GraphQL error: {errors}")
    return res["data"]


def starred():
    repos, after = [], None
    while True:
        data = graphql("""query($after: String) {
          viewer { starredRepositories(first: 100, after: $after) {
            pageInfo { hasNextPage endCursor }
            nodes { nameWithOwner isPrivate }
          } }
        }""", {"after": after})["viewer"]["starredRepositories"]
        repos += [n["nameWithOwner"] for n in data["nodes"] if not n["isPrivate"]]
        if not data["pageInfo"]["hasNextPage"]:
            return repos
        after = data["pageInfo"]["endCursor"]


def fetch(targets):
    """targets: list of (key, owner, name, ref, path). Returns {key: bytes | None}."""
    results = {}
    for i in range(0, len(targets), BATCH):
        chunk = targets[i:i + BATCH]
        params, fields, variables = [], [], {}
        for j, (_, owner, name, ref, path) in enumerate(chunk):
            params.append(f"$o{j}: String!, $n{j}: String!, $e{j}: String!")
            fields.append(f"r{j}: repository(owner: $o{j}, name: $n{j}) {{ object(expression: $e{j}) "
                          "{ ... on Blob { text isBinary isTruncated } } }")
            variables |= {f"o{j}": owner, f"n{j}": name, f"e{j}": f"{ref or 'HEAD'}:{path}"}
        t = time.monotonic()
        data = graphql(f"query({', '.join(params)}) {{ {' '.join(fields)} }}", variables)
        print(f"batch {i // BATCH + 1}: {len(chunk)} repos, {time.monotonic() - t:.1f}s", file=sys.stderr)
        for j, (key, owner, name, ref, path) in enumerate(chunk):
            blob = (data.get(f"r{j}") or {}).get("object") or {}
            if "text" not in blob:  # missing file, or path is a tree
                results[key] = None
            elif blob["isBinary"] or blob["isTruncated"] or blob["text"] is None:
                url = f"https://api.github.com/repos/{owner}/{name}/contents/{urllib.parse.quote(path)}"
                if ref:
                    url += "?ref=" + urllib.parse.quote(ref, safe="")
                results[key] = request(url, accept="application/vnd.github.raw")
            else:
                results[key] = blob["text"].encode()
    return results


def main():
    overrides = yaml.safe_load((ROOT / "overrides.yaml").read_text()) or {}
    repos = starred()
    keys = {f"github.com/{r}" for r in repos}

    targets = []
    for r in repos:
        o = overrides.get(f"github.com/{r}") or {}
        if not o.get("skip"):
            owner, name = r.split("/")
            targets.append((f"github.com/{r}", owner, name, o.get("ref"), o.get("path", "README.md")))
    results = fetch(targets)

    written = set()
    for key, content in results.items():
        if content is None:
            continue
        f = ROOT / f"{key}.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        if not f.exists() or f.read_bytes() != content:
            f.write_bytes(content)
        written.add(f)

    removed = 0
    for f in OUT.glob("*/*.md") if OUT.exists() else []:
        if f not in written:
            f.unlink()
            removed += 1
    for d in OUT.glob("*/") if OUT.exists() else []:
        if not any(d.iterdir()):
            d.rmdir()

    missing = sorted(k for k, v in results.items() if v is None and k not in overrides)
    broken = sorted(k for k, v in results.items() if v is None and k in overrides)
    unknown = sorted(set(overrides) - keys)
    lines = [
        f"## Sync result\n\nstarred (public): {len(repos)}, written: {len(written)}, "
        f"skipped: {len(repos) - len(targets)}, removed stale: {removed}\n",
        f"### Override broken ({len(broken)})", *[f"- {k}" for k in broken], "",
        f"### Override for unstarred repo ({len(unknown)})", *[f"- {k}" for k in unknown], "",
        f"### No README.md ({len(missing)})", *[f"- {k}" for k in missing],
    ]
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    with open(summary, "a") if summary else sys.stdout as out:
        out.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
