# cmdhlp

使用 AI 翻译或解释命令行帮助文本。

hlp 来自 help，执行 help 命令时，看到满满的英文文档，总会不由自主的"呃呃(ee)，看不懂啊"，
还是问下 AI 好了，长久以往，浪费了时间不说，还没有顺带学到这个命令其他隐藏的高级用法。
现在，我们只需要 help，但不需要呃(e)了，故名 hlp。

> 目前仅支持 DeepSeek 模型及中文输出。选择 DeepSeek 是因为其响应速度快、性价比高，非常适合翻译这类对实时性要求较高的场景。其他语言及其他 AI 模型将在后续更新中逐步补充。

包名：`cmdhlp` | 命令：`hlp`

## 演示

**原始命令输出：**

![原始命令输出](img/raw-help.gif)

**hlp trans（或快捷方式 TT）：**

![hlp trans 演示](img/hlp-trans.gif)

**hlp expl（或快捷方式 EE）：**

![hlp expl 演示](img/hlp-expl.gif)

## 安装

```bash
pip install cmdhlp
# 或
pipx install cmdhlp
```

> 如果安装后提示 `hlp` 命令不存在，请留意 `pip install` 输出中的 PATH 警告信息，将提示的目录添加到你的 shell 配置文件中（如 `~/.zshrc` 或 `~/.bashrc`）。

## 快速开始

```bash
# 1. 设置 DeepSeek API Key（申请地址：https://platform.deepseek.com/api_keys）
hlp config set api_key sk-your-key-here

# 2. 注册快捷方式（可选）
hlp init
source ~/.zshrc  # 或重启终端

# 3. 开始使用
nvm --help | hlp trans    # 翻译帮助文本为中文
nvm --help | hlp expl     # 用中文解释命令用法

# 使用快捷方式（执行 hlp init 后可用）：
nvm --help | TT           # 等同于 hlp trans
nvm --help | EE           # 等同于 hlp expl
```

## 命令列表

| 命令 | 说明 |
|---|---|
| `hlp trans` | 翻译管道输入的帮助文本为中文 |
| `hlp expl` | 用中文解释管道输入的帮助文本 |
| `hlp config set <key> <value>` | 设置配置项（api_key、model、base_url） |
| `hlp config show` | 查看当前配置 |
| `hlp config reset` | 重置配置为默认值 |
| `hlp init` | 注册 shell 快捷方式（TT、EE） |
| `hlp uninit` | 移除 shell 快捷方式 |

## 配置

配置文件路径：`~/.config/hlp/config.json`

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `api_key` | （空） | [DeepSeek API Key](https://platform.deepseek.com/api_keys) |
| `model` | `deepseek-chat` | 模型名称 |
| `base_url` | `https://api.deepseek.com` | API 地址 |

环境变量 `DEEPSEEK_API_KEY` 会覆盖配置文件中的值。

## 协议

AGPL-3.0
