可以。你这部分目录比较完整，**异常（Exception）这一章我建议按“概念 → 抛出/捕获 → 栈展开 → 匹配处理 → 重新抛出 → 安全问题 → 规范 → 标准库异常”这样的顺序学习**，这样知识点之间是连起来的，而不是一个个孤立地背。我们先讲**第一块：1.1 异常的概念 + 1.2 异常的抛出和捕获**，这两节是整个异常机制的核心。

# 第一块：异常的概念、抛出与捕获

## 1.1 什么是异常？

先不要急着记语法，先理解**异常到底是解决什么问题的**。

我们以前写代码的时候，经常会遇到这样的情况：

```cpp
int Div(int x, int y)
{
    return x / y;
}

int main()
{
    int ret = Div(10, 0);
}
```

这里 `y == 0`，显然存在问题。

传统 C/C++ 中，我们可能这样处理：

```cpp
int Div(int x, int y)
{
    if (y == 0)
    {
        return -1;
    }

    return x / y;
}
```

调用者：

```cpp
int ret = Div(10, 0);

if (ret == -1)
{
    // 处理错误
}
```

这种方式的问题是：**函数的返回值既承担“正常结果”，又承担“错误信息”。**

例如：

```cpp
int Find(const vector<int>& v, int x)
{
    // 找到了返回下标
    // 找不到返回 -1
}
```

这里 `-1` 是人为规定的错误码。

但是如果函数本身的返回值有可能就是所有整数：

```cpp
int Calculate();
```

那你就很难设计一个不会和正常结果冲突的错误码。

而且还有一个更麻烦的问题：

```cpp
void A()
{
    B();
}

void B()
{
    C();
}

void C()
{
    D();
}

void D()
{
    // 出错了
}
```

如果 `D()` 出错，我们可能需要：

```cpp
D() 出错
↓
C() 检查错误
↓
B() 检查错误
↓
A() 检查错误
↓
main() 检查错误
```

**每一层都需要判断错误、传递错误。**

代码会变得非常繁琐。

于是 C++ 提供了**异常机制（Exception Handling）**。

它的核心思想可以概括成一句话：

> **正常情况下按照正常流程执行；发生异常时，立即跳出当前正常执行流程，把异常交给能够处理它的地方。**

所以异常本质上是一种**错误处理机制**。

---

# 1.2 异常的抛出和捕获

C++ 异常机制最核心的三个关键字：

```cpp
try
throw
catch
```

可以先记住这个基本结构：

```cpp
try
{
    // 可能出现异常的代码
}
catch (...)
{
    // 处理异常
}
```

但是异常从哪里来？

通过：

```cpp
throw
```

抛出。

例如：

```cpp
int Div(int x, int y)
{
    if (y == 0)
    {
        throw "除数不能为0";
    }

    return x / y;
}

int main()
{
    try
    {
        int ret = Div(10, 0);
        cout << ret << endl;
    }
    catch (const char* str)
    {
        cout << str << endl;
    }

    return 0;
}
```

执行：

```cpp
Div(10, 0)
```

进入：

```cpp
if (y == 0)
{
    throw "除数不能为0";
}
```

于是异常被**抛出**。

注意这里有一个非常重要的事情：

```cpp
throw "除数不能为0";
```

并不是普通的：

```cpp
return "除数不能为0";
```

`return` 的意思是：

> **函数正常结束，把一个值返回给调用者。**

而 `throw` 的意思是：

> **当前正常执行流程出现异常，中断当前流程，把异常交给外层寻找能够处理它的 `catch`。**

所以：

```text
return
    ↓
正常返回

throw
    ↓
异常退出当前执行流程
```

这是理解异常机制最重要的区别之一。

---

# 1.3 `try`、`throw`、`catch` 到底是怎么配合的？

我们把刚才的代码拆开：

```cpp
try
{
    int ret = Div(10, 0);
    cout << ret << endl;
}
catch (const char* str)
{
    cout << str << endl;
}
```

可以把它理解成：

```text
try
│
├── 执行正常
│     ↓
│   继续执行后面的代码
│
└── 发生异常
      ↓
    throw
      ↓
    立即停止 try 中后续代码
      ↓
    寻找匹配的 catch
      ↓
    执行 catch
```

例如：

```cpp
try
{
    cout << "A" << endl;
    throw 10;
    cout << "B" << endl;
}
catch (int e)
{
    cout << "C" << endl;
}
```

输出：

```text
A
C
```

不会输出：

```text
B
```

因为：

```cpp
throw 10;
```

执行之后，**当前 `try` 块中 `throw` 后面的代码不会继续执行。**

这一点非常重要。

可以把：

```cpp
throw 10;
```

理解成：

> “这里出问题了，我不继续执行当前流程了，你们外层谁能处理这个错误，谁来处理。”

---

# 1.4 `throw` 后面可以抛什么？

这是 C++ 异常机制非常重要的一点：

**`throw` 后面几乎可以放任意类型的对象。**

例如：

```cpp
throw 10;
```

抛出：

```cpp
int
```

也可以：

```cpp
throw 3.14;
```

抛出：

```cpp
double
```

还可以：

```cpp
throw 'A';
```

甚至：

```cpp
throw string("除数不能为0");
```

或者自己定义异常类：

```cpp
class Exception
{
public:
    string _msg;
};

throw Exception();
```

所以异常机制的基本思想就是：

```text
throw
  ↓
抛出一个异常对象
  ↓
catch
  ↓
根据异常对象的类型进行匹配
```

例如：

```cpp
try
{
    throw 10;
}
catch (int e)
{
    cout << "int异常：" << e << endl;
}
```

这里：

```cpp
throw 10;
```

抛出的是 `int` 类型。

因此：

```cpp
catch (int e)
```

能够匹配。

---

# 1.5 `catch` 为什么要写类型？

例如：

```cpp
try
{
    throw 10;
}
catch (int e)
{
    cout << "int异常" << endl;
}
```

这里：

```cpp
catch (int e)
```

实际上就是在说：

> **如果你抛出来的异常是 `int` 类型，那么我负责处理。**

如果：

```cpp
try
{
    throw 10.5;
}
catch (int e)
{
    cout << "int异常" << endl;
}
```

就匹配不上。

因为：

```text
throw 10.5
      ↓
    double

catch(int)
      ↓
    int
```

类型不同。

所以可以把 `catch` 理解成一种**异常类型筛选器**。

例如：

```cpp
try
{
    throw 10;
}
catch (double e)
{
    cout << "double" << endl;
}
catch (int e)
{
    cout << "int" << endl;
}
catch (const char* e)
{
    cout << "string" << endl;
}
```

执行：

```cpp
throw 10;
```

最终匹配：

```cpp
catch (int e)
```

---

# 1.6 一个非常重要的问题：异常是怎么“传出去”的？

这个问题会直接连接你目录中的 **1.3 栈展开**，所以这里先给你建立一个概念。

例如：

```cpp
void D()
{
    throw 10;
}

void C()
{
    D();
}

void B()
{
    C();
}

void A()
{
    B();
}

int main()
{
    try
    {
        A();
    }
    catch (int e)
    {
        cout << "捕获异常：" << e << endl;
    }
}
```

调用过程：

```text
main
 ↓
 A()
 ↓
 B()
 ↓
 C()
 ↓
 D()
```

到了：

```cpp
throw 10;
```

异常产生。

那么问题来了：

**D 没有 `catch`，怎么办？**

C++ 会继续向外寻找：

```text
D
↓
C
↓
B
↓
A
↓
main
```

最终：

```cpp
main()
```

里面有：

```cpp
catch (int e)
```

于是就由它处理。

所以异常机制的一个重要特点就是：

> **异常可以跨越多层函数调用，直到找到能够匹配的 `catch`。**

这也是异常相比传统错误码非常重要的优势。

传统错误码：

```text
D 出错
↓
C 接收错误
↓
C 返回错误
↓
B 接收错误
↓
B 返回错误
↓
A 接收错误
↓
A 返回错误
↓
main 处理
```

异常：

```text
D
↓
throw
↓
直接向外寻找匹配的 catch
↓
main
↓
catch
```

当然，实际上中间还有一个非常重要的过程——**栈展开（Stack Unwinding）**。

这就是你目录中的：

> **1.3 栈展开**

它是理解 C++ 异常机制的关键，尤其是理解**局部对象析构、RAII、异常安全**。

---

# 1.7 `catch(...)`：不管什么异常都接

还有一种特殊写法：

```cpp
catch (...)
{
    cout << "发生异常" << endl;
}
```

这里的：

```cpp
...
```

表示：

> **匹配任意类型的异常。**

例如：

```cpp
try
{
    throw 10;
}
catch (...)
{
    cout << "发生异常" << endl;
}
```

可以捕获。

即使：

```cpp
throw string("error");
```

也可以捕获。

所以：

```cpp
catch (...)
```

相当于一个**兜底的 catch**。

但是你现在先不要把它理解成“以后所有异常都用这个”，因为实际项目中通常希望知道**异常的具体类型**，而不是简单地把所有异常一锅端。后面学习异常规范、标准库异常的时候会继续遇到它。

---

# 1.8 你现在需要建立的整体认知

到这里，先不要急着背很多细节。你只需要把异常机制的主线建立起来：

```text
程序正常执行
      ↓
发现异常情况
      ↓
throw 抛出异常对象
      ↓
停止当前正常执行流程
      ↓
向调用链外层寻找匹配的 catch
      ↓
找到
      ↓
执行 catch
      ↓
异常处理完成
```

其中三个关键字：

| 关键字     | 作用         |
| ------- | ---------- |
| `try`   | 放可能发生异常的代码 |
| `throw` | 抛出异常       |
| `catch` | 捕获并处理异常    |

再记住三个最重要的结论：

> **① `throw` 不是普通的 `return`，它表示异常发生。**
> **② `throw` 后，当前 `try` 中后面的代码不会继续执行。**
> **③ 异常可以跨越多层函数调用，向外寻找匹配的 `catch`。**

---

## 下一块

下一块我们直接进入你目录里的 **1.3「栈展开」**。这一节我建议重点讲，因为它实际上是 C++ 异常机制里最容易“看懂代码但没真正理解”的地方。尤其是下面这种代码：

```cpp
void Func()
{
    A a;
    B b;
    C c;

    throw 10;
}
```

当 `throw` 发生时，`a、b、c` 到底发生了什么？**为什么析构函数会被调用？为什么这和 RAII 有直接关系？异常到底是怎么从 `Func()` 一层一层传出去的？**这些问题搞清楚之后，后面的 `1.4 查找匹配的处理代码` 会自然很多。

# 2
好，继续讲 **1.3 栈展开（Stack Unwinding）**。这一节非常重要，因为它解释了一个核心问题：**异常抛出以后，C++到底是怎么从当前函数一路退出，再找到外层 `catch` 的？**

# 1.3 栈展开

## 一、先理解“栈展开”是什么

先看一个例子：

```cpp
void D()
{
    throw 10;
}

void C()
{
    D();
}

void B()
{
    C();
}

void A()
{
    B();
}

int main()
{
    try
    {
        A();
    }
    catch (int e)
    {
        cout << "捕获异常：" << e << endl;
    }
}
```

正常情况下，函数调用关系是：

```text
main()
 ↓
A()
 ↓
B()
 ↓
C()
 ↓
D()
```

程序执行到：

```cpp
throw 10;
```

异常发生。

此时 `D()` 中没有能够匹配的 `catch`，怎么办？

C++就开始**沿着函数调用链向外寻找能够处理这个异常的 `catch`**：

```text
D()
 ↓
C()
 ↓
B()
 ↓
A()
 ↓
main()
 ↓
catch(int)
```

这个过程中，当前函数以及中间函数的栈帧会逐层退出，这个过程就叫：

> **栈展开（Stack Unwinding）**

你可以先把它简单理解成：

> **发生异常后，程序从当前函数开始，一层一层往外退，同时销毁这些函数中的局部对象，直到找到匹配的 `catch`。**

---

# 二、为什么叫“栈展开”？

你之前已经学过函数调用和栈帧，所以这里可以直接联系起来。

假设：

```cpp
main()
{
    A();
}

A()
{
    B();
}

B()
{
    C();
}

C()
{
    D();
}

D()
{
    throw 10;
}
```

函数调用过程中，栈大概可以理解成：

```text
┌──────────────┐
│ D() 栈帧      │ ← 当前
├──────────────┤
│ C() 栈帧      │
├──────────────┤
│ B() 栈帧      │
├──────────────┤
│ A() 栈帧      │
├──────────────┤
│ main() 栈帧   │
└──────────────┘
```

`D()` 抛出异常之后：

```text
D() 退出
 ↓
C() 退出
 ↓
B() 退出
 ↓
A() 退出
 ↓
main() 中的 catch 接住
```

所以栈逐渐“退回去”。

这就是栈展开。

---

# 三、最重要的：局部对象会析构

这一点是这一节最值得你理解的内容。

看代码：

```cpp
class A
{
public:
    A()
    {
        cout << "A构造" << endl;
    }

    ~A()
    {
        cout << "A析构" << endl;
    }
};

void Func()
{
    A a;

    throw 10;

    cout << "Func继续执行" << endl;
}
```

调用：

```cpp
try
{
    Func();
}
catch (int e)
{
    cout << "捕获异常" << endl;
}
```

输出大致是：

```text
A构造
A析构
捕获异常
```

注意：

```cpp
throw 10;
```

后面的：

```cpp
cout << "Func继续执行" << endl;
```

不会执行。

但是 `a` 的析构函数：

```cpp
~A()
```

**会执行。**

为什么？

因为 `throw` 导致 `Func()` 的栈开始展开。

而 `a` 是 `Func()` 中创建的局部对象：

```cpp
A a;
```

当 `Func()` 因为异常退出时，C++必须对已经构造完成的局部对象进行清理。

所以：

```text
Func()
│
├── A a;       ← 构造
│
├── throw 10
│
└── 异常
     ↓
   栈展开
     ↓
   a.~A()
     ↓
   Func()退出
```

这就是为什么 **C++异常机制和析构函数、RAII联系非常紧密。**

---

# 四、多个局部对象怎么办？

看这个：

```cpp
void Func()
{
    A a;
    B b;
    C c;

    throw 10;
}
```

假设三个对象都正常构造：

```text
A构造
B构造
C构造
```

发生：

```cpp
throw 10;
```

那么析构顺序是：

```text
C析构
B析构
A析构
```

也就是：

> **局部对象按照与构造相反的顺序析构。**

这和普通函数正常结束时的析构规则是一致的。

正常：

```cpp
void Func()
{
    A a;
    B b;
    C c;
}
```

离开 `Func()`：

```text
C析构
B析构
A析构
```

异常：

```cpp
void Func()
{
    A a;
    B b;
    C c;

    throw 10;
}
```

也是：

```text
C析构
B析构
A析构
```

所以你可以记：

> **异常并不会让已经构造完成的局部对象“凭空消失”，栈展开过程中仍然会调用它们的析构函数。**

---

# 五、如果对象还没有构造完成呢？

这个地方再深入一点。

例如：

```cpp
void Func()
{
    A a;
    B b;

    throw 10;

    C c;
}
```

执行：

```text
A构造
B构造
throw
```

`C c` 根本没有执行到，因此 `C` 没有构造。

所以栈展开时：

```text
B析构
A析构
```

不会有：

```text
C析构
```

这说明一个非常重要的原则：

> **只有已经成功构造完成的对象，离开作用域时才需要析构。**

这也是 C++对象生命周期管理非常核心的知识。

---

# 六、栈展开不仅发生在一个函数内部

现在回到最开始的例子：

```cpp
void D()
{
    A a;
    throw 10;
}

void C()
{
    B b;
    D();
}

void B()
{
    C();
}

int main()
{
    try
    {
        B();
    }
    catch (int e)
    {
        cout << "catch" << endl;
    }
}
```

假设 `D()` 抛出异常。

首先：

```text
D()
```

里面的：

```cpp
A a;
```

析构。

然后 `D()`退出。

但是 `C()`也没有处理这个异常，于是继续展开 `C()`。

如果 `C()`里面有：

```cpp
B b;
```

那么：

```text
B b析构
C()退出
```

然后继续：

```text
B()退出
↓
main()
↓
catch(int)
```

所以整个过程可以理解成：

```text
D()
 │
 │ throw 10
 ↓
D()栈展开
 │
 └── 局部对象析构
 ↓
C()栈展开
 │
 └── 局部对象析构
 ↓
B()栈展开
 │
 └── 局部对象析构
 ↓
main()
 │
 └── catch(int)
```

这就是**完整的栈展开过程**。

---

# 七、这和 RAII 有什么关系？

这个知识点你以后学 C++后端会经常遇到，所以一定要建立联系。

RAII 的核心思想你可以先记成：

> **把资源的生命周期交给对象管理，在对象析构时自动释放资源。**

例如：

```cpp
{
    string s;
    vector<int> v;
    // ...
}
```

离开作用域时：

```text
v析构
s析构
```

如果是异常：

```cpp
{
    string s;
    vector<int> v;

    throw 10;
}
```

依然：

```text
throw
 ↓
v析构
 ↓
s析构
 ↓
离开作用域
```

所以异常机制实际上给 RAII 提供了一个非常重要的保障：

> **即使程序因为异常提前离开作用域，已经构造成功的局部对象依然会被正确析构，从而完成资源释放。**

例如以后你可能写：

```cpp
{
    lock_guard<mutex> lock(mtx);

    // 执行一些代码

    throw exception();
}
```

即使发生异常：

```text
throw
 ↓
lock_guard析构
 ↓
自动释放锁
```

这就是为什么现代 C++非常强调：

**RAII + 异常安全。**

---

# 八、一个容易混淆的问题：`catch` 在哪里？

看：

```cpp
void Func()
{
    A a;
    throw 10;
}

int main()
{
    try
    {
        Func();
    }
    catch (int e)
    {
        cout << e << endl;
    }
}
```

很多初学者会觉得：

> `Func()`抛异常 → `main()`的 `catch` 接住 → 那是不是 `Func()`还在？

不是。

实际上：

```text
Func()
 ↓
throw
 ↓
寻找catch
 ↓
Func()退出
 ↓
局部对象析构
 ↓
回到main的catch
 ↓
catch处理异常
```

也就是说：

**`catch` 执行的时候，抛出异常的那个函数通常已经退出了。**

这也是为什么不能把异常简单理解成“跳转到 catch”。

它不仅仅是：

```text
goto catch
```

而是：

```text
throw
 ↓
寻找匹配处理器
 ↓
沿途进行栈展开
 ↓
销毁局部对象
 ↓
到达catch
```

这就是栈展开真正重要的地方。

---

# 九、这一节你需要掌握到什么程度？

你现在不需要去研究编译器内部到底如何实现异常，也不用研究 ABI、异常表之类的底层细节。

目前掌握下面这张图就足够：

```text
             throw
               ↓
        当前函数发生异常
               ↓
       寻找匹配的 catch
               ↓
        ┌──────┴──────┐
        ↓             ↓
     找到了         没找到
        ↓             ↓
     栈展开        继续向外层
        ↓             ↓
  析构局部对象      栈展开
        ↓             ↓
      catch        继续寻找
```

最核心的四句话：

| 知识点  | 你应该理解成               |
| ---- | -------------------- |
| 栈展开  | 异常发生后沿调用链向外退出        |
| 局部对象 | 栈展开时会析构已经构造完成的局部对象   |
| 析构顺序 | 与构造顺序相反              |
| RAII | 异常提前退出作用域时，依然能自动释放资源 |

### 一个必须记住的例子

```cpp
void Func()
{
    A a;
    B b;
    C c;

    throw 10;
}
```

发生异常以后：

```text
throw 10
   ↓
c析构
   ↓
b析构
   ↓
a析构
   ↓
Func退出
```

**这就是“栈展开”。**

---

## 下一小节：1.4 查找匹配的处理代码

接下来就是一个非常自然的问题：

> **既然异常会一路往外找，那么 C++到底按照什么规则寻找匹配的 `catch`？**

例如：

```cpp
try
{
    throw 10;
}
catch (double)
{
}
catch (int)
{
}
catch (...)
{
}
```

为什么会进入第二个 `catch`？如果写成：

```cpp
catch (...)
{
}
catch (int)
{
}
```

又会发生什么？

以及：

```cpp
catch (const A&)
catch (A)
catch (B&)
```

这些到底怎么匹配。

**1.4 就专门解决这个问题。**

#  2
好，继续 **1.4 查找匹配的处理代码**。这一节核心就是弄明白：**`throw` 抛出异常以后，C++到底按照什么规则去选择哪个 `catch`。**

# 1.4 查找匹配的处理代码

## 一、先看最基本的匹配

例如：

```cpp
try
{
    throw 10;
}
catch (int e)
{
    cout << "int异常：" << e << endl;
}
```

这里：

```cpp
throw 10;
```

抛出的异常类型是 `int`，所以：

```cpp
catch (int e)
```

可以匹配。

如果：

```cpp
try
{
    throw 10.5;
}
catch (int e)
{
    cout << "int异常" << endl;
}
```

那么这个 `catch` 就不能匹配，因为：

```text
throw 10.5
    ↓
double

catch(int)
    ↓
int
```

所以最基本的规则就是：

> **C++会根据异常对象的类型，寻找能够匹配的 `catch`。**

---

# 二、可以有多个 `catch`

实际代码通常不是只有一个 `catch`：

```cpp
try
{
    // ...
}
catch (int e)
{
    cout << "int异常" << endl;
}
catch (double e)
{
    cout << "double异常" << endl;
}
catch (const char* e)
{
    cout << "字符串异常" << endl;
}
catch (...)
{
    cout << "未知异常" << endl;
}
```

例如：

```cpp
throw 10;
```

匹配：

```cpp
catch (int e)
```

如果：

```cpp
throw 3.14;
```

匹配：

```cpp
catch (double e)
```

如果：

```cpp
throw "error";
```

匹配：

```cpp
catch (const char* e)
```

---

# 三、一个非常重要的规则：从上往下匹配

例如：

```cpp
try
{
    throw 10;
}
catch (double e)
{
    cout << "double" << endl;
}
catch (int e)
{
    cout << "int" << endl;
}
catch (...)
{
    cout << "未知" << endl;
}
```

程序会：

```text
throw 10
   ↓
检查 catch(double)
   ↓
不匹配
   ↓
检查 catch(int)
   ↓
匹配
   ↓
执行 catch(int)
```

**匹配到一个以后，就不会继续往下面寻找。**

所以 `catch` 的顺序是有意义的。

---

# 四、`catch(...)` 为什么必须放最后？

看：

```cpp
try
{
    throw 10;
}
catch (...)
{
    cout << "未知异常" << endl;
}
catch (int e)
{
    cout << "int异常" << endl;
}
```

你可能觉得：

> `throw 10` 应该匹配下面的 `catch(int)`。

实际上不是。

因为：

```cpp
catch (...)
```

表示：

> **任何类型的异常我都可以匹配。**

所以程序执行：

```text
throw 10
 ↓
catch(...)
 ↓
匹配成功
 ↓
执行
 ↓
结束
```

根本不会继续检查下面的：

```cpp
catch(int)
```

因此：

> **如果使用 `catch(...)` 作为兜底处理，一般应该放在所有具体类型的 `catch` 后面。**

正确：

```cpp
catch (int e)
{
}
catch (double e)
{
}
catch (...)
{
}
```

错误/不合理：

```cpp
catch (...)
{
}
catch (int e)
{
}
```

---

# 五、为什么经常看到 `catch(const T&)`？

这个是 C++异常处理中非常重要的写法。

例如：

```cpp
class Exception
{
public:
    string _msg;
};

try
{
    throw Exception();
}
catch (const Exception& e)
{
    cout << e._msg << endl;
}
```

这里不是：

```cpp
catch (Exception e)
```

而是：

```cpp
catch (const Exception& e)
```

为什么？

主要有两个原因：

### ① 避免拷贝

如果：

```cpp
catch (Exception e)
```

异常对象可能需要拷贝/复制给 `e`。

而：

```cpp
catch (const Exception& e)
```

使用引用，不需要额外复制整个对象。

如果异常对象比较大，这一点很重要。

### ② 可以捕获派生类异常

例如：

```cpp
class Exception
{
};

class FileException : public Exception
{
};

try
{
    throw FileException();
}
catch (const Exception& e)
{
    cout << "异常" << endl;
}
```

这里可以捕获。

因为：

```text
FileException
      ↓
   继承自
      ↓
Exception
```

所以：

```cpp
catch (const Exception&)
```

可以捕获：

```cpp
FileException
```

这就涉及一个非常重要的知识点：

> **异常的匹配存在继承关系上的匹配。**

---

# 六、异常匹配和普通函数参数匹配有点像，但不要完全等同

例如：

```cpp
class A
{
};

class B : public A
{
};
```

然后：

```cpp
try
{
    throw B();
}
catch (const A& e)
{
    cout << "A" << endl;
}
```

可以匹配。

因为 `B` 是 `A` 的派生类。

但是如果：

```cpp
try
{
    throw B();
}
catch (A e)
{
}
```

也可能发生切片。

因此实际 C++项目中，**捕获异常对象通常更推荐使用引用**：

```cpp
catch (const A& e)
```

而不是：

```cpp
catch (A e)
```

后面学习标准库异常时，你会大量看到这种写法：

```cpp
catch (const exception& e)
```

这就是同一个思想。

---

# 七、为什么要按照“派生类 → 基类”的顺序写？

这是一个非常容易考、也非常容易写错的地方。

例如：

```cpp
class Exception
{
};

class FileException : public Exception
{
};
```

如果：

```cpp
try
{
    throw FileException();
}
catch (const Exception& e)
{
    cout << "Exception" << endl;
}
catch (const FileException& e)
{
    cout << "FileException" << endl;
}
```

那么：

```cpp
throw FileException();
```

首先检查：

```cpp
catch (const Exception&)
```

发现：

```text
FileException
   ↓
可以转换为
Exception&
```

于是已经匹配成功。

所以后面的：

```cpp
catch (const FileException&)
```

根本不会执行。

因此应该写成：

```cpp
catch (const FileException& e)
{
    cout << "FileException" << endl;
}
catch (const Exception& e)
{
    cout << "Exception" << endl;
}
```

也就是：

```text
具体异常
  ↓
派生类异常
  ↓
基类异常
  ↓
catch(...)
```

**越具体的放越前面，越宽泛的放越后面。**

---

# 八、异常匹配不是“随便转换都可以”

这里有一个很容易产生误解的地方。

比如：

```cpp
try
{
    throw 10;
}
catch (double e)
{
}
```

你可能会想：

```text
int
 ↓
double
```

普通 C++表达式里不是可以发生：

```cpp
int → double
```

吗？

例如：

```cpp
double x = 10;
```

确实可以。

但是**异常匹配并不是按照普通函数调用/赋值时的所有隐式转换规则来进行匹配的**。

所以不要把：

```cpp
throw 10;
```

理解成可以随便被：

```cpp
catch(double)
```

捕获。

对于你目前学习阶段，最重要的就是：

> **不要依赖数值类型之间的转换来设计异常匹配；让 `throw` 的类型和 `catch` 的类型明确对应。**

---

# 九、`throw` 抛出异常之后，到底在哪里找？

把前面的知识串起来。

例如：

```cpp
void D()
{
    throw 10;
}

void C()
{
    D();
}

void B()
{
    C();
}

int main()
{
    try
    {
        B();
    }
    catch (double e)
    {
        cout << "double" << endl;
    }
    catch (int e)
    {
        cout << "int" << endl;
    }
}
```

执行：

```text
main
 ↓
B
 ↓
C
 ↓
D
 ↓
throw 10
```

D没有处理。

于是开始向外：

```text
D
 ↓
C
 ↓
B
 ↓
main
```

最终找到：

```cpp
catch (int e)
```

匹配。

所以这里实际上涉及两个“顺序”：

**第一：调用链向外寻找**

```text
D → C → B → main
```

**第二：同一个 `try` 中的 `catch` 从上往下检查**

```text
catch 1
 ↓
catch 2
 ↓
catch 3
 ↓
...
```

把这两个方向搞清楚，异常匹配就基本不会乱。

---

# 十、如果一直找不到怎么办？

例如：

```cpp
void Func()
{
    throw 10;
}

int main()
{
    Func();
}
```

没有任何：

```cpp
try
catch
```

或者：

```cpp
try
{
    Func();
}
catch (double e)
{
}
```

但是抛出的是：

```cpp
int
```

也没有匹配的 `catch`。

那么异常会继续向更外层寻找。

如果最终：

> **整个调用链都没有找到匹配的异常处理代码**

那么程序会调用：

```cpp
std::terminate()
```

最终通常导致程序异常终止。

所以可以记：

```text
throw
 ↓
寻找 catch
 ↓
找到？
 ├── 是 → 执行 catch
 │
 └── 否
      ↓
   继续向外层
      ↓
   仍然没有
      ↓
std::terminate()
```

---

# 十一、把 1.3 和 1.4 连起来

现在你应该能把前两节串起来了：

```text
                 throw
                   ↓
             异常产生
                   ↓
        当前函数正常流程终止
                   ↓
             开始栈展开
                   ↓
       析构已经构造完成的局部对象
                   ↓
         向调用链外层寻找 catch
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
     找到匹配               没找到
        ↓                     ↓
   执行对应 catch          继续向外找
                              ↓
                         最终仍没有
                              ↓
                       std::terminate()
```

而同一个 `try` 里的 `catch`：

```cpp
catch (具体类型)
catch (另一个具体类型)
catch (基类)
catch (...)
```

通常按照：

```text
具体
 ↓
更宽泛
 ↓
...
 ↓
catch(...)
```

来安排。

---

# 十二、这一小节你重点记这几个结论

| 知识点          | 核心结论                                |
| ------------ | ----------------------------------- |
| 基本匹配         | `throw` 的异常类型与 `catch` 进行匹配         |
| 查找顺序         | 同一个 `try` 中从上到下寻找                   |
| 匹配成功         | 执行第一个匹配的 `catch`，后面的不再检查            |
| `catch(...)` | 可以匹配任意异常，通常放最后                      |
| 继承关系         | 派生类异常可以被合适的基类引用捕获                   |
| 捕获对象         | 实际开发中通常使用 `const T&`                |
| 找不到          | 一直向外层寻找，最终找不到会导致 `std::terminate()` |

### 最后用一道小题检查你是否真的理解

```cpp
class Exception {};
class FileException : public Exception {};

try
{
    throw FileException();
}
catch (const Exception& e)
{
    cout << "1" << endl;
}
catch (const FileException& e)
{
    cout << "2" << endl;
}
catch (...)
{
    cout << "3" << endl;
}
```

输出是：

```text
1
```

原因不是 `FileException` 变成了 `Exception`，而是**异常匹配时，第一个 `catch(const Exception&)` 已经能够匹配这个派生类对象，所以匹配成功后就停止继续寻找。**

因此正确顺序应该是：

```cpp
catch (const FileException& e)
{
    cout << "FileException" << endl;
}
catch (const Exception& e)
{
    cout << "Exception" << endl;
}
catch (...)
{
    cout << "Unknown" << endl;
}
```

下一小节就是 **1.5「异常重新抛出」**。这一节会开始涉及一个很实际的问题：**如果当前函数能够发现异常，但自己处理不了，怎么办？能不能“接住之后再扔出去”？**答案就是 `throw;`，而且这里有一个非常重要的 `throw;` 与 `throw e;` 的区别。

# 1.5
好，继续讲 **1.5 异常重新抛出**。这一节的核心其实就一个问题：**一个函数捕获到了异常，但它自己处理不了，怎么办？**答案就是：**捕获 → 做一部分处理 → 再把异常交给更外层处理**，这就是“异常重新抛出”。

# 1.5 异常重新抛出

## 一、为什么需要“重新抛出”？

先看一个场景：

```cpp
void Func()
{
    try
    {
        throw 10;
    }
    catch (int e)
    {
        cout << "Func发现了异常" << endl;
    }
}
```

这里 `Func()` 已经把异常捕获了。

但是假设 `Func()` 只是负责**记录日志**，并没有能力真正处理这个异常，那么直接：

```cpp
catch (int e)
{
    cout << "记录异常日志" << endl;
}
```

就把异常“吃掉”了。

外层调用者根本不知道发生过异常。

所以我们可能希望：

```text
异常产生
 ↓
Func捕获
 ↓
Func记录日志
 ↓
Func重新抛出
 ↓
外层继续处理
```

这就是**异常重新抛出**。

---

# 二、最基本的重新抛出：`throw;`

来看代码：

```cpp
void Func()
{
    try
    {
        throw 10;
    }
    catch (int e)
    {
        cout << "Func捕获异常：" << e << endl;

        throw;
    }
}

int main()
{
    try
    {
        Func();
    }
    catch (int e)
    {
        cout << "main再次捕获：" << e << endl;
    }
}
```

执行过程：

```text
Func()
 ↓
throw 10
 ↓
Func中的catch捕获
 ↓
输出：Func捕获异常：10
 ↓
throw;
 ↓
异常重新向外抛出
 ↓
main中的catch捕获
 ↓
输出：main再次捕获：10
```

最终：

```text
Func捕获异常：10
main再次捕获：10
```

这里最重要的是：

```cpp
throw;
```

它表示：

> **把当前正在处理的异常原封不动地重新抛出去。**

---

# 三、`throw;` 和 `throw e;` 是完全一样的吗？

**不是。这个是本节最重要的知识点之一。**

假设：

```cpp
try
{
    throw 10;
}
catch (int e)
{
    throw;
}
```

这里：

```cpp
throw;
```

表示：

> **重新抛出当前正在处理的原异常。**

而：

```cpp
catch (int e)
{
    throw e;
}
```

表示：

> **重新抛出变量 `e`。**

虽然这个简单例子中看起来结果一样，但在涉及**继承体系**时就可能出现重要区别。

---

# 四、为什么 `throw e;` 有可能出问题？

看一个经典例子：

```cpp
class Exception
{
public:
    virtual const char* what() const
    {
        return "Exception";
    }
};

class FileException : public Exception
{
public:
    const char* what() const override
    {
        return "FileException";
    }
};
```

然后：

```cpp
try
{
    throw FileException();
}
catch (const Exception& e)
{
    cout << e.what() << endl;

    throw;
}
```

这里最开始抛出的是：

```text
FileException
```

虽然：

```cpp
catch (const Exception& e)
```

使用基类引用接住了它，但是**原来的异常对象本身仍然是 `FileException` 类型**。

所以：

```cpp
throw;
```

重新抛出之后，仍然是原来的：

```text
FileException
```

这就是 `throw;` 非常重要的地方。

---

# 五、如果改成 `throw e;` 呢？

```cpp
try
{
    throw FileException();
}
catch (const Exception& e)
{
    throw e;
}
```

这里的 `e` 的静态类型是：

```cpp
const Exception&
```

所以：

```cpp
throw e;
```

抛出的会按照 `Exception` 类型重新构造异常对象。

这可能导致**派生类信息丢失，也就是对象切片（slicing）**。

简单理解：

```text
原始异常：
FileException
     ↓
catch(const Exception& e)
     ↓
e只是一个基类引用
     ↓
throw e
     ↓
重新抛出一个Exception
```

而：

```cpp
throw;
```

则是：

```text
原始异常：
FileException
     ↓
catch(const Exception& e)
     ↓
throw;
     ↓
仍然是原来的FileException异常
```

所以一个非常重要的经验：

> **如果你的目的只是把当前异常继续向外传递，使用 `throw;`，不要写成 `throw e;`。**

---

# 六、一个更直观的例子

```cpp
class Base
{
public:
    virtual void Print() const
    {
        cout << "Base" << endl;
    }
};

class Derive : public Base
{
public:
    void Print() const override
    {
        cout << "Derive" << endl;
    }
};
```

第一种：

```cpp
try
{
    throw Derive();
}
catch (const Base& e)
{
    e.Print();

    throw;
}
```

第一次：

```cpp
e.Print();
```

由于虚函数：

```text
Derive
```

然后：

```cpp
throw;
```

原来的 `Derive` 异常继续向外传递。

而如果：

```cpp
catch (const Base& e)
{
    e.Print();

    throw e;
}
```

那么重新抛出时可能发生切片，外层接收到的异常类型就不再保持原来的派生类类型。

所以：

```cpp
throw;
```

和：

```cpp
throw e;
```

**千万不要认为只是写法不同。**

---

# 七、重新抛出最常见的使用场景

实际开发中经常出现这种结构：

```cpp
void Func()
{
    try
    {
        // 可能发生异常的代码
    }
    catch (const exception& e)
    {
        // 当前层做一些处理
        cout << "记录日志：" << e.what() << endl;

        // 当前层无法彻底解决
        throw;
    }
}
```

外层：

```cpp
int main()
{
    try
    {
        Func();
    }
    catch (const exception& e)
    {
        // 最终处理
        cout << "最终处理：" << e.what() << endl;
    }
}
```

这就形成了一种**分层处理异常**的思路：

```text
底层函数
 ↓
发现异常
 ↓
底层catch
 ↓
记录日志 / 清理资源 / 添加上下文
 ↓
throw;
 ↓
上层catch
 ↓
最终处理
```

这个思想在大型项目里很重要。

---

# 八、`throw;` 只能在 `catch` 里面使用

例如：

```cpp
int main()
{
    throw;
}
```

这种写法是不对的。

因为：

```cpp
throw;
```

的含义是：

> **重新抛出当前正在处理的异常。**

如果当前根本没有正在处理的异常，那么就没有东西可以重新抛。

所以：

```cpp
catch (...)
{
    throw;
}
```

是合理的。

而：

```cpp
void Func()
{
    throw;
}
```

就没有正常的“当前异常”可以重新抛出。

你现在记住：

> **`throw;` 是“重新抛出当前异常”，必须处于异常处理过程中。**

---

# 九、重新抛出并不一定要重新抛给 `main`

例如：

```cpp
void C()
{
    try
    {
        throw 10;
    }
    catch (int e)
    {
        cout << "C处理" << endl;
        throw;
    }
}

void B()
{
    try
    {
        C();
    }
    catch (int e)
    {
        cout << "B处理" << endl;
        throw;
    }
}

int main()
{
    try
    {
        B();
    }
    catch (int e)
    {
        cout << "main处理" << endl;
    }
}
```

执行：

```text
C处理
B处理
main处理
```

异常经历了：

```text
C
 ↓ throw;
B
 ↓ throw;
main
 ↓ catch
```

这就是异常可以**逐层向上传递**。

---

# 十、一个特别容易犯的错误：捕获之后什么都不做

例如：

```cpp
try
{
    Func();
}
catch (const exception& e)
{
    // 什么都不做
}
```

这相当于：

> **异常被捕获以后直接被吃掉。**

当然，某些场景确实需要这样处理，但不能无脑这么做。

比如：

```cpp
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

如果当前层已经能够彻底处理异常，那么可以结束。

但如果：

```text
当前层只能发现异常
不能解决异常
```

那么通常应该考虑：

```cpp
catch (...)
{
    // 当前层处理一部分
    throw;
}
```

---

# 十一、把这一节和前面几节串起来

现在你已经学了：

```text
1.1 异常概念
       ↓
1.2 异常抛出和捕获
       ↓
1.3 栈展开
       ↓
1.4 查找匹配的处理代码
       ↓
1.5 异常重新抛出
```

完整流程已经可以画成：

```text
函数执行
  ↓
发生异常
  ↓
throw
  ↓
寻找匹配的catch
  ↓
栈展开
  ↓
析构局部对象
  ↓
进入catch
  ↓
当前层能解决？
 ├── 能 → 处理完成
 │
 └── 不能
      ↓
    throw;
      ↓
   继续向外层寻找
      ↓
   上层catch处理
```

所以你现在应该能理解一个很重要的设计思想：

> **异常不一定由“发现异常”的函数最终处理。底层函数可以负责发现和报告，上层函数负责决定怎么处理。**

---

# 十二、`throw;` vs `throw e;` 总结

| 写法           | 含义          | 是否保持原异常类型  | 常见用途             |
| ------------ | ----------- | ---------- | ---------------- |
| `throw;`     | 重新抛出当前异常    | **保持**     | 向上层继续传递异常        |
| `throw e;`   | 抛出 `e` 这个对象 | **可能发生切片** | 确实需要重新构造/改变异常对象时 |
| `throw xxx;` | 抛出一个新的异常对象  | 取决于 `xxx`  | 抛出新的异常           |

**你现在最应该形成的习惯：**

```cpp
catch (const exception& e)
{
    // 做一些当前层的事情

    throw;   // 继续向上抛原异常
}
```

而不要在单纯“重新向上抛”的场景下写：

```cpp
catch (const exception& e)
{
    throw e;
}
```

---

## 这一节的核心总结

> **异常重新抛出 = 当前层捕获异常后，发现自己无法彻底处理，于是继续把异常交给上层。**
>
> **`throw;` = 原封不动地重新抛出当前异常，这是最重要的写法。**
>
> **`throw e;` = 重新抛出 `e`，涉及继承关系时可能发生切片，因此不能简单等同于 `throw;`。**

下一块就是 **1.6 异常安全问题 + 1.7 异常规范**。这两节开始从“会使用异常”进入“**怎样正确地设计异常代码**”。其中异常安全会和你之前学过的**构造/析构、资源管理、RAII**再次联系起来，这部分对以后写 C++ 后端很有价值。


# 1.6

好，继续。按照你这份目录，接下来是 **1.6 异常安全问题 → 1.7 异常规范**。这两节我一起讲，因为它们分别解决两个问题：**异常发生时，程序的数据和资源是否还安全？一个函数到底允许抛出什么异常？**

# 1.6 异常安全问题

前面我们已经知道：

```cpp
try
{
    // ...
}
catch (...)
{
    // ...
}
```

能够处理异常；也知道异常发生时会进行**栈展开**，自动调用已经构造完成的局部对象的析构函数。

但是，这还不代表我们的程序就是“异常安全”的。

所谓**异常安全**，核心就是：

> **程序发生异常以后，不能因为异常导致资源泄漏、数据损坏、对象处于不可用状态等问题。**

---

## 一、最简单的资源泄漏问题

例如：

```cpp
void Func()
{
    int* p = new int[100];

    // 中间发生异常
    throw 10;

    delete[] p;
}
```

执行：

```cpp
throw 10;
```

之后，下面的：

```cpp
delete[] p;
```

根本不会执行。

于是：

```text
new
 ↓
p指向资源
 ↓
throw
 ↓
异常退出
 ↓
delete[]没有执行
 ↓
内存泄漏
```

这就是典型的**异常安全问题**。

---

# 二、为什么 RAII 能解决这个问题？

这正好和我们上一节讲的栈展开联系起来。

不要直接使用裸指针：

```cpp
void Func()
{
    int* p = new int[100];

    throw 10;

    delete[] p;
}
```

而是让一个对象管理这个资源：

```cpp
void Func()
{
    vector<int> v(100);

    throw 10;
}
```

当异常发生：

```text
throw
 ↓
栈展开
 ↓
v析构
 ↓
vector自动释放内部资源
```

所以现代 C++非常强调：

> **资源尽量交给对象管理，而不是手动管理。**

这就是 RAII 在异常安全中的重要作用。

你以后学：

```cpp
unique_ptr
shared_ptr
lock_guard
fstream
vector
string
```

都会反复看到这个思想。

---

# 三、异常安全不仅仅是“不能内存泄漏”

例如我们有一个简单的动态数组：

```cpp
class Vector
{
public:
    void push_back(int x)
    {
        // 扩容
        // 开辟新空间
        // 拷贝旧数据
        // 释放旧空间
        // 更新指针
    }
};
```

假设扩容过程中：

```text
旧空间
 ↓
申请新空间
 ↓
拷贝数据
 ↓
第5个元素拷贝时发生异常
```

如果代码设计不好，就可能出现：

```text
旧数据丢失
+
新空间没有释放
+
对象内部指针指向错误位置
```

最终：

> **异常发生以后，这个对象甚至不能正常使用了。**

所以异常安全实际上还涉及：

* 资源不能泄漏
* 数据不能损坏
* 对象状态不能失效
* 操作失败以后应该处于什么状态

---

# 四、异常安全通常可以理解成几个层次

这里你不需要死背标准定义，先理解三个层次。

## ① 基本保证（Basic Guarantee）

发生异常之后：

> **对象仍然处于有效状态，没有资源泄漏。**

例如：

```cpp
obj.push_back(x);
```

失败了，虽然数据可能发生了一些变化，但是：

```text
对象仍然有效
资源没有泄漏
程序可以继续运行
```

这就是比较基本的异常安全保证。

---

## ② 强保证（Strong Guarantee）

更进一步：

> **如果操作发生异常，那么程序状态就像这个操作从来没有发生过一样。**

例如：

```cpp
obj.insert(x);
```

如果插入成功：

```text
旧状态 → 新状态
```

如果失败：

```text
旧状态 → 仍然是旧状态
```

可以理解成：

```text
操作成功
    ↓
提交修改

操作失败
    ↓
回滚
```

这就是所谓的**强异常安全保证**。

---

## ③ 不抛异常保证（No-Throw Guarantee）

最强的一类：

> **这个操作保证不会抛出异常。**

例如：

```cpp
void Func() noexcept
{
    // 保证不抛异常
}
```

当然，`noexcept` 我们马上会讲。

你可以先形成这样一个层次：

```text
基本保证
    ↓
不泄漏资源，对象仍然有效

强保证
    ↓
失败后状态保持不变

不抛异常保证
    ↓
保证这个操作不会抛异常
```

---

# 五、为什么“强保证”很难？

看一个简单例子：

```cpp
void Change()
{
    a = 10;
    b = 20;
    c = 30;
}
```

如果：

```text
a修改成功
b修改成功
c修改时发生异常
```

此时：

```text
a = 10
b = 20
c = 原来的值
```

对象就处于“修改了一半”的状态。

如果你想实现强保证，就需要设计成：

```text
先准备新的状态
      ↓
所有操作成功
      ↓
一次性提交
```

类似：

```cpp
NewState tmp;

// 在 tmp 上进行操作
// 如果失败，tmp自动销毁

// 全部成功
// 再让原对象进入新状态
```

这也是 C++中非常重要的设计思想：

> **先准备，再提交。**

你以后实现 `vector`、`string`、智能指针、容器等东西时，会经常遇到异常安全问题。

---

# 六、异常安全和你之前学的拷贝构造也有关系

例如：

```cpp
class String
{
public:
    String(const char* str)
    {
        _str = new char[strlen(str) + 1];

        // ...
    }

private:
    char* _str;
};
```

假设构造过程中：

```cpp
_str = new char[100];
```

成功了，但是后面的某一步发生异常。

如果资源没有被正确管理：

```text
new成功
 ↓
异常
 ↓
构造函数没有完成
 ↓
资源泄漏
```

所以现代 C++设计中，通常尽量让资源由对象管理。

这也是为什么你后面学 STL 时，会发现：

```cpp
vector
string
unique_ptr
shared_ptr
```

这些类的设计都非常强调资源生命周期。

---

# 七、一个非常重要的结论

所以：

> **异常安全 ≠ “写了 try-catch 就安全”。**

这是初学者非常容易产生的误解。

例如：

```cpp
try
{
    int* p = new int[100];

    throw 10;

    delete[] p;
}
catch (...)
{
}
```

虽然异常被捕获了：

```text
异常被处理
```

但是：

```text
p指向的内存
```

仍然可能泄漏。

真正的异常安全来自：

> **合理的资源管理 + 正确的对象状态设计 + 必要的异常处理。**

而其中最重要的手段之一就是：

> **RAII。**

---

# 1.7 异常规范

接下来进入：

> **异常规范（Exception Specification）**

这个概念主要是用来描述：

> **一个函数可能抛出什么异常，或者保证自己不抛异常。**

不过这里一定要注意：**C++历史上有两套不同的异常规范机制。**

---

# 一、早期 C++ 的异常规范：`throw(类型)`

以前可以这样写：

```cpp
void Func() throw(int, double);
```

它表示：

> `Func()` 可能抛出 `int` 或 `double` 类型的异常。

例如：

```cpp
void Func() throw(int)
{
    throw 10;
}
```

表示这个函数声明允许：

```cpp
throw int;
```

---

# 二、还可以写 `throw()`

例如：

```cpp
void Func() throw();
```

早期 C++中表示：

> **这个函数不允许抛出异常。**

所以：

```cpp
void Func() throw()
{
    throw 10;
}
```

就违反了它的异常规范。

---

# 三、但是现在不要把 `throw(type)` 当成现代 C++的推荐写法

这一点非常重要。

早期 C++有：

```cpp
void Func() throw(int);
```

但是这种动态异常规范后来被认为设计存在很多问题。

C++11 引入了：

```cpp
noexcept
```

现代 C++主要使用：

```cpp
void Func() noexcept;
```

表示：

> **这个函数承诺不会抛出异常。**

所以你现在学习的时候，可以简单理解成：

```text
老式异常规范
throw(int)
throw(double)
throw()
     ↓
现代 C++
noexcept
```

---

# 四、`noexcept` 是什么？

例如：

```cpp
void Func() noexcept
{
    cout << "Hello" << endl;
}
```

它表达的是：

> **Func() 不应该抛出异常。**

如果：

```cpp
void Func() noexcept
{
    throw 10;
}
```

那么问题就严重了。

程序违反了 `noexcept` 承诺，最终会调用：

```cpp
std::terminate()
```

也就是说：

```text
noexcept函数
 ↓
发生异常
 ↓
异常无法正常继续传播
 ↓
std::terminate()
```

因此：

> **`noexcept` 不是“捕获异常”，而是对函数行为做出的“不抛异常”承诺。**

---

# 五、为什么需要 `noexcept`？

这就涉及 C++的性能和程序设计。

例如一个对象的移动构造：

```cpp
class String
{
public:
    String(String&& s) noexcept
    {
        // 转移资源
    }
};
```

如果移动构造明确保证不会抛异常，STL在某些场景下就可以更放心地使用移动操作。

例如 `vector` 扩容时，需要把旧空间中的元素转移到新空间。

如果移动构造：

```cpp
noexcept
```

那么容器通常可以更放心地进行移动。

这就是为什么你以后看 STL 源码时，经常看到：

```cpp
noexcept
```

尤其是：

```cpp
move constructor
move assignment
swap
destructor
```

等函数。

---

# 六、`noexcept` 还可以带条件

例如：

```cpp
void Func() noexcept(true)
{
}
```

等价于：

```cpp
void Func() noexcept
{
}
```

也可以：

```cpp
void Func() noexcept(false)
{
}
```

表示这个函数**允许抛异常**。

所以：

```cpp
noexcept(true)
```

相当于：

```cpp
noexcept
```

而：

```cpp
noexcept(false)
```

表示不承诺不抛异常。

实际开发中最常见的是：

```cpp
void Func() noexcept;
```

---

# 七、析构函数为什么通常应该不抛异常？

这个知识点和前面的栈展开直接联系起来。

假设：

```cpp
void Func()
{
    A a;

    throw 10;
}
```

现在异常发生：

```text
throw 10
 ↓
开始栈展开
 ↓
a析构
```

如果：

```cpp
~A()
{
    throw 20;
}
```

那么就出现：

```text
原异常
 ↓
栈展开
 ↓
析构函数又抛异常
```

也就是：

> **一个异常正在传播的过程中，又出现了另一个异常。**

这种情况非常危险。

因此现代 C++中，析构函数通常应该保证：

```text
不抛异常
```

这也是为什么你以后经常看到：

```cpp
~A() noexcept
{
}
```

---

# 八、异常规范和函数指针

这一部分你现在不需要深入，但是知道一个概念即可。

`noexcept` 属于函数类型的一部分。

例如：

```cpp
void Func() noexcept;
```

和：

```cpp
void Func();
```

在现代 C++中并不是完全相同的函数类型。

不过你现在刚开始学习异常，这部分暂时不用深入。

---

# 九、`noexcept` 的一个实用判断：`noexcept(...)`

还有一种写法：

```cpp
noexcept(Func())
```

它不是在声明函数，而是在**判断一个表达式是否保证不抛异常**。

例如：

```cpp
cout << noexcept(Func()) << endl;
```

如果 `Func()` 是：

```cpp
void Func() noexcept;
```

那么：

```cpp
noexcept(Func())
```

结果就是：

```text
true
```

如果：

```cpp
void Func();
```

则通常为：

```text
false
```

这个东西以后学习**模板、移动构造、泛型编程**时会非常常见。

---

# 十、把“异常规范”这一节整理成一张表

| 写法                            | 含义               | 现代 C++中的情况       |
| ----------------------------- | ---------------- | ---------------- |
| `void Func()`                 | 没有 `noexcept` 承诺 | 可以抛异常            |
| `void Func() throw(int)`      | 允许特定类型异常         | **旧式机制，不推荐使用**   |
| `void Func() throw()`         | 旧式“不抛异常”         | 已被 `noexcept` 取代 |
| `void Func() noexcept`        | 保证不抛异常           | **现代 C++常用**     |
| `void Func() noexcept(false)` | 不保证不抛异常          | 可以抛              |
| `noexcept(Func())`            | 判断表达式是否不抛异常      | 模板/STL中常见        |

---

# 十一、把 1.6 和 1.7 连起来

现在你已经把这一部分完整串起来了：

```text
1.6 异常安全
      ↓
异常发生之后
      ↓
资源不能泄漏
对象不能进入不可用状态
      ↓
RAII 是重要解决方案

1.7 异常规范
      ↓
描述函数的异常行为
      ↓
旧式 throw(type)
      ↓
现代 C++主要使用 noexcept
      ↓
明确告诉程序：
“这个函数保证不抛异常”
```

你可以把这两节浓缩成：

> **异常安全解决“发生异常以后怎么办，如何保证程序仍然可靠”；异常规范解决“一个函数对于异常做什么承诺”。**

---

# 这一大块的重点总结

到现在，你的 **1.1～1.7「异常的概念及使用」** 就全部学完了：

| 小节                | 核心内容                   |
| ----------------- | ---------------------- |
| **1.1 异常的概念**     | 异常是一种错误处理机制            |
| **1.2 异常的抛出和捕获**  | `try / throw / catch`  |
| **1.3 栈展开**       | 异常向外传播，沿途析构局部对象        |
| **1.4 查找匹配的处理代码** | 按规则寻找匹配的 `catch`       |
| **1.5 异常重新抛出**    | `throw;` 原异常继续向外传播     |
| **1.6 异常安全问题**    | 保证资源、数据、对象状态安全；RAII很重要 |
| **1.7 异常规范**      | 现代 C++主要使用 `noexcept`  |

其中你现在最应该牢牢记住的是这一条主线：

```text
throw
 ↓
异常产生
 ↓
寻找匹配 catch
 ↓
栈展开
 ↓
析构局部对象
 ↓
进入 catch
 ↓
能处理 → 结束
不能处理 → throw;
 ↓
继续向外传播
```

以及两个非常容易混淆的点：

```cpp
throw;       // 重新抛出原异常
throw e;     // 抛出 e，继承体系中可能发生切片
```

```cpp
noexcept     // 函数承诺不抛异常
```

**下一部分就是目录中的「2. 标准库的异常」**。这一部分会开始进入真正的 C++标准库异常体系：`exception`、`logic_error`、`runtime_error`、`out_of_range`、`invalid_argument`、`bad_alloc` 等，以及你以后在 STL 中实际遇到的异常。这个部分和你已经学过的 STL 联系会比较紧。

# 2

好，接下来进入目录的 **2. 标准库的异常**。这一部分和前面最大的区别是：前面我们是在学习**异常机制本身怎么工作**，现在开始学习 **C++标准库已经帮我们定义好的异常类型**。这部分其实不难，重点是理解它们之间的**继承体系**，以及知道什么时候会遇到它们。

# 2. 标准库的异常

## 一、为什么需要标准库异常？

前面我们自己可以写：

```cpp
throw 10;
```

也可以：

```cpp
throw "error";
```

甚至自己定义：

```cpp
class MyException
{
    // ...
};
```

但是如果每个人都自己定义异常：

```cpp
throw 10;
throw "error";
throw MyException();
throw XXXException();
```

那么大型项目里就会非常混乱。

所以 C++ 标准库提供了一套统一的异常体系。

最核心的一个类就是：

```cpp
std::exception
```

它位于：

```cpp
#include <exception>
```

---

# 二、`std::exception` 是什么？

最基本的使用方式：

```cpp
try
{
    // 可能发生异常的代码
}
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

这里：

```cpp
e.what()
```

是非常重要的。

`exception` 提供了：

```cpp
virtual const char* what() const noexcept;
```

你现在不用纠结完整函数声明，先理解：

> **`what()` 用来获取异常的描述信息。**

例如：

```cpp
try
{
    throw exception();
}
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

---

# 三、为什么 `catch(const exception& e)` 很常见？

这是因为标准库的各种异常，很多都是从：

```text
exception
```

继承下来的。

所以可以：

```cpp
catch (const exception& e)
```

统一捕获很多标准库异常。

例如：

```text
std::exception
     ↑
     ├── logic_error
     ├── runtime_error
     ├── bad_alloc
     └── ...
```

所以：

```cpp
catch (const exception& e)
```

相当于一个比较大的“异常兜底”。

---

# 四、标准库异常的继承体系

这一部分你一定要理解，而不是单纯背类名。

可以先记成：

```text
                    exception
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        logic_error         runtime_error
             │                   │
       ┌─────┼─────┐        ┌────┴────┐
       ↓     ↓     ↓        ↓         ↓
 invalid   out_of  length   overflow  underflow
 argument  _range  error
```

除此之外，还有一些其他标准异常类型：

```text
exception
   ├── logic_error
   │     ├── invalid_argument
   │     ├── out_of_range
   │     ├── length_error
   │     └── domain_error
   │
   ├── runtime_error
   │     ├── range_error
   │     ├── overflow_error
   │     └── underflow_error
   │
   └── bad_alloc
```

具体实现细节和标准版本可能存在一些差异，但你学习这一章时，**先掌握这个继承关系和各异常的语义**即可。

---

# 五、`logic_error` 和 `runtime_error` 怎么区分？

这是标准库异常体系里最重要的一个分类。

## ① `logic_error`

顾名思义：

> **逻辑错误。**

通常表示：

> **程序本身的逻辑/使用方式存在问题。**

例如：

```cpp
vector<int> v;
v.at(100);
```

下标越界属于程序使用容器的方式有问题。

常见的：

```cpp
invalid_argument
out_of_range
length_error
domain_error
```

都属于这一类。

---

## ② `runtime_error`

表示：

> **运行过程中发生的错误。**

也就是说，这类错误通常不是简单地说“代码逻辑写错了”，而是运行环境、运行条件等导致的问题。

例如：

```cpp
runtime_error
```

以及：

```cpp
range_error
overflow_error
underflow_error
```

属于这一类。

你现在可以简单记：

```text
logic_error
    ↓
程序使用/逻辑方面的问题

runtime_error
    ↓
运行过程中出现的问题
```

不过注意：

> **不要把它理解成绝对严格的“编译前错误 vs 运行时错误”。**

这是标准库对异常语义的一种分类，而不是说 `logic_error` 一定能在编译期发现。

---

# 六、`invalid_argument`

这个异常表示：

> **函数接收到一个不合法的参数。**

例如：

```cpp
void Func(int x)
{
    if (x < 0)
    {
        throw invalid_argument("x不能小于0");
    }
}
```

使用：

```cpp
try
{
    Func(-10);
}
catch (const invalid_argument& e)
{
    cout << e.what() << endl;
}
```

这里：

```cpp
-10
```

虽然是合法的 `int`，但是对于 `Func()` 的业务要求来说，它是一个**无效参数**。

所以：

```cpp
invalid_argument
```

就是：

> **参数类型没问题，但参数的值不符合要求。**

---

# 七、`out_of_range`

这个你以后使用 STL 时会非常常见。

例如：

```cpp
vector<int> v = {1, 2, 3};

cout << v.at(10) << endl;
```

这里：

```cpp
v.at(10)
```

超出了合法范围。

`vector::at()` 会抛出：

```cpp
std::out_of_range
```

例如：

```cpp
try
{
    vector<int> v = {1, 2, 3};

    cout << v.at(10) << endl;
}
catch (const out_of_range& e)
{
    cout << e.what() << endl;
}
```

所以：

> **`out_of_range` = 访问的下标、位置等超出了允许范围。**

注意一个 STL 细节：

```cpp
v.at(10);
```

会进行范围检查。

而：

```cpp
v[10];
```

**不会以抛出 `out_of_range` 的方式进行范围检查。**

所以你以后看到：

```cpp
vector::at()
```

就应该联想到：

```text
范围检查
↓
越界
↓
out_of_range
```

---

# 八、`length_error`

这个异常表示：

> **对象的长度超过了允许的范围。**

例如某些 STL 容器操作，如果请求的大小超过容器允许的最大范围，就可能抛出：

```cpp
length_error
```

你可以把它和：

```cpp
out_of_range
```

区分开：

```text
out_of_range
    ↓
访问的位置超了

length_error
    ↓
对象本身要求的长度/容量超了
```

例如：

```text
vector访问第100个元素
↓
out_of_range
```

而：

```text
试图创建一个超过容器允许最大长度的对象
↓
length_error
```

---

# 九、`domain_error`

这个你在实际项目中遇到的频率相对低一些。

它表示：

> **参数虽然类型正确，但不属于这个操作允许的数学/逻辑定义域。**

例如某个函数要求：

```text
x > 0
```

你传入：

```text
x = -1
```

就可能使用：

```cpp
throw domain_error("...");
```

你可以简单理解：

```text
invalid_argument
    ↓
参数不符合函数要求

domain_error
    ↓
参数超出了某个操作的合法定义域
```

两者在实际设计中有一定语义重叠，所以你现在不需要纠结得特别细。

---

# 十、`runtime_error`

然后来看：

```cpp
runtime_error
```

它表示：

> **运行过程中出现的错误。**

例如：

```cpp
void Connect()
{
    if (连接失败)
    {
        throw runtime_error("连接服务器失败");
    }
}
```

然后：

```cpp
try
{
    Connect();
}
catch (const runtime_error& e)
{
    cout << e.what() << endl;
}
```

这种异常和：

```cpp
invalid_argument
```

的区别就比较明显：

```text
invalid_argument
↓
你传的参数不对

runtime_error
↓
运行过程中发生了问题
```

---

# 十一、`overflow_error` 和 `underflow_error`

这两个名字你应该很好理解。

### `overflow_error`

表示：

> **计算结果超出了能够表示的范围。**

例如某些数值计算场景。

```text
数值太大
 ↓
超过表示范围
 ↓
overflow_error
```

### `underflow_error`

表示：

> **计算结果出现下溢。**

简单理解：

```text
数值太接近表示范围的下限
 ↓
underflow
```

这两个都属于：

```cpp
runtime_error
```

---

# 十二、`bad_alloc`

这个异常非常重要，因为你以后写 C++一定可能遇到。

例如：

```cpp
int* p = new int[100000000000000];
```

如果系统无法满足内存分配请求，`new` 默认可能抛出：

```cpp
std::bad_alloc
```

例如：

```cpp
try
{
    int* p = new int[100000000000000];
}
catch (const bad_alloc& e)
{
    cout << e.what() << endl;
}
```

所以：

> **`bad_alloc` = 动态内存分配失败。**

它是：

```cpp
std::exception
```

体系中的一个重要异常。

这和你之前学过的：

```cpp
new
```

直接相关。

---

# 十三、标准库异常最大的价值是什么？

你现在应该已经发现一个特点：

我们可以统一这样写：

```cpp
try
{
    // STL代码
}
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

因为很多标准库异常都继承自：

```cpp
exception
```

所以：

```text
out_of_range
      ↓
logic_error
      ↓
exception
```

以及：

```text
runtime_error
      ↓
exception
```

都可以被：

```cpp
catch (const exception& e)
```

捕获。

这就是**多态 + 异常继承体系**结合起来的应用。

---

# 十四、为什么推荐 `const exception&`？

你前面已经学过：

```cpp
catch (const Exception& e)
```

这里再次出现：

```cpp
catch (const exception& e)
```

原因完全一样：

**① 引用避免拷贝**

```cpp
catch (exception e)
```

可能产生对象拷贝。

而：

```cpp
catch (const exception& e)
```

不需要复制整个对象。

**② `const` 表示我们只读取异常信息**

一般只是：

```cpp
e.what()
```

并不需要修改异常对象。

**③ 能保持多态**

例如：

```cpp
catch (const exception& e)
```

可以捕获派生类异常。

---

# 十五、实际使用中最常见的写法

以后你看到：

```cpp
try
{
    // ...
}
catch (const exception& e)
{
    cerr << e.what() << endl;
}
```

应该立刻知道它是什么意思：

```text
try
 ↓
执行可能产生标准异常的代码
 ↓
发生异常
 ↓
exception体系中的异常
 ↓
catch(const exception&)
 ↓
e.what()
 ↓
获得错误描述
```

例如：

```cpp
try
{
    vector<int> v = {1, 2, 3};

    cout << v.at(100) << endl;
}
catch (const exception& e)
{
    cout << "发生异常：" << e.what() << endl;
}
```

这里真正抛出的是：

```cpp
out_of_range
```

但我们使用：

```cpp
catch (const exception& e)
```

也能接住。

---

# 十六、如果想针对不同异常分别处理呢？

当然也可以：

```cpp
try
{
    vector<int> v = {1, 2, 3};

    cout << v.at(100) << endl;
}
catch (const out_of_range& e)
{
    cout << "数组越界：" << e.what() << endl;
}
catch (const exception& e)
{
    cout << "其他标准异常：" << e.what() << endl;
}
```

注意这里的顺序：

```text
具体
 ↓
out_of_range
 ↓
exception
```

**派生类必须放在基类前面。**

否则：

```cpp
catch (const exception& e)
```

先匹配成功，后面的：

```cpp
catch (const out_of_range& e)
```

就永远不会执行。

这正好对应我们上一节学习的**异常匹配规则**。

---

# 十七、你可以把整个标准异常体系记成这张图

```text
                    std::exception
                          │
             ┌────────────┴────────────┐
             │                         │
             ↓                         ↓
       std::logic_error          std::runtime_error
             │                         │
      ┌──────┼──────┐           ┌──────┼──────┐
      ↓      ↓      ↓           ↓      ↓      ↓
 invalid   out_of  length      range  overflow underflow
 argument  range   error       error   error    error
```

另外还有：

```text
std::exception
      │
      └── std::bad_alloc
```

你目前不用把所有异常类背得滚瓜烂熟，**先把继承关系 + 使用场景建立起来**。

---

# 十八、这一部分最重要的几个异常

| 异常                 | 含义          | 典型场景              |
| ------------------ | ----------- | ----------------- |
| `exception`        | 所有标准异常的基类之一 | 统一捕获              |
| `logic_error`      | 逻辑/使用方式相关错误 | 程序逻辑问题            |
| `invalid_argument` | 参数不合法       | 函数收到不符合要求的参数      |
| `out_of_range`     | 超出合法范围      | `vector::at()` 越界 |
| `length_error`     | 长度超过允许范围    | 容器长度请求过大          |
| `domain_error`     | 超出合法定义域     | 数学/逻辑定义域问题        |
| `runtime_error`    | 运行过程中发生的问题  | 运行环境/运行条件导致的问题    |
| `overflow_error`   | 数值溢出        | 计算结果过大            |
| `underflow_error`  | 数值下溢        | 计算结果过小            |
| `bad_alloc`        | 内存分配失败      | `new` 分配失败        |

---

# 十九、这一节你真正需要记住什么？

不要现在去死背十几个异常类。你先形成下面这个思维：

```text
标准库异常
    ↓
exception
    ↓
不同的派生异常
    ↓
根据错误性质选择对应异常
```

例如：

```cpp
throw invalid_argument("参数错误");
```

表示：

> “你给我的参数不符合要求。”

```cpp
throw out_of_range("下标越界");
```

表示：

> “你访问的位置超出了合法范围。”

```cpp
throw runtime_error("连接失败");
```

表示：

> “程序运行过程中发生了错误。”

```cpp
new ...
   ↓
内存分配失败
   ↓
bad_alloc
```

而上层如果不关心具体是哪一种：

```cpp
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

就可以统一处理。

---

## 总结

**这一部分的核心不是背异常类，而是理解标准库已经建立了一套异常继承体系：**

```text
std::exception
├── logic_error
│   ├── invalid_argument
│   ├── out_of_range
│   ├── length_error
│   └── domain_error
│
├── runtime_error
│   ├── range_error
│   ├── overflow_error
│   └── underflow_error
│
└── bad_alloc
```

其中你现阶段尤其要记住：

```cpp
vector.at()
    ↓
out_of_range
```

以及：

```cpp
new
    ↓
分配失败
    ↓
bad_alloc
```

还有最常见的统一捕获方式：

```cpp
catch (const exception& e)
{
    cout << e.what() << endl;
}
```

这实际上把你前面学的**继承、多态、引用、异常捕获**全部串起来了。

下一部分如果按照这份目录继续，应该进入 **3. 自定义异常体系**。这一部分就会从“使用标准库异常”进入“**我们自己设计一个异常系统**”，尤其适合结合你以后写的 C++ 后端项目来理解。

