# Linux 基础开发工具 — 复习文档

> 来源：Linux 系统编程课程第 2 讲课件 + 课堂板书（已剔除前几节课内容）
> 本节核心工具链：**yum/apt → vim → gcc/g++ → make/Makefile → 进度条实践 → git → gdb**

---

## 1. 软件包管理器 yum / apt

### 1.1 核心概念

- **软件包**：提前编译好的程序（类似 Windows 安装程序），存放在服务器上。
- **包管理器**：类似"应用商店"，负责下载、安装、解决依赖。
  - CentOS / RedHat / Fedora：`yum`
  - Ubuntu：`apt`
- **软件源（repo）**：提供软件包的服务器地址；国内建议换镜像源（阿里云、清华 TUNA、中科大 USTC 等）加速。

### 1.2 常用命令（需网络畅通，需 sudo）

| 操作 | CentOS (yum) | Ubuntu (apt) |
|---|---|---|
| 查找软件包 | `yum list \| grep 包名` | `apt search 包名` |
| 查看包详情 | — | `apt show 包名` |
| 安装 | `sudo yum install -y 包名` | `sudo apt install -y 包名` |
| 卸载 | `sudo yum remove -y 包名` | `sudo apt remove -y 包名` |
| 装扩展源 | `sudo yum install -y epel-release` | — |

- `-y`：自动确认，不交互。
- 同一时刻只能有一个 yum/apt 进程在装软件。
- 验证网络：`ping www.baidu.com`

### 1.3 软件包命名规则

`主版本号.次版本号.源程序发行号-软件包发行号.发行版.架构`
- `x86_64` = 64 位，`i686` = 32 位（要与系统匹配）
- `el7` = CentOS7 / RedHat7，`el6` = CentOS6
- 最后一列（如 `@base`）表示软件源名称。

### 1.4 源配置文件位置

- CentOS：`/etc/yum.repos.d/`（`CentOS-Base.repo` 标准源、`epel.repo` 扩展源）
- Ubuntu：`/etc/apt/sources.list`（标准源）、`/etc/apt/sources.list.d/`（扩展源）

换源通用流程：备份旧配置 → 下载新源配置 → 清缓存重建（`yum clean all && yum makecache` / `apt update`）。

---

## 2. 编辑器 vim

### 2.1 三种核心模式

| 模式 | 作用 | 进入 / 退出 |
|---|---|---|
| 命令模式 (Normal) | 移动光标、删除/复制/粘贴、切换到其他模式 | 打开文件后默认所在；任何模式下按 `ESC` 回到此模式 |
| 插入模式 (Insert) | 输入文字（最常用编辑模式） | 命令模式下按 `i` / `a` / `o` |
| 底行模式 (Last Line) | 保存、退出、查找、替换、设置 | 命令模式下按 `:`（shift+;） |

- `i`：光标前插入；`a`：光标后插入；`o`：下一行新开一行插入。
- 底行模式常用：`:w` 保存、`:q` 退出、`:wq` 保存退出、`:q!` 强制不保存退出。

### 2.2 命令模式常用指令

**光标移动**

| 按键 | 作用 |
|---|---|
| `h` `j` `k` `l` | 左 / 下 / 上 / 右 |
| `gg` / `G`（shift+g） | 到文件首行 / 末行 |
| `#G`（如 `15G`） | 跳到第 # 行 |
| `$` / `^` | 行尾 / 行首 |
| `w` / `e` / `b` | 下一个词首 / 下一个词尾 / 上一个词首 |
| `ctrl+b` / `ctrl+f` | 后翻 / 前翻一页 |
| `ctrl+u` / `ctrl+d` | 后翻 / 前翻半页 |

**删除 / 复制 / 粘贴**

| 按键 | 作用 |
|---|---|
| `x` / `#x` | 删光标处（及之后共 # 个）字符 |
| `X` / `#X` | 删光标前 1 个 / # 个字符 |
| `dd` / `#dd` | 删除当前行 / 从当前行删 # 行 |
| `yy` / `#yy` | 复制当前行 / 复制 # 行 |
| `yw` / `#yw` | 复制一个词 / # 个词 |
| `p` | 粘贴（复制类命令需配合 p 使用） |

**其他**

| 按键 | 作用 |
|---|---|
| `r` / `R` | 替换单个字符 / 持续替换模式（ESC 结束） |
| `u` | 撤销（可多次） |
| `ctrl+r` | 反撤销（恢复撤销） |
| `cw` / `c#w` | 修改一个词 / # 个词 |
| `ctrl+g` | 显示光标所在行号 |

### 2.3 底行模式常用指令

- `:set nu`：显示行号
- `:#`（如 `:15`）：跳到第 # 行
- `/关键字`：向下查找，按 `n` 找下一个
- `?关键字`：向上查找，按 `n` 找上一个
- `:w`、`:q`、`:wq`、`:q!`

### 2.4 vim 配置（了解）

- 全局配置：`/etc/vimrc`（所有用户生效）
- 个人配置：`~/.vimrc`（对当前用户生效，推荐）
- 常用配置项：

```vim
syntax on            " 语法高亮
set nu               " 显示行号
set shiftwidth=4     " 缩进空格数为 4
```

- 官方自带教程：终端执行 `vimtutor`

---

## 3. 编译器 gcc / g++

### 3.1 编译的四个阶段

```
hello.c ──预处理──> hello.i ──编译──> hello.s ──汇编──> hello.o ──链接──> hello(可执行)
           (gcc -E)           (gcc -S)          (gcc -c)          (gcc)
```

| 阶段 | 命令 | 做了什么 |
|---|---|---|
| 预处理 | `gcc -E hello.c -o hello.i` | 宏替换、头文件展开、条件编译、去注释（生成 `.i`） |
| 编译 | `gcc -S hello.i -o hello.s` | 语法检查，翻译成汇编（生成 `.s`） |
| 汇编 | `gcc -c hello.s -o hello.o` | 转成机器可识别的二进制目标文件（生成 `.o`） |
| 链接 | `gcc hello.o -o hello` | 把目标文件与库链接成可执行文件 |

一步编译：`gcc hello.c -o hello`（g++ 同理）。

### 3.2 常用选项

| 选项 | 作用 |
|---|---|
| `-o 文件名` | 指定输出文件 |
| `-g` | 生成调试信息（供 gdb 使用） |
| `-static` | 静态链接 |
| `-shared` | 生成动态库 |
| `-O0/-O1/-O2/-O3` | 优化级别（O0 无优化，O3 最高） |
| `-w` / `-Wall` | 关闭所有警告 / 开启所有警告 |

### 3.3 动态链接 vs 静态链接

| | 动态链接 | 静态链接 |
|---|---|---|
| 时机 | 程序**运行时**才链接库 | **编译链接时**把库代码拷进可执行文件 |
| 优点 | 节省空间；库更新无需重编 | 运行时速度快、不依赖外部库 |
| 缺点 | 运行时依赖库存在 | 体积大、库更新需重编译 |

- gcc **默认动态链接**，可用 `file 可执行文件` 验证。
- `ldd 可执行文件`：查看程序依赖的共享库列表。
- 库的本质：`printf` 等函数实现放在 `libc.so.6`，链接时 gcc 默认到 `/usr/lib` 查找。
- 库后缀：Linux 动态库 `.so`、静态库 `.a`；Windows 动态库 `.dll`、静态库 `.lib`。
- 云服务器安装 C/C++ 静态库（CentOS）：`yum install -y glibc-static libstdc++-static`

---

## 4. 自动化构建 make / Makefile

### 4.1 基本概念

- **make 是命令，Makefile 是文件**，两者配合完成项目自动化编译。
- Makefile 定义规则：哪些文件先编译、哪些后编译、何时需要重新编译。
- 写好后只需一个 `make` 命令，整个工程自动编译。

### 4.2 最小示例

```makefile
myproc:myproc.c          # 目标:依赖（依赖关系）
	gcc -o myproc myproc.c   # 依赖方法（注意：行首必须是 Tab）

.PHONY:clean             # 伪目标，总是被执行
clean:
	rm -f myproc
```

- 第一个目标是默认目标，执行 `make` 即构建它。
- `make clean` 显式执行清理目标。

### 4.3 make 的工作原理

1. 在当前目录找 `Makefile` / `makefile`；
2. 以文件中**第一个目标**为最终目标；
3. 目标不存在，或依赖文件比目标**更新**（比较 Modify 时间），则执行对应命令重新生成；
4. 依赖不存在则递归查找其规则（类似压栈过程），找不到依赖就直接报错退出。

> 知识补充：`stat 文件名` 可查看文件时间属性
> - **Modify**：内容修改时间；**Change**：属性修改时间；**Access**：最近访问时间。
> - make 通过比较依赖与目标的 **Modify 时间**决定是否重新编译。
> - `.PHONY` 伪目标让 make 忽略时间对比，**总是执行**。

### 4.4 常用变量与符号

```makefile
BIN=proc.exe             # 定义变量
CC=gcc
SRC=$(wildcard *.c)      # 获取当前目录所有 .c 文件
OBJ=$(SRC:.c=.o)         # 把 .c 替换为同名 .o
RM=rm -f

$(BIN):$(OBJ)
	@$(CC) -o $@ $^        # $@ = 目标文件；$^ = 所有依赖文件
%.o:%.c                  # 模式规则：每个 .c 生成同名 .o
	@$(CC) -c $<           # $< = 逐个依赖文件；@ = 不回显命令
.PHONY:clean
clean:
	$(RM) $(OBJ) $(BIN)
```

- `@` 加在命令前：执行时不回显该命令。
- `make` 命令前必须使用 **Tab** 缩进，不能用空格。

---

## 5. 第一个 Linux 程序：进度条

### 5.1 回车与换行（基础概念）

- `\n`（换行）：光标移到下一行行首（老式打字机"换行 + 回车"两动作合一）。
- `\r`（回车）：光标回到**当前行行首**，配合覆写实现"原地刷新"效果。

### 5.2 行缓冲区

- printf 输出默认先进入**行缓冲区**，遇到 `\n`（或缓冲区满、程序结束）才真正显示。
- 无 `\n` 时内容不会立即显示 → 需要 `fflush(stdout)` 强制刷新。

```c
printf("hello");       // sleep(3) 期间看不到输出
fflush(stdout);        // 强制刷新缓冲区，立即显示
```

### 5.3 进度条核心套路

```c
printf("[%-100s][%d%%][%c]\r", buffer, cnt, lable[cnt%4]);
fflush(stdout);            // 每次打印后必须刷新
usleep(50000);             // 微秒级休眠
```

要点：
1. 用 `\r` 回到行首，每次覆盖上一帧，形成动画；
2. `%-100s` 左对齐撑满固定宽度；
3. 旋转光标 `|/-\` 用取模循环；
4. 每次输出后 `fflush(stdout)`；
5. 结束时补一个 `printf("\n")` 换行。

---

## 6. 版本控制器 Git

### 6.1 基本概念

- 版本控制器：记录文件的每次改动和版本迭代，便于回滚与多人协作。
- 最主流的是 **Git**（Linus 于 2005 年开发，特点：速度快、分布式、强分支支持）。

### 6.2 安装与克隆

```bash
yum install git          # 安装
git --version            # 验证
git clone [url]          # 把远端仓库下载到本地
```

### 6.3 三板斧（提交到 Github）

```bash
git add 文件名            # 1. 告诉 git 要管理哪些文件（git add . 添加当前目录全部）
git commit -m "提交说明"  # 2. 提交到本地仓库，-m 必须写清楚改动说明
git push                 # 3. 同步到远端服务器（需用户名密码/Token）
```

### 6.4 其他常用命令

- `git log`：查看提交历史
- `git status`：查看当前状态（哪些文件被改动/未跟踪）
- `git pull`：拉取远端最新代码
- `.gitignore`：配置不需要 git 管理的文件

---

## 7. 调试器 gdb / cgdb

### 7.1 前提：编译时加 `-g`

- gcc 默认生成 **release** 版，**不含调试信息**，无法 gdb 调试。
- 必须加 `-g` 生成 **debug** 版：`gcc mycmd.c -o mycmd -g`
- 可用 `file mycmd` 验证（debug 版会显示 `with debug_info`）。
- 进入：`gdb 可执行文件名`；退出：`quit` 或 `ctrl+d`。

### 7.2 常用命令速查表

| 命令 | 作用 | 示例 |
|---|---|---|
| `list` / `l` | 显示源码（每次 10 行） | `l`、`l main`、`l mycmd.c:1` |
| `run` / `r` | 从头运行程序 | `r` |
| `next` / `n` | 单步执行，**不进函数**（逐过程） | `n` |
| `step` / `s` | 单步执行，**进入函数**（逐语句） | `s` |
| `break` / `b` | 打断点 | `b 10`、`b main`、`b mycmd.c:10` |
| `info b` | 查看所有断点 | `info b` |
| `continue` / `c` | 继续执行到下一断点 | `c` |
| `finish` | 执行到当前函数返回并停住 | `finish` |
| `until 行号` | 直接执行到指定行 | `until 20` |
| `print` / `p` | 打印变量/表达式的值 | `p x`、`p start+end` |
| `set var 变量=值` | 修改变量的值（验证问题原因） | `set var flag=1` |
| `display 变量` | 每次停下自动显示该变量 | `display i` |
| `undisplay 编号` | 取消自动显示 | `undisplay 1` |
| `delete/d 断点编号` | 删除断点 | `d 1`（不带编号删全部） |
| `disable` / `enable` | 禁用 / 启用断点 | `disable 1` |
| `watch 变量` | 监视变量，**值一变就暂停** | `watch result` |
| `backtrace` / `bt` | 查看函数调用栈 | `bt` |
| `info locals` | 查看当前栈帧的局部变量 | `info locals` |

### 7.3 条件断点（重点）

两种写法，语法不同别混淆：

```gdb
b 9 if i == 30        # 方式1：新建条件断点（有 if）
condition 2 i==30     # 方式2：给已有 2 号断点追加条件（无 if）
```

### 7.4 实用技巧

- **watch 定位"谁改了变量"**：变量不该变却变了 → `watch` 它，一变就通知。
- **set var 验证猜想**：怀疑某个标志位导致结果错误 → `set var` 改值重跑确认。
- **cgdb**：带源码分屏的 gdb，体验更好。
  - 安装：CentOS `sudo yum install -y cgdb`；Ubuntu `sudo apt-get install -y cgdb`
  - 分屏切换：按 `ESC` 进代码屏，按 `i` 回 gdb 命令屏。

---

## 附：本节工具链关系图

```
yum/apt 装环境 ──> vim 写代码 ──> gcc -g 编译 ──> Makefile 自动化构建
                                        │
                                        ├─> 程序有 bug ──> gdb/cgdb 调试
                                        └─> 代码管理 ──> git 三板斧上传 Github
```
