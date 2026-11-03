# Rust Tutorial

Rust 是一门近年来快速发展的系统级编程语言。

它兼具高性能与内存安全, 广泛应用于嵌入式系统、操作系统、WebAssembly、后端服务以及命令行工具的开发。

相较于 C 语言 “相信你知道自己在做什么”, 因此几乎不加限制地允许你操作内存和指针。
Rust 则恰恰相反, 它从语言设计层面 “不信任开发者”, 认为 “你总有一天会犯错”。

因此, Rust 引入了所有权系统、借用检查和生命周期机制。以求在编译阶段就将那些 “未来可能出问题的代码” 拒之门外。
这也意味着, 开发者在编写代码时, 往往需要花时间理解这些机制, 努力 “说服” 编译器接受自己的写法。
尽管这过程曲折, 但最终收获的是更加健壮和安全的程序。

本文将通过带领读者实现一个简单用于记录 Todo 事项的 CLI (Command Line Interface, 命令行接口) 程序来学习 Rust。

## 初始准备

首先通过 [Rust 官网](https://www.rust-lang.org/zh-CN/learn/get-started) 获取 Rust 安装包。

并跟随官方的文档来进行安装环境。

安装完毕之后, 使用 `cargo init` 可以初始化一个项目。

```shell
cargo init # 在当前目录下初始化
cargo init Project # 当前目录下新建一个 Project 目录
```

## 初始化项目

使用 `cargo init cli` 初始化一个名为 cli 的项目。

目录结构如下:

```sh
# cli 目录结构
- .git
- src
  - main.rs
- .gitignore
- Cargo.toml
```

其中的 `src` 目录存放的是项目源代码。 `Cargo.toml` 文件则用于保存项目依赖。

使用编辑器打开 `src/main.rs`。可以看见以下内容:

```rust
fn main() {
  println!("Hello, world!");
}
```

使用终端打开项目。使用 `cargo run` 运行项目。

可以看见 `Hello world!` 被输出。

需要注意的是，在 Rust 中，语句末尾要加上分号 `;`。

## 变量

在 Rust 中, 变量声明使用的是 `let` 关键字。

```rust
fn main() {
  let msg: &str = "Hello, world!";
  println!("{}", msg);
}
```

我们不需要每个变量都专门标注类型, 编译器会自动推断出变量的类型。
只有当编译器无法推断出变量类型时, 才需要手动标注类型。

因此以上代码可以更改为:

```rust
fn main() {
  let msg = "Hello, world!";
  println!("{}", msg);
}
```

我们的 CLI 用于记录 Todo 事项, 因此我们需要可以输入内容。

Rust 官方提供了标准库 `std::env` 用来获取环境信息。它提供了一个 `args` 函数, 允许获取命令行参数。

更改 `main.rs` 为如下内容:

```rust
fn main() {
  // 因为 args 函数返回的是一个迭代器, 我们需要将其收集为一个数据集合
  // 用户输入是未知的, 因此我们需要指定收集的输入类型, 即 String
  let args: Vec<String> = std::env::args().collect();

  println!("{:#?}", args);
}
```

命令行运行 `cargo run -- a b`, 结果如下:

```bash
[
  "target\\debug\\cli.exe",
  "a",
  "b",
]
```

可以看见, 我们获得的输入是一个数组格式, 它的第一项是我们的可执行文件路径。

我们需要的是输入的内容, 即 `a` 和 `b`

```rust
fn main() {
  let args: Vec<String> = std::env::args().collect();

  let title = args[1];
  let content = args[2];

  println!("todo title: {}, content: {}", title, content);
}
```

运行 `cargo run -- a b`。会发现有报错:

```bash
error[E0507]: cannot move out of index of `Vec<String>`
 --> src\main.rs:6:15
  |
6 |   let title = args[1];
  |               ^^^^^^^ move occurs because value has type `String`, which does not implement the `Copy` trait
  |
help: consider borrowing here
  |
6 |   let title = &args[1];
  |               +
help: consider cloning the value if the performance cost is acceptable
  |
6 |   let title = args[1].clone();
  |                      ++++++++

error[E0507]: cannot move out of index of `Vec<String>`
 --> src\main.rs:7:17
  |
7 |   let content = args[2];
  |                 ^^^^^^^ move occurs because value has type `String`, which does not implement the `Copy` trait
  |
help: consider borrowing here
  |
7 |   let content = &args[2];
  |                 +
help: consider cloning the value if the performance cost is acceptable
  |
7 |   let content = args[2].clone();
  |                        ++++++++
```

### 所有权

以上报错的关键如下:

```bash
cannot move out of index of `Vec<String>`

move occurs because value has type `String`, which does not implement the `Copy` trait
```

它的意思是: 无法从 `Vec<String>` 中取出值, 因为 `String` 类型没有实现 `Copy` 特征, 无法被隐式复制。

在前面有提及到:

> Rust 它从语言设计层面 “不信任开发者”, 认为 “你总有一天会犯错”。
>
> 因此, Rust 引入了所有权系统、借用检查和生命周期机制。以求在编译阶段就将那些 “未来可能出问题的代码” 拒之门外。

这里就是因为 Rust 引入的所有权系统导致的问题。

根据 Rust 所有权规则:

- 每个值都有一个所有者。
- 每个值同时只能有一个所有者。
- 当所有者离开作用域时, 这个值将被丢弃。

以上报错就很好理解了。

我们试图从 `Vec<String>` 这个类型中取出值, 但是根据所有权原则, 每个值都只能有一个所有者。
因此 `Vec<String>` 拥有它内部所有 `String` 元素的所有权。

当我们使用 `args[1]` 这样的方式访问时, 实际上是尝试将该元素的所有权 “移动” 到另一个变量。这就违反了所有权规则,
因为 `args` 还可能在后续被使用, 如果移动了元素所有权, 那么会导致它内部状态不一致, 甚至出现悬垂指针、重复释放等问题。

### 引用和借用

Rust 在其语言设计层面上“不信任开发者”, 因此它采用了所有权系统来强制保障内存安全。
也因此编译器非常“智能”, 它不仅会告诉你哪里出错了, 还会提供修复建议。

比如, 下面的编译错误信息中就给出了两种可能的解决方式:

```bash
help: consider borrowing here
  |
6 |   let title = &args[1];
  |               +
help: consider cloning the value if the performance cost is acceptable
  |
6 |   let title = args[1].clone();
  |                      ++++++++
```

第一种方法是 `let title = &args[1];`, 它表示借用 `args[1]` 的值, 而不移动它的所有权。
这种方式高效, 不会复制数据, 但是变量的类型将变为 `&String`, 表示这个变量是一个 `String` 值的引用。
因此它将受到引用对象的限制。当 `args` 失效, 那么它的引用也将失效。

而第二种方法是 `let title = args[1].clone();`, 它表示克隆 `args[1]` 的值,
并将这个值移动到 `title` 变量中, 这样 `args` 失效时, 也不会影响 `title` 的使用。

因此, 我们选择使用第二种方式, 显式调用 `clone` 方法, 克隆一份 `args[1]` 的值。

> 创建一个引用的行为叫做借用。引用则是借用这个行为的结果。

我们再次运行 `cargo run -- a b`, 可以发现编译通过了。

### 可变变量

在当前实现中, 每次运行程序都需要输入两个参数（标题和内容）, 否则程序会因索引越界而报错。
为了提升程序的健壮性, 我们可以为缺失的参数设置默认值。

修改代码:

```rust
fn main() {
  let args: Vec<String> = std::env::args().collect();
  let len = args.len();
  let title = args[1].clone();
  let content = String::from("default content");

  if len > 2{
    content = args[2].clone();
  }

  println!("todo title: {}, content: {}", title, content);
}
```

以上代码中, 我们对输入参数做了检查, 一旦参数数量大于 2 个, 就会使用第三个参数作为内容。否则就会使用默认值。

执行 `cargo run -- a`, 发现又有报错了。

```bash
error[E0384]: cannot assign twice to immutable variable `content`
  --> src\main.rs:10:5
   |
7  |   let content = String::from("default content");
   |       ------- first assignment to `content`
...
10 |     content = args[2].clone();
   |     ^^^^^^^ cannot assign twice to immutable variable
   |
help: consider making this binding mutable
   |
7  |   let mut content = String::from("default content");
   |       +++
```

这是因为 Rust 出于安全性和可读性考虑, 默认所有变量都是不可变的。
这段报错的意思是: 不能对不可变变量 `content` 进行二次赋值, 除非将它声明为可变的。

编译器已经为我们提示了。在 `let` 后面增加 `mut` 关键字即可。

```rust
fn main() {
  let args: Vec<String> = std::env::args().collect();
  let len = args.len();
  let title = args[1].clone();
  let mut content = String::from("default content");

  if len > 2{
    content = args[2].clone();
  }

  println!("todo title: {}, content: {}", title, content);
}
```

再次执行 `cargo run -- a`, 成功运行。

### 变量类型

Rust 是一门强类型的语言, 这意味着变量在编译时必须要有明确的类型。

类型确定方式有两种, 分别是显式声明和隐式推断。

显式声明, 在变量名称后面使用 `:` 指定类型。
例如: `let args: Vec<String> = std::env::args().collect();`。将变量 `args` 的类型指定为 `Vec<String>`。

隐式推断, 编译器根据变量的值和上下文推断变量的类型。
而 Rust 有着强大的类型推断机制, 使得我们在大多数情况下, 不需要手动标注类型。
编译器会自动推断类型, 只有当编译器无法推断类型时才需要手动标注。

例如以下代码中, 我们并未显式声明 `len`, `title` 或 `content` 的类型, 但它们的类型仍然是确定的:

```rust
  let args: Vec<String> = std::env::args().collect();
  let len /* usize */ = args.len();
  let title /* String */ = args[1].clone();
  let mut content /* String */ = String::from("default content");
```

Rust 支持常见的基本类型:

- 整型: `i8`, `i16`, `i32`, `i64`, `i128`, `isize`
- 无符号整型: `u8`, `u16`, `u32`, `u64`, `u128`, `usize`
- 浮点数: `f32`, `f64`
- 布尔值: `bool`
- 字符: `char`

需要注意的是, Rust 中, `"xxx"` 是一个字符串字面量切片, 类型为 `&str`, 是在编译时就固定不可变的。
而 `String` 是一个字符串类型, 编译时动态分配, 可变长度。

我们在前面使用的 `args` 是 `Vec<String>`, 就是一个动态字符串的集合。

## 控制流

所谓控制流, 就是控制程序的流程。

在没有控制流的情况下, 程序会按顺序从上往下逐行执行。
而控制流语句可以让我们根据条件选择性地执行某段代码, 或者重复执行某段代码,
从而让程序拥有判断和循环的能力。

### if/else 分支

`if`/`else` 是 Rust 中最常用的控制流语句。

它用于判断某个条件是否成立。
它的判断条件必须返回布尔值, 而不是其他类型。

如果判断条件成立, 则执行 `if` 后面的代码块。
如果判断条件不成立, 则执行 `else` 后面的代码块。

```rust
  let mut content = String::from("default content");

  if len > 2{
    content = args[2].clone();
  }
```

当参数格式多于两个时, 取第三个参数替换变量 `content` 的值。
否则 `content` 不变。

需要注意的是, Rust 中的 `if` 是一个表达式。允许有返回值。因此以上代码可以改为:

```rust
  let content = if len > 2 {
    args[2].clone()
  } else {
    String::from("default content")
  };
```

以上代码意思是, 如果 `len > 2` 条件成立, 就使用 `args[2].clone()` 作为 `content` 的值。
否则, 就使用 `String::from("default content")` 作为 `content` 的值。

> Rust 是一种表达式导向的语言, 实际上大部分的结构都可以返回值。

### 循环

Rust 中, 循环方式如下:

- `loop` 循环会一直执行, 直到遇到 `break` 语句。
- `while` 循环会在条件成立的情况下执行。
- `for` 循环会遍历一个集合中的所有元素。

我们将使用 `while` 实现一个交互式的命令行输入, 逐步获取 Todo 的标题与内容, 并确认是否创建该条 Todo。

修改 `main.rs` 代码如下:

```rust
fn main() {
  let mut inputs: Vec<String> = Vec::new();
  let args: Vec<String> = std::env::args().collect();
  let mut ok = args[1].clone() == "create";

  while ok {
    let len = inputs.len();

    if len == 0 {
      println!("Please input todo title");

      let mut title = String::new();

      std::io::stdin()
        .read_line(&mut title)
        .expect("read line failed");

      if title.is_empty() {
        continue;
      }

      inputs.push(title.trim().to_string());

    } else if len == 1 {
      println!("Please input todo content");

      let mut content = String::new();

      std::io::stdin()
        .read_line(&mut content)
        .expect("read line failed");

      if content.is_empty() {
        continue;
      }

      inputs.push(content.trim().to_string());
    }

    else {
      println!("title:   [{}]", inputs[0].clone());
      println!("content: [{}]", inputs[1].clone());
      println!("Are you sure to create this todo? (y/n)");

      let mut sure = String::new();

      std::io::stdin()
        .read_line(&mut sure)
        .expect("read line failed");

      if sure.trim().to_lowercase() != "n" {
        ok = false;
      }else{
        inputs.clear();
      }
    }
  }

  let title = inputs[0].clone();
  let content = inputs[1].clone();

  println!("create todo title: {}, content: {}", title, content);
}
```

以上代码中, 我们使用了 `while` 循环来实现一个交互式, 用于创建 Todo 项的命令行程序。

我们使用了一个状态变量 `ok` 来控制循环, 当 `ok` 为 `false` 时, 循环会结束。
并在用户输入的内容为空时, 使用 `continue` 语句来跳过当前循环。

如果改成 `loop` 循环的话如下所示:

```rust
loop {
  // 其他地方保持不变

  if sure.trim().to_lowercase() != "n" {
    ok = false;
  }else{
    inputs.clear();
  }

  if !ok {
    break
  }
}
```

`while` 和 `loop` 都可以用来循环, 效果可以说是等价的。

两者区别在于:

- `while` 适合用于条件驱动的循环, 比如获取用户输入并确认。
- `loop` 则更适合结构复杂, 需要手动控制循环的情况。例如游戏开发。

现在, 执行 `cargo run -- create` 就可以进入交互式界面来创建 Todo 项了。

### for 循环

`for` 循环常用于遍历一个数据集合。

我们将为 CLI 程序增加一个 `list` 命令, 用于列出所有的 Todo 项。

修改 `main.rs` 如下:

```rust
fn main() {
  let mut todos: Vec<String> = Vec::new();
  todos.push(String::from("learn rust"));
  todos.push(String::from("work"));
  todos.push(String::from("play"));

  let args: Vec<String> = std::env::args().collect();
  let mut inputs: Vec<String> = Vec::new();

  if args[1].clone() == "list" {
    for todo in todos {
      println!("todo title: {}", todo);
    }
    return;
  }

  let mut ok = args[1].clone() == "create";

  // ...
}
```

相较于需要手动管理索引的 `while` 和 `loop`, `for` 可以更简洁安全的遍历数据集合。
是 Rust 中处理数据集合的首选方式。

## 切片和数组

在前面的代码中, 我们使用到了 `String` 类型和 `&str` 类型。
可既然有 `&str` 那为什么要使用 `String` 呢?

这是因为在 Rust 中, `String` 类型的字符串, 是一个动态长度的字符串, 可以在任意位置增加或减少字符。
而 `&str` 类型的字符串, 是一个静态长度的字符串, 它的长度在编译时就确定了, 不能改变。

`&str` 适用于只读借用, 而 `String` 适用于修改操作。

### 切片

切片允许引用集合中的部分连续元素, 而不是整个集合。`&str` 类型就是一个字符串切片。

切片的语法是 `&[start..end]`。其中 `start` 是切片的起始位置, `end` 是切片的结束位置。
需要注意的是, 切片的范围是左闭右开区间, 即包含 `start` 位置, 不包含 `end` 位置。

例如: `let s = "hello world";`, `s` 就是一个字符串切片, 它的类型是 `&str`。
`&s[0..5]` 表示获取字符串 `s` 的前 5 个字符, 即 `"hello"`。

边界是可以省略的, 从零开始可以写为: `&s[..5]`, 到结尾可以写为: `&s[6..]`。

> Rust 字符串是 UTF-8 编码, 切片时需要保证切在合法字符边界, 否则会导致程序崩溃。

切片是相当常用的功能, 避免了复制从而提供效率, 也可以提供灵活视图操作。

### 数组

Rust 中的数组也是编译时固定长度, 要求所有元素类型相同, 性能较高, 使用 `let var: [type; length] = [];` 定义。
例如: `let arr: [i32; 5] = [1, 2, 3, 4, 5];`, 声明了一个长度 5 的 `i32` 类型数组。

如果需要使用动态的数组, Rust 提供了 `Vec<T>` 动态数组, 它的长度可以在运行时改变。常用于不定量数据, 例如用户输入, 命令行参数等。
前面我们使用的 `Vec<String>` 就是这样的元素类型为 `String` 的动态数组。

## 模式匹配

目前, 我们的 CLI 程序包含两个命令:

- `create`: 创建 Todo 项。
- `list`: 查看 Todo 列表。

但随着功能逐渐扩展, 代码也逐渐变得臃肿、不易维护。

为了解决这个问题, Rust 提供了一种更为优雅强大的方式, 即模式匹配 `match`。

我们可以使用 `match` 匹配输入内容, 根据不同的匹配进行相应的逻辑。

```rust
fn main() {
  let mut todos: Vec<String> = Vec::new();
  todos.push(String::from("learn rust"));
  todos.push(String::from("work"));
  todos.push(String::from("play"));

  let args: Vec<String> = std::env::args().collect();

  match args[1].clone().as_str() {
    "create" => {
      let mut inputs: Vec<String> = Vec::new();
      let mut ok = true;

      // ...

      println!("create todo title: {}, content: {}", title, content);
    }
    "list" => {
      for todo in todos {
        println!("todo title: {}", todo);
      }
    }
    _ => {
      println!("unknown command");
    }
  }
}
```

通过以上代码, 我们不难发现, `match` 很像其他语言中的 `switch`,
但是 Rust 的 `match` 则相对于 `switch` 更加强大。它可以:

- 匹配多种可能的值。
- 支持变量绑定和解构。
- 必须覆盖所有情况, 但允许使用 `_` 匹配所有。
- 它同时是表达式, 可以返回值。
- 支持守卫条件, 可以使用 `if` 增加条件限制。

下面是一个简单的示例:

```rust
let auth_level: i32 = 2;

let role = match auth_level {   // 返回值给变量声明
  0 => "Guest",                 // 单值匹配
  1 | 2 => "User",              // 多值匹配
  n if n >= 16 => "Admin",      // 守卫语句
  _ => "Unknow"                 // 默认分支, 匹配所有剩余情况
}
```

## 结构体

目前, 我们的 Todo 项分别有 Title 和 Content 两个属性。

为了更好的表达两者之间的关系, 我们可以使用 Rust 中的结构体将它们组织在一起。

结构体是一种可以由我们自定义的数据类型。能够将多种字段打包在一起形成一个整体, 便于管理, 传递和扩展。

改造 `main.rs`。

```rust
struct TodoItem {
  title: String,
  content: String,
}

fn main() {
  let mut todos: Vec<TodoItem> = Vec::new();
  todos.push(TodoItem {
    title: "learn rust".to_string(),
    content: "read rust book".to_string(),
  });
  todos.push(TodoItem {
    title: "work".to_string(),
    content: "complete required".to_string(),
  });
  todos.push(TodoItem {
    title: "play".to_string(),
    content: "play game".to_string(),
  });

  // ...
  "list" => {
    for todo in todos {
      println!("todo title: {}, content: {}", todo.title, todo.content);
    }
  }
  // ...
}
```

以上代码中, 我们定义了一个名为 `TodoItem` 的结构体, 它包含了 `title` 和 `content` 两个属性, 分别代表 Todo 项的标题和内容。

在 `main` 函数中, 我们用一个 `Vec<TodoItem>` 来保存多个 Todo 项, 每个 Todo 项都是一个结构体实例。

当匹配到 `"list"` 命令时, 我们遍历 `todos` 列表, 打印每个 Todo 的标题和内容, 实现了简单的查看功能。

## 函数

在先前的代码中, 我们定义了 `todos` 变量来存储 Todo 项, 并逐个实例化 Todo 项然后添加到 `todos` 中。

我们实例化 Todo 项的代码如下, 可以看到, 有些繁琐:

```rust
TodoItem {
  title: "learn rust".to_string(),
  content: "read rust book".to_string(),
}
```

为了避免每次都写重复的转换和构造过程, 我们可以使用 Rust 的函数。

函数是一段可以被重复调用的代码块。用于完成特定的任务。可以:

- 将某段功能独立出, 从而进行复用, 避免代码重复。
- 通过函数名描述功能, 让代码结构清晰, 提升可读性。
- 需要修改则只需要修改函数内部, 并不会影响外部调用, 增加了维护性和扩展性。
- 通过传递不同参数, 来改变函数内部走向, 实现不同的功能。
- 可以返回值, 实现外部与内部交互。

```rust
fn create_todo_item(title: &str, content: &str) -> TodoItem {
  return TodoItem {
    title: title.to_string(),
    content: content.to_string(),
  };
}

fn main() {
  let mut todos: Vec<TodoItem> = Vec::new();
  todos.push(create_todo_item("learn rust", "read rust book"));
  todos.push(create_todo_item("work", "complete required"));
  todos.push(create_todo_item("play", "play game"));

  // ...
}
```

在以上示例中, `create_todo_item` 接受两个 `&str` 类型的参数。返回 `TodoItem` 类型。
在它内部, 实现了将两个 `&str` 参数转换为 `String` 类型的值, 并绑定到 `TodoItem` 类型的实例上。

随后, 我们只需要使用 `create_todo_item("title", "content");` 就可以实例化一个 `TodoItem` 类型了。

相较于先前需要手动指定结构体类型、列出所有字段并逐一进行字符串转换的写法, 使用函数可以大大减少重复代码, 提升开发效率。

通过封装 `create_todo_item` 函数, 我们只需要传入标题和内容两个参数, 就能快速创建一个 `TodoItem` 实例, 既简洁, 又易于阅读和维护。

这样的封装方式在实际开发中非常常见, 也体现了函数抽象的核心思想: 隐藏实现细节, 对外暴露清晰的接口。

### 函数返回值

在 `create_todo_item` 中, 我们使用了 `return` 关键字返回了一个 `TodoItem` 类型的实例。

但是实际上, 我们其实可以不使用 `return` 关键字, 将函数改为:

```rust
fn create_todo_item(title: &str, content: &str) -> TodoItem {
  TodoItem {
    title: title.to_string(),
    content: content.to_string(),
  }
}
```

将行尾的 `;` 分号去掉, 就可以返回数据了。这是因为 Rust 默认将函数体中最后一个表达式的值作为返回值。
我们将行尾的 `;` 分号去掉了, 就将语句改为了表达式, 于是 Rust 可以将这个表达式的值作为返回值。

如果需要提前返回，才需要使用 `return` 关键字。

### 元组

元组是多种类型组合在一起形成的复合类型。长度和顺序都是固定的。
我们可以简单的将元组视为一个不能改变类型顺序的数组。

```rust
let tup: (i32, f64, &str) = (1, 1.0, "1");
```

元组允许使用 `.` 访问内容。

```rust
let a = tup.0
let b = tup.1
let c = tup.2
```

常用于包装多个值并供给其他地方使用。

### 单元类型

Rust 的单元类型只有一个值, 即 `()`。
它实际上是一个特殊元组, 但需要注意的是, Rust 中元组一定不能为空, 为空就不是元组了。

通常, 单元类型被用来表示无返回值。

没有返回值的函数实际上相当于默认返回了一个空元组 `()`。

## 模块化

随着程序逐渐复杂, 我们的 `main.rs` 文件中的代码越来越多, 所有的逻辑都堆在一起, 不仅可读性差, 也不利于维护和扩展。

在 Rust 中, 模块化是一种常见的代码组织方式。通过将代码拆分成多个文件, 让每个文件负责不同的功能。
可以让代码结构更加清晰, 职责划分明确。

目前, 我们的项目结构如下:

```bash
|- src/
  |- main.rs
```

新建一些文件, 项目结构如下:

```bash
|- src/
  |- todo/        # todo 模块目录
    |- core.rs    # todo 核心逻辑
    |- create.rs  # create todo 命令
    |- list.rs    # list todo 命令
  |- main.rs      # 程序入口
  |- todo.rs      # 子模块声明
```

### 访问修饰符

```rust
// src/todo/core.rs
pub struct TodoItem {
  pub title: String,
  pub content: String,
}

pub fn create_todo_item(title: &str, content: &str) -> TodoItem {
  TodoItem {
    title: title.to_string(),
    content: content.to_string(),
  }
}

pub fn get_todo_list() -> Vec<TodoItem> {
  let mut todos: Vec<TodoItem> = Vec::new();

  todos.push(create_todo_item("learn rust", "read rust book"));
  todos.push(create_todo_item("work", "complete required"));
  todos.push(create_todo_item("play", "play game"));

  return todos;
}
```

在以上代码中, 我们可以看见, 不论是结构体还是函数, 在声明前面都有着一个 `pub` 关键字。`pub` 表示该结构体或函数是公开的, 其他模块可以访问。

Rust 中, 默认所有内容都是私有的, 如果不添加 `pub`, 则该内容只能在当前模块中访问。

```rust
// src/todo/create.rs
pub fn create_todo() {
    let mut inputs: Vec<String> = Vec::new();
    let mut ok = true;

    while ok {
        let len = inputs.len();

        if len == 0 {
            println!("Please input todo title");

            let mut title = String::new();

            std::io::stdin()
                .read_line(&mut title)
                .expect("read line failed");

            if title.is_empty() {
                continue;
            }

            inputs.push(title.trim().to_string());
        } else if len == 1 {
            println!("Please input todo content");

            let mut content = String::new();

            std::io::stdin()
                .read_line(&mut content)
                .expect("read line failed");

            if content.is_empty() {
                continue;
            }

            inputs.push(content.trim().to_string());
        } else {
            println!("title:   [{}]", inputs[0].clone());
            println!("content: [{}]", inputs[1].clone());
            println!("Are you sure to create this todo? (y/n)");

            let mut sure = String::new();
            std::io::stdin()
                .read_line(&mut sure)
                .expect("read line failed");

            if sure.trim().to_lowercase() != "n" {
                ok = false;
            } else {
                inputs.clear();
            }
        }
    }

    let inputs_len = inputs.len();

    let title = if inputs_len > 0 {
        inputs[0].clone()
    } else {
        String::from("default title")
    };
    let content = if inputs_len > 1 {
        inputs[1].clone()
    } else {
        String::from("default content")
    };

    println!("create todo title: {}, content: {}", title, content);
}
```

### 模块路径解析

```rust
// src/todo/list.rs
use super::core::TodoItem;

pub fn list_todo(todos: &Vec<TodoItem>) {
  for todo in todos {
    println!("todo title: {}, content: {}", todo.title, todo.content);
  }
}
```

在以上代码中, 可以看见 `use super::core::TodoItem;` 这行语句。
这是在引用其他模块的内容。

Rust 使用文件夹路径的方式来引用不同的模块内容, 并提供了三种路径前缀:

- `super`, 表示当前模块的父模块。
- `self`, 表示当前模块自身。
- `crate`, 表示当前根模块, 即 `src` 目录, 如果是第三方库，则替换为库名称。

回到 `use super::core::TodoItem;`, 我们可以得知它的作用是引用 `list` 模块的父模块下的子模块 `core` 的 `TodoItem` 并使用它。
换句话说, 它的作用是从兄弟模块 `core` 引入 `TodoItem` 并使用。

> 引用的内容必须使用 `pub` 关键字公开, 否则无法引用。

### 模块声明

```rust
// src/todo.rs
pub mod core;
pub mod create;
pub mod list;
```

我们可以使用 `mod` 关键字来声明子模块。同样的, 子模块需要 `pub` 关键字修饰来公开给外部访问。

在 Rust 中, 每个模块都有一个 `mod.rs` 文件, 该文件是模块的入口文件。
在 `mod.rs` 文件中, 我们可以定义模块的公开内容, 如结构体、函数、模块等。

如果使用的 `rustc` 版本在 1.30 以前, 那么这是唯一声明模块入口的方法。

但如果是在 1.30 以后, 那么可以在模块同级位置创建一个同名的 `.rs` 文件来作为模块入口声明。

这里使用的就是使用与模块同名的 `.rs` 文件作为模块入口声明。

需要注意的是, 模块是可以直接声明的, 而无需单独文件。

```rust
pub mod list {
  use super::core::TodoItem;

  pub fn list_todo(todos: &Vec<TodoItem>) {
    for todo in todos {
      println!("todo title: {}, content: {}", todo.title, todo.content);
    }
  }
}
```

```rust
// src/main.rs
mod todo;

fn main() {
  let args: Vec<String> = std::env::args().collect();
  let todos = todo::core::get_todo_list();

  match args[1].clone().as_str() {
    "create" => todo::create::create_todo(),
    "list" => todo::list::list_todo(&todos),
    _ => {
        println!("unknown command");
    }
  }
}
```

## 数据持久化

目前, 我们的任务数据是保存在内存中的。当程序退出时, 这些数据会随之消失。

为了让用户的数据在下次启动程序时依然可用, 我们需要将数据持久化, 也就是保存到磁盘上。

一个简单且常见的做法是: 将数据保存到一个文件中。程序启动时从文件中读取任务列表, 退出或修改数据时再将更新后的任务保存回文件。

要实现这一功能, 我们需要先让数据支持序列化与反序列化。

- 序列化是指将结构体等内存对象转换为可保存的格式。
- 反序列化则是将这些格式转换回结构体对象。

### 添加依赖

在实际开发中, 我们通常会将常用的一些功能给封装起来, 方便后续重复使用。

更进一步的就是将这些功能封装为一个库包给发布到网络中, 让其他人也可以使用。
如果项目中有用到某个库包, 那么说明项目依赖于这个库包。这个库包就是项目的依赖。

`cargo` 就是 Rust 的库包管理工具。我们可以通过它安装项目依赖库包。

为了让 `TodoItem` 能被正确地序列化/反序列化, 我们需要引入第三方库 `Serde` 以及 `serde_json`。

在项目根目录下执行命令:

```bash
cargo add serde --features derive     # 增加 serde 依赖, 并开启 derive 功能
cargo add serde_json                  # 增加 serde_json 依赖
```

> serde 是一个强大的序列化/反序列化库, 它支持多种格式, 包括 JSON、YAML 等。
>
> 而 serde_json 则是基于 JSON 格式的实现。

### 为结构体实现方法

在 Rust 中, 我们可以使用 `impl` 关键字为结构体定义方法, 将结构体和它的行为组织在一起。

我们来为 `TodoItem` 添加创建、序列化和反序列化的方法:

```rust
// src/todo/core.rs
use serde::{Deserialize, Serialize};
use serde_json;

#[derive(Deserialize, Serialize)]
pub struct TodoItem {
  pub title: String,
  pub content: String,
}

impl TodoItem {
  pub fn new(title: &str, content: &str) -> Self {
    create_todo_item(title, content)
  }

  pub fn serializer(&self) -> String {
    serde_json::to_string(self).unwrap()
  }

  pub fn deserializer(s: &str) -> Self {
    serde_json::from_str(s).unwrap()
  }
}
```

我们在结构体上添加了 `#[derive(Serialize, Deserialize)]` 派生宏,
这会自动为 `TodoItem` 实现 `Serde` 所需的转换逻辑。避免了手动实现的复杂性。

此外, 我们还添加了:

- `new` 方法: 用于创建一个新的 `TodoItem`, 现在可以直接用 `TodoItem::new(...)` 替代之前的 `create_todo_item(...)`。
- `serializer` 方法: 将当前实例转换为 JSON 字符串。
- `deserializer` 方法: 从 JSON 字符串还原为 `TodoItem` 实例。

通过这种方式, 我们就为 `TodoItem` 实现了基本的序列化与反序列化功能。接下来, 我们就可以在程序中使用文件来保存和读取任务数据了。

### self 和 Self

在上方代码中, 我们可以在结构体实例函数的参数处看见 `self` 关键字。
它表示当前实例。相当于其他语言中的 `this`, `self`。

我们可以通过 `self.title`, `self.content` 这样的方式来访问当前实例属性。

除此之外, 它与其他参数并没有什么区别。

而 `Self` 则表示当前类型。等价于直接使用类型名称。
但可以在类型重命名等情况下保持代码不变, 使得代码更具有稳定性和可读性。

### 文件操作

现在, 我们已经实现了 `TodoItem` 的序列化和反序列化。接下来, 我们需要将数据存储到文件中, 实现持久化。

Rust 提供了标准库 `std::fs` 用于文件读写。我们将使用它实现以下两个功能:

- 保存 Todo 列表到文件。
- 读取 Todo 列表到程序。

增加 `src/todo/storage.rs` 文件, 并在 `src/todo.rs` 中声明并公开该模块。

```rust
// src/todo/storage.rs
use super::core::TodoItem;
use std::fs;

pub fn read_todo_list(save_file: &str) -> Vec<TodoItem> {
  let mut result: Vec<TodoItem> = Vec::new();

  match fs::read_to_string(save_file) {
    Ok(content) => match serde_json::from_str(content.as_str()) {
      Ok(mut list) => result.append(&mut list),
      _ => {
        println!("parse file error");
      }
    },
    _ => {
      println!("read file error");
    }
  }

  // 如果没有读取到任何数据, 提供默认示例
  if result.len() == 0 {
    result.push(TodoItem::new("learn rust", "read rust book"));
    result.push(TodoItem::new("work", "complete required"));
    result.push(TodoItem::new("play", "play game"));
  }

  return result;
}

pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) {
  let data = serde_json::to_string(todos).unwrap();
  fs::write(save_file, data).unwrap();
}
```

修改 `create_todo`,为 `todos` 根据用户输入添加 `TodoItem`:

```rust
// src/todo/create.rs
use crate::todo::core::TodoItem;
pub fn create_todo(todos: Vec<TodoItem>) {
  // ...
  while ok {
    //...
  }
  // ...
  println!("create todo title: {}, content: {}", title, content);
  todos.push(TodoItem::new(title.as_str(), content.as_str()));
}
```

```rust
// src/main.rs
use crate::todo::storage::{read_todo_list, save_todo_list};

mod todo;

fn main() {
  let args: Vec<String> = std::env::args().collect();
  let save_file = "todo.json";
  let mut todos = read_todo_list(save_file);

  match args[1].clone().as_str() {
    "create" => todo::create::create_todo(&mut todos),
    "list" => todo::list::list_todo(&todos),
    _ => {
      println!("unknown command");
    }
  }

  save_todo_list(save_file, &todos);
}
```

这样, 当我们执行以下命令时:

```bash
cargo run -- list    # 显示 Todo 列表（包括初始默认内容）
cargo run -- create  # 添加 Todo 项（修改会被保存）
```

数据将自动从 `todo.json` 读取并写入, 实现完整的本地持久化。

## 枚举

目前, 我们的程序通过匹配 `args[1]` 实现 `create` 与 `list` 两个命令:

```rust
match args[1].as_str() {
  "create" => { ... }
  "list" => { ... }
  _ => println!("unknown command"),
}
```

虽然简单直观, 但这种基于字符串的匹配存在如下问题:

- 命令数量增加后, `match` 分支会变得冗长。
- 容易因拼写错误而出错, 缺乏类型保障。
- 命令的参数结构难以统一组织和扩展。
- 无法自动生成 --help 等提示信息。

为解决此问题, 我们将结合 Rust 的枚举和引入第三方库 `clap` 来构建维护性和扩展性更强的 CLI 程序。

> clap 是一个强大的 Rust 库, 用于解析命令行参数。它支持自动生成命令行参数的帮助信息, 并支持丰富的参数类型和校验规则。

在项目根目录执行命令:

```bash
cargo add clap --features derive # 增加依赖并启用 derive 功能
```

### 为什么使用枚举

枚举, 在各种编程语言中或多或少都有着它的身影。

它的作用是用于表示一组有限的、互斥的可能取值, 例如周一到周日, 性别等。

与其他语言的枚举相比, Rust 的枚举更加灵活和强大:

- 支持每个变体携带不同的数据。
- 可与模式匹配强结合, 做复杂的控制流。
- 可以和 `trait`、方法一起使用, 实现丰富的抽象设计。

这使得枚举天然适合表示 CLI 的命令结构: 每个命令对应一个枚举变体, 每个变体携带所需参数。

### 声明枚举

Rust 中的枚举使用 `enum` 关键字声明。

```rust
// src/todo/core.rs
use clap::Subcommand;

#[derive(Debug, Clone, Subcommand)]
pub enum TodoCommand {
  /// Create a new todo item
  Create,
  /// List all todo items
  List,
}
```

以上代码定义了一个名为 `TodoCommand` 的枚举, 它有两个枚举值, 分别是 `Create` 和 `List`。
我们使用了派生宏 `#[derive(Debug, Clone, Subcommand)]` 为枚举自动实现 `Debug`、`Clone` 和 `Subcommand` 三个特征。

`Subcommand` 特征告诉 `clap` 该枚举对应一个子命令。

### 解析命令行参数

```rust
//src/main.rs
use crate::todo::storage::{read_todo_list, save_todo_list};
use clap::Parser;
use todo::core::TodoCommand;

mod todo;

#[derive(Debug, Parser)]
#[command(version, about, long_about = "Todo Cli")]
struct Program {
  #[command(subcommand)]
  pub command: TodoCommand,
}

fn main() {
  let args = Program::parse();
  let save_file = "todo.json";
  let mut todos = read_todo_list(save_file);

  match args.command {
    TodoCommand::Create => todo::create::create_todo(&mut todos),
    TodoCommand::List => todo::list::list_todo(&todos),
  }

  save_todo_list(save_file, &todos);
}
```

以上代码中, 我们定义了一个 `Program` 结构体, 它有一个字段 `command` 用于接收子命令。

`#[command(version, about, long_about = "Todo Cli")]` 告诉 `clap` 自动生成 --version 和 --help 两个参数。

`#[command(subcommand)]` 告诉 `clap` 该字段对应一个子命令。

运行 `cargo run -- --help` 可以看到自动生成的帮助信息:

```bash
Todo Cli

Usage: cli.exe <COMMAND>

Commands:
  create  Create a new todo item
  list    List all todo items
  help    Print this message or the help of the given subcommand(s)

Options:
  -h, --help
          Print help (see a summary with '-h')

  -V, --version
          Print version
```

### Rust 注释

在上面的例子中, 我们给 TodoCommand 的每个枚举项添加了文档注释。
但是当我们运行 `--help` 时, 注释内容却自动出现在帮助信息中。

这可能让人疑惑: 我们只是加了一些注释, 为什么这些注释会出现在运行时输出的帮助信息里？

这是因为在 Rust 中的注释有三种形式。

```rust
// 单行注释（不会被编译器解析）
// 在 // 的所有内容都会被注释

/*
多行注释
只有在 /* */ 范围内的内容才会被注释
（也不会被编译器解析）
*/

/// 文档注释（会被编译器和工具识别）

/**
 * 这也是文档注释
 * 以 /** 开头
*/
```

我们用到的就是 `/// xxx` 即文档注释。它是编译器可识别的元信息。
文档注释的内容会被编译器和第三方工具解析为注释对象的文档说明。

`clap` 通过它的派生宏 `#[derive(Subcommand)]` 来在编译期间获取结构体和枚举的元信息, 其中就有文档注释。
因此, 文档注释的内容会出现在运行时输出的帮助信息里。

### 枚举变体

Rust 的枚举是支持携带数据的。

改造 `TodoCommand`。

```rust
#[derive(Debug, Clone, Subcommand)]
pub enum TodoCommand {
  Create {
    #[arg(short, long)]
    title: String,
    #[arg(short, long)]
    content: String,
  },
  List,
}
```

我们在 `Create` 枚举值中增加了两个字段 `title` 和 `content`。

分别对应 `--title` 和 `--content` 参数。

`#[arg(short, long)]` 告诉 `clap` 该字段对应一个参数, 并指定参数的短名称和长名称。

执行 `cargo run -- create --help`, 可以看到自动生成的帮助信息:

```bash
Create a new todo item

Usage: cli.exe create --title <TITLE> --content <CONTENT>

Options:
  -t, --title <TITLE>
  -c, --content <CONTENT>
  -h, --help               Print help
```

修改 `create_todo` 方法。

```rust
pub fn create_todo(todos: &mut Vec<TodoItem>, title: String, content: String) {
  let mut inputs: Vec<String> = Vec::new();

  if !title.is_empty() {
    inputs.push(title);
  }

  if !content.is_empty() {
    inputs.push(content);
  }

  let mut ok = inputs.len() == 0;
  // ...
}
```

模式匹配是相当强大的, 可以将枚举值的字段解构出,
修改 `main.rs`:

```rust
// ...
  match args.command {
    TodoCommand::Create { title, content } => todo::create::create_todo(&mut todos, title, content),
    TodoCommand::List => todo::list::list_todo(&todos),
  }
// ...
```

随后, 我们就可以使用 `cargo run -- create --title t --content c` 来创建 Todo 而不需要进入交互式界面了。

### 可选参数

目前, 我们的 `create` 命令的参数都是必填的。
但是这样我们没法区分到底是使用命令行参数还是交互式界面来创建 Todo 项。

因此我们需要使用可选参数。

Rust 提供了一个 `Option<T>` 类型的枚举。

```rust
pub enum Option<T> {
  None,
  Some(T),
}
```

可以看见, 枚举 `Option<T>` 就有两个枚举值。分别是 `Some(T)` 和 `None`, 分别代表有值和无值。

将 `TodoCommand` 枚举改为如下内容:

```rust
#[derive(Debug, Clone, Subcommand)]
pub enum TodoCommand {
  /// Create a new todo item
  Create {
    #[arg(short, long)]
    title: Option<String>,
    #[arg(short, long)]
    content: Option<String>,
  },
  /// List all todo items
  List,
}
```

随后修改 `create_todo` 方法。

```rust
pub fn create_todo(todos: &mut Vec<TodoItem>, title: Option<String>, content: Option<String>) {
  let mut inputs: Vec<String> = Vec::new();

  match title {
    Some(arg_title) => {
      if !arg_title.is_empty() {
        inputs.push(arg_title);
      }
    }
    _ => {}
  }

  match content {
    Some(arg_content) => {
      if !arg_content.is_empty() {
        inputs.push(arg_content);
      }
    }
    _ => {}
  }
  // ...
```

改造完毕后, 我们的 `create` 命令可以不指定参数进入交互式界面创建 Todo, 也可以指定参数直接创建 Todo 了。

### 泛型

在前面的例子中, 我们使用了 `Option<String>` 来表示将参数变得可选。
那么, `Option<T>` 中的 `T` 是从哪里来的？为什么我们只需要将 `T` 替换为 `String`, 就能让参数变得可选？

因为这里的 `T` 是一个泛型。它并不是某个具体的值, 而是作为一个占位符被用来指代一个将来会具体指定的类型。

Rust 是一门静态类型语言, 拥有强大而灵活的类型系统。
为了保证类型安全, Rust 要求在编译期间就确定所有变量和参数的类型。
这虽然增强了代码的可靠性, 但也带来了一个问题: 我们往往需要为不同的类型编写大量结构相似但类型不同的代码。

例如翻转一个元组, 如果不使用泛型, 将是这样的。

```rust
fn reverse_i8_tuple(tuple: (i8, i8)) -> (i8, i8) {
  let (a, b) = tuple;
  return (b, a);
}

fn reverse_u8_tuple(tuple: (u8, u8)) -> (u8, u8) {
  let (a, b) = tuple;
  return (b, a);
}
```

为了解决类型重复的问题, 许多静态类型语言都引入了泛型这一机制, Rust 也不例外。
泛型允许我们编写与具体类型无关的通用代码, 从而在保持类型安全的同时避免重复劳动。

当我们将 `String` 传入 `Option<T>`,  `Option<T>` 就变成了 `Option<String>`。`T` 从一个广泛的类型收缩为一个明确的 `String` 类型。

我们需要为每个类型单独实现一个方法。

但如果使用泛型, 在需要泛型的内容后面追加一个 `<T>` 即可:

```rust
fn reverse<T>(args: (T, T)) -> (T, T) {
  let (a, b) = args;
  return (b, a);
}
```

于是, 我们就可以使用 `reverse` 方法来翻转任意类型的元组了。

```rust
let a = reverse((1, 2));
let b = reverse(("a", "b"));
```

需要注意的是, `T` 并不是固定的名称, 只是约定成俗将泛型参数命名为 `T`。
只要开发者愿意, 那么将泛型可以是任何符合变量命名规则的名称。

下面的示例展示了如何使用多个自定义命名的泛型参数:

```rust
fn reverse<Rust_1, Rust_2>(args: (Rust_1, Rust_2)) -> (Rust_2, Rust_1) {
  let (a, b) = args;
  return (b, a);
}
```

### if let

在前面的代码中, 我们对可选参数进行了模式匹配。

```rust
match title {
  Some(arg_title) => {
    if !arg_title.is_empty() {
      inputs.push(arg_title);
    }
  }
  _ => {}
}
```

虽然功能正确, 但代码稍显冗长, 尤其当我们只关心某一个具体模式时。

Rust 提供了一个 `if let` 语法糖, 用来匹配并解构某个特定的枚举变体, 而忽略其他所有可能的枚举值。

于是我们可以将 `create_todo` 改为这样:

```rust
pub fn create_todo(todos: &mut Vec<TodoItem>, title: Option<String>, content: Option<String>) {
  let mut inputs: Vec<String> = Vec::new();

  if let Some(arg_title) = title {
    if !arg_title.is_empty() {
      inputs.push(arg_title);
    }
  }

  if let Some(arg_content) = content {
    if !arg_content.is_empty() {
      inputs.push(arg_content);
    }
  }
  // ...
```

这段代码的意思是如果 `title` 可以匹配出 `Some(arg_title)`, 则将 `arg_title` 解构出并判断是否为空。
而如果无法匹配, 则什么都不做。

可以看见, 相较于之前, 代码简化了不少。

## 错误处理

在进行数据持久化时, 我们编写了 `save_todo_list` 方法。

```rust
pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) {
  let data = serde_json::to_string(todos).unwrap();
  fs::write(save_file, data).unwrap();
}
```

虽然这样写能让程序正常运行, 但也埋下了隐患。
即, 一旦序列化失败或文件写入失败, 就会导致程序崩溃。

我们希望即使程序运行出错也可以正常处理, 而不是崩溃。
因此我们需要引入 Rust 的错误处理机制。

Rust 并没有 `try-catch` 机制。
而是通过枚举 `Result<T, E>` 来显式处理。
`T` 表示成功的返回值类型, `E` 表示错误类型。

```rust
enum Result<T, E> {
    Ok(T),      // 操作成功时, 返回结果 T
    Err(E),     // 操作失败时, 返回错误类型 E
}
```

### unwrap 和 expect

我们在 `save_todo_list` 方法中使用了 `unwrap`。它用于从 `Result<T, E>` 中获取值。

- 如果 `Result` 是 `Ok(T)`, 则返回 `T`;
- 如果 `Result` 是 `Err(E)`, 则程序会崩溃并打印错误信息。

我们也可以使用 `expect` 方法。它与 `unwrap` 类似, 但它会返回一个自定义的错误信息。

```rust
let data = serde_json::to_string(todos).expect("序列化失败");
```

但这两种方法都不推荐在正常程序中使用。因为一旦出错就会导致程序崩溃。

更加健壮的方法是使用一个 `match` 来处理 `Result<T, E>`。

```rust
pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) {
  match serde_json::to_string(todos) {
    Ok(data) => match fs::write(save_file, data) {
      Err(msg) => {
        println!("save file error: {}", msg);
      }
      Ok(_) => {
        println!("save file success");
      }
    },
    Err(msg) => {
      println!("save file error: {}", msg);
    }
  }
}
```

这样, 即使出错了, 程序也能继续运行, 并向用户提示错误原因。

### try 运算符

Rust 还提供了一个 `?` 运算符, 用于自动传播错误。它避免了我们层层 `match`。

```rust
pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) -> Result<(), String> {
  let data = serde_json::to_string(todos)?;
  fs::write(save_file, data)?;
  Ok(())
}
```

可当我们直接运行以上代码时, 编译器会报错。

```bash
error[E0277]: `?` couldn't convert the error to `std::string::String`
  --> src\todo\storage.rs:29:44
   |
28 | pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) -> Result<(), String> {
   |                                                                  ------------------ expected `std::string::String` because of this
29 |     let data = serde_json::to_string(todos)?;
   |                ----------------------------^ the trait `From<serde_json::Error>` is not implemented for `std::string::String`
   |                |
   |                this can't be annotated with `?` because it has type `Result<_, serde_json::Error>`
   |
   = note: the question mark operation (`?`) implicitly performs a conversion on the error value using the `From` trait
   = help: the following other types implement trait `From<T>`:
             `std::string::String` implements `From<&mut str>`
             `std::string::String` implements `From<&std::string::String>`
             `std::string::String` implements `From<&str>`
             `std::string::String` implements `From<Box<str>>`
             `std::string::String` implements `From<Cow<'_, str>>`
             `std::string::String` implements `From<Id>`
             `std::string::String` implements `From<char>`
             `std::string::String` implements `From<clap::builder::Str>`
   = note: required for `Result<(), std::string::String>` to implement `FromResidual<Result<Infallible, serde_json::Error>>`
```

这是因为只有当返回类型是 `Result` 且错误一致时, 才能够使用 `?`。

我们可以看到报错信息: ``` `?` couldn't convert the error to `std::string::String` ``` ,

错误原因是 `save_todo_list` 返回 `Result<(), String>`, 但 `serde_json::to_string(...)` 的错误类型是 `serde_json::Error`,
? 运算符尝试将 `serde_json::Error` 转换为 `String`, 但 `From<serde_json::Error> for String` 并未实现。

于是我们需要对错误进行转换, 使得返回的类型与 `save_todo_list` 函数一致。

### 函数闭包

我们可以使用闭包来解决这个问题。

闭包是一种匿名函数, 除了可以接受参数外, 还可以捕获其环境中的变量。
除此之外, 闭包还可以作为参数传递给函数。

语法如下:

```rust
{
  let x = 5;
  // 类型标注不是必须的
  let add_x = |y: i32| -> i32 {
    return x + y;
  }
  println!("{}", add_x(3));
}
```

如果只有一个返回表达式, 可以简化为 `let add_x = |y| x + y;`。

认识了闭包之后, 我们就可以改造 `save_todo_list` 了。
使用 `map_err` 函数, 传递一个闭包, 将可能发生的错误统一转换为 `String` 类型。

```rust
pub fn save_todo_list(save_file: &str, todos: &Vec<TodoItem>) -> Result<(), String> {
  let data = serde_json::to_string(todos).map_err(|e| e.to_string())?;
  fs::write(save_file, data).map_err(|e| e.to_string())?;
  Ok(())
}
```

重新运行, 这下就可以正常工作了。

## 查找 Todo

我们将 `create` 命令功能基本完善了, 它可以使用命令行参数和交互式界面两种方式来创建 Todo 项。

但是我们的 `list` 命令还相对简陋, 它只能列出所有的 Todo 项, 而无法根据条件筛选 Todo 项。
因此我们需要完善它。

### 筛选 Todo

我们将创建一个 `TodoItemFilter` 结构体。用来表示筛选配置。

```rust
pub struct TodoItemFilter {
  pub title: Option<String>,
  pub content: Option<String>,
}
```

`TodoItemFilter` 将具有两个属性, 分别代表需要筛选的 `title` 和 `content` 内容。
因为可能只需要筛选其中一个, 因此将两者均设为 `Option<String>` 属性表示可选的。

接下来我们将为它实现一些方法。

首先是实例化方法。

```rust
impl TodoItemFilter {
  pub fn new() -> Self {
    Self {
      title: Option::None,
      content: Option::None,
    }
  }
}
```

在一开始, 我们并没有办法知道需要筛选什么内容, 因此将 `title` 和 `content` 均设为 `None`。

### 泛型约束

在之前代码中, 我们了解到了用来占位表示任何类型的泛型。
但仅仅只是一个 `T` 的范围就太大了。例如我们可能需要的参数是一个字符串, 但却可以将数字, 布尔传递进来。

为解决这个问题, Rust 支持对泛型进行类型约束, 使得泛型参数必须满足特定的条件。
因此我们需要对泛型进行进一步的约束。

例如, 我们希望参数可以转换为字符串类型, 那么可以使用 `Into<String>` 作为约束条件。
`Into<String>` 表示“任何可以转换成 `String` 的类型”。

```rust
impl TodoItemFilter {
  // ...
  pub fn set_title<T: Into<String>>(&mut self, title: T) {
    self.title = Some(title.into());
  }

  pub fn set_content<T: Into<String>>(&mut self, content: T) {
    self.content = Some(content.into());
  }
}
```

上方代码分别为 `TodoItemFilter` 实现 `set_title` 和 `set_content` 方法。
我们不关心参数 `T` 具体是什么类型, 只要它满足约束条件 `Into<String>` 就行。
无论 `T` 是 `String` 类型, 还是 `&str` 类型, 抑或是 `Vec<u8>` 类型, 只要它可以被转换为 `String` 类型, 都可以作为参数传入。

类型约束有两种写法, 上面的是第一种, 直接将约束条件写在泛型参数位置, 更加常用。
第二种则是使用 `where` 子句单独列出, 适用于复杂约束情况。

```rust
impl TodoItemFilter {
  // ...
  pub fn set_title<T>(&mut self, title: T) where T: Into<String> {
    self.title = Some(title.into());
  }

  pub fn set_content<T>(&mut self, content: T) where T: Into<String> {
    self.content = Some(content.into());
  }
}
```

### 筛选参数

我们目前的 Todo 项具有两项属性, 即 `title` 和 `content`。
我们可以根据这两项属性中的任意一项或两项来筛选 Todo 项。

我们为 `TodoItemFilter` 实现一个 `filter` 方法用于过滤 Todo 项。

```rust
pub fn filter(&self, list: &Vec<TodoItem>) {
  let mut filtered_list = Vec::<&TodoItem>::new();

  if self.title.is_none() && self.content.is_none() {
    for item in list {
      filtered_list.push(item);
    }
  } else {
    for item in list {
      let mut flag: (bool, bool) = (false, false);

      flag.0 = match &self.title {
        Some(title) => item.title.contains(title),
        _ => true,
      };

      flag.1 = match &self.content {
        Some(content) => item.content.contains(content),
        _ => true,
      };

      if flag.0 && flag.1 {
        filtered_list.push(item);
      }
    }
  }

  for item in filtered_list {
    println!("todo title: {}, content: {}", item.title, item.content);
  }
}
```

以上代码为 `TodoItemFilter` 实现的 `filter` 方法。
它首先创建一个空的 `filtered_list` 用于存储筛选后的 Todo 项。
如果 `title` 和 `content` 均为空, 则直接将所有 Todo 项放入 `filtered_list`。
否则, 遍历所有 Todo 项, 根据 `title` 和 `content` 进行筛选。
如果 Todo 项的 `title` 和 `content` 均包含筛选条件, 则将其放入 `filtered_list`。

最后, 遍历 `filtered_list`, 打印出筛选后的 Todo 项。

然后我们改造 `TodoCommand` 枚举, 为 `list` 命令增加两个参数。

```rust
// ...
/// List all todo items
List {
  #[arg(short, long)]
  title: Option<String>,
  #[arg(short, long)]
  content: Option<String>,
}
// ...
```

改造 `main` 函数, 在 `list` 命令中添加筛选参数。

```rust
// ...
  match args.command {
    TodoCommand::Create { title, content } => {
      todo::create::create_todo(&mut todos, title, content)
    }
    TodoCommand::List { title, content } => todo::list::list_todo(&todos, title, content),
  }
// ...
```

接着改造 `list_todo` 函数。

```rust
pub fn list_todo(todos: &Vec<TodoItem>, title: Option<String>, content: Option<String>) {
  let mut filter = TodoItemFilter::new();

  if let Some(title) = title {
    filter.set_title(title);
  }

  if let Some(content) = content {
    filter.set_content(content);
  }

  filter.filter(todos);
}
```

现在, 当我们执行 `cargo run -- list` 命令时, 可以携带 `--title` 和 `--content` 参数进行筛选了。

## 特征

在为 `list` 命令实现 `set_title` 和 `set_content` 方法时, 我们使用了 `Into<String>` 进行类型约束。
但 `Into<T>` 并非是类型, 它是一个特征, 是 Rust 用于定义行为约定的一种机制。可以为类型定义统一的能力规范。

我们可以将 Rust 中的特征看作是其他语言中的接口。

Rust 内置了许多特征。例如 `Into<T>` 表示可以将类型转换为 `T`。`From<T>` 表示可以从 `T` 构造出某个类型。
`Copy` 和 `Clone` 可以表示一个类型是否可以被复制等等。

在最开始我们编写程序时就遇到过一个涉及特征的错误。
`String` 类型没有实现 `Copy` 特征, 因此无法直接将参数赋值。

```bash
6 |   let title = args[1];
  |               ^^^^^^^ move occurs because value has type `String`, which does not implement the `Copy` trait
```

### 声明特征

特征的声明使用 `trait` 关键字。

```rust
trait PrintName {
  fn PrintName(&self) -> String;
}
```

与枚举一样, 特征只要使用了 `pub` 修饰, 那么它的方法就全部可供外部访问。

### 实现特征

特征的实现依赖于类型。在原先的为类型实现方法的基础上增加实现的特征名称和 `for` 关键字。

```rust
trait PrintName {
  fn PrintName(&self) -> String;
}

impl PrintName for TodoItem {
  fn PrintName(&self) -> String {
    "TodoItem".to_string()
  }
}
```

倘若需要为类型 A 实现特征 B, 那么两者必须有一个是在当前作用域中定义的。否则将无效。
例如想为 `String` 实现 `Copy` 特征, 但两者都定义在标准库中而不在当前作用域, 因此无法实现。

这个规则被称为孤儿规则, 它确保了他人编写的代码不会破坏我们的代码, 我们也不会莫名其妙破坏他人的代码。

### 特征约束

前面我们使用到了特征约束, 即 `T: Into<String>`。它表示 `T` 必须实现 `Into<String>` 特征。

特征约束不仅可以约束泛型, 也可以约束特征自身。

```rust
trait PrintName: Display {
  fn PrintName(&self) -> String;
}
```

以上代码为 `PrintName` 特征的定义, 它要求实现对象必须实现 `Display` 特征才能实现它。
可以使用 `+` 号增加更多的约束。例如 `trait PrintName: Display + Clone` 表示 `PrintName` 必须实现 `Display` 和 `Clone` 特征才能实现它。

### 参数约束

特征也可以用来约束参数类型。

```rust
trait PrintName: Display {
  fn PrintName(&self) -> String;
}

fn printName(item: &impl PrintName) {
  println!("{}", item.PrintName());
}

// 以上等价于

fn printName<T: PrintName>(item: &T) {
  println!("{}", item.PrintName());
}
```

## 为 TodoItem 实现特征

在先前的开发中, 我们为 `TodoItem` 实现了序列化和反序列化方法。这两种方法在开发过程中相当常见。
我们如果要为每个方法都去实现一遍有点太繁琐了。

因此, 我们可以声明一个特征, 从而将这些通用行为给抽离出来。

首先定义 `Serializer` 特征表示序列化和反序列化方法集合。然后为 `TodoItem` 实现 `Serializer` 特征。

```rust
pub trait Serializer {
  fn serialize(&self) -> String;
  fn deserialize<S: Into<String>>(s: S) -> Self;
}

impl Serializer for TodoItem {
  fn deserialize<S: Into<String>>(s: S) -> Self {
    serde_json::from_str(&s.into()).unwrap()
  }

  fn serialize(&self) -> String {
    serde_json::to_string(self).unwrap()
  }
}
```

### 默认实现特征

以上代码中, 尽管我们已经将序列化和反序列化方法抽离。但仍然需要手动实现方法体。这依然较为繁琐。

因此我们可以使用默认实现来取消手动实现方法体。

```rust
pub trait Serializer {
  fn serialize(&self) -> String {
    serde_json::to_string(self).unwrap()
  }

  fn deserialize<S: Into<String>>(s: S) -> Self {
    serde_json::from_str(&s.into()).unwrap()
  }
}

impl Serializer for TodoItem {}
```

将代码改成以上内容, 然后运行。会发现有报错。我们先解决 `serialize` 方法的报错。

```bash
error[E0277]: the trait bound `Self: Serialize` is not satisfied
    --> src\todo\core.rs:68:31
     |
68   |         serde_json::to_string(self).unwrap()
     |         --------------------- ^^^^ the trait `Serialize` is not implemented for `Self`
     |         |
     |         required by a bound introduced by this call
     |
     = note: for local types consider adding `#[derive(serde::Serialize)]` to your `Self` type
     = note: for types from other crates check whether the crate offers a `serde` feature flag
note: required by a bound in `serde_json::to_string`
    --> C:\Users\Administrator\.cargo\registry\src\rsproxy.cn-e3de039b2554c837\serde_json-1.0.128\src\ser.rs:2209:17
     |
2207 | pub fn to_string<T>(value: &T) -> Result<String>
     |        --------- required by a bound in this function
2208 | where
2209 |     T: ?Sized + Serialize,
     |                 ^^^^^^^^^ required by this bound in `to_string`
help: consider further restricting `Self`
     |
67   |     fn serialize(&self) -> String where Self: Serialize {
     |                                   +++++++++++++++++++++
```

报错内容是 ```the trait bound `Self: Serialize` is not satisfied```。
这是因为 `Self` 类型没有满足 `serde_json::to_string(self)` 要求的类型约束导致的。

我们可以查看 `serde_json::to_string` 方法的定义。

```rust
serde_json::ser
pub fn to_string<T>(value: &T) -> Result<String>
where
  T: ?Sized + Serialize,
// ...
```

可以看见, 它使用了 `where` 子句, 要求 `T` 类型必须实现 `?Sized` 和 `Serialize` 特征。

我们将类型约束补上。

```rust
pub trait Serializer
where
  Self: Sized + Serialize,
{
  fn serialize(&self) -> String {
    serde_json::to_string(self).unwrap()
  }

  fn deserialize<S: Into<String>>(s: S) -> Self {
    serde_json::from_str(&s.into()).unwrap()
  }
}

impl Serializer for TodoItem {}
```

再次运行, `serialize` 方法不再报错, 现在只剩下 `deserialize` 方法的报错了。

`deserialize` 方法的报错如下:

```bash
error[E0277]: the trait bound `Self: Deserialize<'_>` is not satisfied
    --> src\todo\core.rs:75:9
     |
75   |         serde_json::from_str(&s.into()).unwrap()
     |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ the trait `Deserialize<'_>` is not implemented for `Self`
     |
     = note: for local types consider adding `#[derive(serde::Deserialize)]` to your `Self` type
     = note: for types from other crates check whether the crate offers a `serde` feature flag
note: required by a bound in `serde_json::from_str`
    --> C:\Users\Administrator\.cargo\registry\src\rsproxy.cn-e3de039b2554c837\serde_json-1.0.128\src\de.rs:2680:8
     |
2678 | pub fn from_str<'a, T>(s: &'a str) -> Result<T>
     |        -------- required by a bound in this function
2679 | where
2680 |     T: de::Deserialize<'a>,
     |        ^^^^^^^^^^^^^^^^^^^ required by this bound in `from_str`
help: consider further restricting `Self`
     |
74   |     fn deserialize<S: Into<String>>(s: S) -> Self where Self: Deserialize<'_> {
     |                                                   +++++++++++++++++++++++++++
```

报错信息: ```the trait bound `Self: Deserialize<'_>` is not satisfied``` 可以看见, 也是因为没有满足类型约束导致的。

编译器也有提示我们增加约束。

补上约束, 代码如下:

```rust
pub trait Serializer
where
  Self: Sized + Serialize + Deserialize<'_>,
{
  fn serialize(&self) -> String {
    serde_json::to_string(self).unwrap()
  }

  fn deserialize<S: Into<String>>(s: S) -> Self {
    serde_json::from_str(&s.into()).unwrap()
  }
}
```

重新运行, `deserialize` 的报错消失了。但出现了新的报错:

```bash
error[E0637]: `'_` cannot be used here
  --> src\todo\core.rs:68:43
   |
68 |     Self: Sized + Serialize + Deserialize<'_>,
   |                                           ^^ `'_` is a reserved lifetime name

For more information about this error, try `rustc --explain E0637`.
```

报错信息: ``` `'_` cannot be used here```, 表示这里不能使用 `'_`,
``` `'_` is a reserved lifetime name``` 提示我们 `'_` 是保留的生命周期名称。

### 生命周期

生命周期, 通常指某个事物从开始到结束的一个完整的过程。

在 Rust 中, 它是一个编译期概念, 用于检查引用是否合法, 避免悬垂指针等问题。
通常情况下, 我们不需要手动标注生命周期, 编译器会自动推导。
只有当编译器无法确定时, 才需要手动标注。

可以将 Rust 中的生命周期简单的认为就是引用的有效作用域。

```rust
{
  let r;
  {
    let n = 0;
    r = &n;
  }
  println!("r: {}", r);
}
```

以上代码通过花括号被分为两层, 在第一层, 声明了变量 `r` 但未赋值。
在第二层, 声明了变量 `n`, 并将 `n` 的地址赋值给 `r`。

`n` 是一个局部变量, 它的生命周期在第二层结束, 即花括号结束。
而 `r` 是一个引用, 它指向 `n`, 它的生命周期在 `r` 所在的作用域内, 即第一层的花括号内。

`n` 的生命周期比 `r` 的生命周期短, 这没有问题。但是 `r` 被赋值为 `n` 的引用, 就会导致出问题。
因为 `n` 会在 `n` 的生命周期结束后被销毁, 而 `r` 指向了一个已经被销毁的变量。

回到新的 `deserialize` 方法报错。`'_` 是一个特殊的生命周期标记。它被用于生命周期省略或临时生命周期标注。
它可以被编译器自动推导。但在类型约束这里并不被允许。

Rust 要求在类型约束时, 必须手动标注明确的生命周期名称。因为编译器无法在这里推断出具体的生命周期。

我们将 `'_` 替换为 `'a`, 再次运行。
> 需要注意的是, Rust 的声明周期命名并没有什么特别要求, 只是一般通常使用单个小写字母命名。

原先的报错消失了, 新的报错出现了。

### 高阶生命周期绑定

```bash
error[E0261]: use of undeclared lifetime name `'a`
  --> src\todo\core.rs:68:43
   |
68 |     Self: Sized + Serialize + Deserialize<'a>,
   |                                           ^^ undeclared lifetime
   |
   = note: for more information on higher-ranked polymorphism, visit https://doc.rust-lang.org/nomicon/hrtb.html
help: consider making the bound lifetime-generic with a new `'a` lifetime
   |
68 |     Self: Sized + Serialize + for<'a> Deserialize<'a>,
   |                               +++++++
help: consider making the bound lifetime-generic with a new `'a` lifetime
   |
68 |     for<'a> Self: Sized + Serialize + Deserialize<'a>,
   |     +++++++
help: consider introducing lifetime `'a` here
   |
66 | pub trait Serializer<'a>
   |                     ++++
```

还是聚焦报错内容 ```use of undeclared lifetime name `'a` ```, 意思是我们使用了未声明的生命周期。编译器也给出多种解决方法。

以下是几种解决方法的含义:

- `Self: Sized + Serialize + for<'a> Deserialize<'a>`:
  这是最常见通用的写法, 使用了高阶生命周期约束, 表示不论 `'a` 是什么生命周期, `Self` 都能实现特征 `Deserialize<'a>`。

- `pub trait Serializer<'a>`:
  这让特征本身携带生命周期参数, 可以在该特征的所有方法中使用, 但会导致使用特征时需要额外传递生命周期, 侵入性较强。

- `for<'a> Self: Sized + Serialize + Deserialize<'a>,`:
  同样使用了高阶生命周期约束, 但 `'a` 被作用于整个约束条件, 表示不论 `'a` 是什么生命周期都能让类型约束成立。

我们使用第一种即可。改造完毕后, 再次运行, 这次没有再报错了。

## 验证功能

到达这一步, 我们已经完成了 Todo CLI 的创建、查看、筛选和持久化功能。
尽管我们可以手动运行命令行进行验证, 但随着功能越来越多、逻辑越来越复杂, 仅靠人手操作显得既繁琐又容易遗漏。

Rust 提供了强大的内建测试模块, 允许我们通过自动化方式验证功能是否正确, 避免反复手动测试。

### 单元测试

单元测试目标是测试某一个代码单元(一般都是函数), 验证该单元是否能按照预期进行工作,
例如测试一个 `add` 函数, 验证当给予两个输入时, 最终返回的和是否符合预期。

我们可以在每个模块中写自己的测试逻辑, 并通过 cargo test 命令批量执行它们。

Rust 中通常将单元测试代码和被测试代码放在一个文件中。

```rust
// src/todo/core.rs

// ...
#[cfg(test)]
mod tests {
  // 因为是子模块, 因此需要使用 super 关键字来引用父模块
  use super::{Serializer, TodoItem};

  #[test]
  fn test_todo_item_creation() {
    let item = TodoItem::new("test1", "content");
    assert_eq!(item.title, "test");
    assert_eq!(item.content, "content");
  }

  #[test]
  fn test_serialization_roundtrip() {
    let original = TodoItem::new("test", "content");
    let serialized = original.serialize();
    let deserialized = TodoItem::deserialize(serialized);

    assert_eq!(original.title, deserialized.title);
    assert_eq!(original.content, deserialized.content);
  }
}
```

以上代码中, 我们添加了两个测试函数:

- `test_todo_item_creation`: 验证 `TodoItem::new`方法能否正确赋值。
- `test_serialization_roundtrip`: 验证结构体能否被序列化后再还原回来。

在 `src/todo/core.rs` 文件中增加以上内容后, 运行 `cargo test` 命令, Rust 就会进行测试了。

```bash
test todo::core::tests::test_serialization_roundtrip ... ok
test todo::core::tests::test_todo_item_creation ... FAILED

failures:

---- todo::core::tests::test_todo_item_creation stdout ----

thread 'todo::core::tests::test_todo_item_creation' panicked at src\todo\core.rs:88:9:
assertion `left == right` failed
  left: "test1"
 right: "test"
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    todo::core::tests::test_todo_item_creation

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

可以看见 `todo::core::tests::test_todo_item_creation` 方法报错了, 说明内容:

```bash
assertion `left == right` failed
  left: "test1"
 right: "test"
```

意思是断言失败了, 因为两个值不匹配。
回到测试代码, 把 `let item = TodoItem::new("test1", "content");` 中写错的 `test1` 改为 `test`。
重新运行 `cargo test` 命令, 结果如下:

```bash
running 2 tests
test todo::core::tests::test_todo_item_creation ... ok
test todo::core::tests::test_serialization_roundtrip ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

说明我们的测试全部通过, 功能符合预期。

### 断言

断言是指在程序中设置检查点, 当程序执行到这些检查点时, 会对程序的状态进行检查。
如果检查结果为真, 程序继续执行；如果检查结果为假, 程序会抛出异常, 终止执行。

Rust 中常用的断言有以下几种:

- `assert!(expr)`: 如果 `expr` 为假, 抛出异常。
- `assert_eq!(left, right)`: 如果 `left` 不等于 `right`, 抛出异常。
- `assert_ne!(left, right)`: 如果 `left` 等于 `right`, 抛出异常。

如果加上 `debug_` 前缀, 则只在 `Debug` 模式运行, 如 `debug_assert!(expr)`。

### 条件编译

在测试部分的代码中, 我们可以看见在模块 `tests` 上的 `#[cfg(test)]`。

它用于进行条件编译。表示 `tests` 的代码仅在满足 `test` 条件时进行编译。
即只在 `cargo test` 命令执行时才会编译。

除了 `test` 条件外, 我们还可以增加更多的条件, 例如:

- `#[cfg(all(target_os="windows", test))]` 表示仅在编译对象为 `windows` 平台时运行 `cargo test` 编译。
- `#[cfg(all(any(target_os = "ios", target_os = "android"), test))]` 表示仅在编译对象为移动端时运行 `cargo test` 编译。
- `#[cfg(all(not(any(target_os = "ios", target_os = "android")), test))]` 表示仅在编译对象非移动端时运行 `cargo test` 编译。

条件编译可以用在许多地方, 小到一个变量, 大到一个模块都可以使用条件编译。

## 总结

通过本文的学习, 我们不仅迈出了 Rust 编程的第一步, 更通过亲手实现一个 Todo CLI, 将理论知识转化为实际应用能力。
从最初的 “Hello, world!” 输出, 到最终能通过命令行创建、列出 Todo 项并实现数据持久化, 我们逐步掌握了 Rust 从基础语法到核心特性的关键知识点。

在这个过程中, 我们深入理解了 Rust 区别于其他语言的核心设计:

- 所有权系统通过严格的内存管理规则避免悬垂指针和重复释放问题。
- 借用与生命周期机制确保引用的有效性。
- 特征与泛型则实现了灵活的代码抽象与复用。

同时, 我们也实践了 Rust 工程化开发的关键环节。
使用 cargo 管理项目与依赖、通过模块化拆分代码结构。
借助 `serde` 和 `clap` 等第三方库提升开发效率, 以及通过单元测试保障代码质量。

然而, 当前的 Todo CLI 仍有较大优化空间:

目前的功能仅支持 create（创建）和 list（列表）两个命令, 缺乏对 Todo 项的删除和修改功能, 无法应对日常使用中 “任务变更” 的场景。

Todo 项数据仅包含标题和内容, 缺少状态标记（如 “已完成”“未完成”）, 难以跟踪任务进度。

此外, 命令行交互的容错性、筛选功能的精细化（如按状态筛选）等细节也有待完善。

但这些不足恰恰是深入学习的契机。

我们可以尝试通过扩展功能、优化实现, 我们可以进一步巩固 Rust 的模式匹配、错误处理、枚举设计等知识点。
真正将 “内存安全”“高性能” 的特性融入实际开发中, 让这个简单的工具逐渐成长为一个实用、健壮的生产力工具。

## 参考内容

- [锈书](https://rusty.course.rs/)
- [Rust 官网](https://www.rust-lang.org/)
- [Rust 参考手册](https://doc.rust-lang.org/stable/reference/introduction.html)
- [Rust 语言圣经](https://course.rs/about-book.html)
- [通过例子学习 Rust](https://doc.rust-lang.org/rust-by-example/)
- [100个练习题学习 Rust](https://colobu.com/rust100/)
- [Rust 程序设计语言 中文版](https://rustwiki.org/zh-CN/book/title-page.html)
- [Rust 高级编程 2018 - 中文译本](https://learnku.com/docs/nomicon/2018)
