# string 

## 编码（拓展知识）
UTF-8,UTF-16,GBK
两个字节代表一个汉字，basic_string 和string 
wchar 
## 拷贝构造和operater=的现代写法以及意义
void swap(string& s)
		{
			std::swap(_str, s._str);
			std::swap(_size, s._size);
			std::swap(_capacity, s._capacity);
		}

		// s2(s1)
		// 现代写法,(一种思想)
		string(const string& s)
		{
			string tmp(s._str);
			swap(tmp);
		}
    		// s1 = s3;
		//string& operator=(const string& s)
		//{
		//	if (this != &s)
		//	{
		//		//string tmp(s._str);
		//		string tmp(s);

		//		swap(tmp);
		//	}

		//	return *this;
		//}

		// s1 = s3;
		string& operator=(string tmp)
		{
			swap(tmp);

			return *this;
		}
## string里面的swap函数
没有用模版那个而是有一个全局函数std::swap(string s1,string s2)

## 知识总结
这个问题非常重要，也是 **赋值运算符（operator=）** 最经典的面试题之一。

其实只要理解了**自赋值（Self Assignment）**，以后就再也不会忘了。

---

# 为什么传统写法要判断 `if (this != &s)`？

假设有两个对象：

```cpp
string s1("hello");
string s2("world");
```

执行

```cpp
s1 = s2;
```

没有任何问题。

但是还有一种情况：

```cpp
s1 = s1;
```

也就是

> **自己给自己赋值**

此时

```
this == &s
```

因为

```
this
↓

s1
```

而

```
&s

↓

s1
```

它们指向的是同一个对象。

---

# 看传统写法

例如：

```cpp
string& operator=(const string& s)
{
    if (this != &s)
    {
        delete[] _str;

        _size = s._size;
        _capacity = s._capacity;

        _str = new char[_capacity + 1];

        strcpy(_str, s._str);
    }

    return *this;
}
```

看起来没有问题。

但是如果删掉判断：

```cpp
string s("hello");

s = s;
```

会发生什么？

---

## 第一步

此时：

```
this

↓

+---------+
| _str ---|-------> "hello"
+---------+

&s

↓

同一个对象
```

也就是说

```
this->_str
```

和

```
s._str
```

其实就是同一块内存。

---

## 第二步

执行

```cpp
delete[] _str;
```

现在：

```
原来的

"hello"

已经释放了
```

但是注意！

因为

```
s

就是自己
```

所以

```
s._str
```

也指向这块已经释放的内存。

此时变成：

```
this->_str
↓

xxxxx

s._str
↓

xxxxx
```

这是**悬空指针（Dangling Pointer）**。

---

## 第三步

继续执行：

```cpp
_size = s._size;
_capacity = s._capacity;
```

没问题。

因为

```
_size
_capacity
```

只是普通变量。

---

## 第四步

申请新空间：

```cpp
_str = new char[_capacity + 1];
```

现在：

```
this->_str

↓

新空间
```

但是

```
s._str
```

呢？

注意：

由于 `this` 和 `s` 是同一个对象，执行 `_str = new ...` 实际上**也把对象里的 `_str` 成员更新成了新地址**。因此这一步之后：

```
this->_str
↓

新空间

s._str
↓

还是同一个成员

↓

新空间
```

所以**真正的问题并不是这里**。

---

## 第五步

执行：

```cpp
strcpy(_str, s._str);
```

如果是**自赋值**，由于上一步 `_str` 已经更新，`s._str` 和 `_str` 都指向**同一块刚申请但尚未初始化的新内存**。

于是相当于：

```cpp
strcpy(新空间, 新空间);
```

程序不会崩溃，但**原来 `"hello"` 的内容已经在第一步被释放了**，没有任何地方保存它，因此数据已经永久丢失。最后得到的是一块未初始化的数据，行为是**未定义（Undefined Behavior）**。

---

# 所以真正的问题是什么？

很多人误以为是：

> `strcpy` 从已经释放的内存拷贝。

实际上，在这种常见写法里，更准确的问题是：

> **一开始就把自己原来的资源释放了，而源数据正是自己，导致数据丢失，再也无法恢复。**

---

# 为什么加判断就解决了？

```cpp
if (this != &s)
{
    ...
}
```

如果

```cpp
s = s;
```

那么

```
this == &s
```

于是：

```
整个函数什么都不做

直接返回
```

对象保持原样。

---

# Copy-and-Swap 为什么不用判断？

现代写法：

```cpp
string& operator=(string tmp)
{
    swap(tmp);
    return *this;
}
```

例如：

```cpp
s = s;
```

第一步：

参数按值传递：

```cpp
string tmp(s);
```

这里会调用**拷贝构造**，创建出一个**独立的新对象**。

```
s

↓

hello
```

```
tmp

↓

hello（另一块内存）
```

两个对象已经完全分离。

第二步：

```cpp
swap(tmp);
```

交换资源。

第三步：

```cpp
tmp
```

析构。

释放的是

```
原来属于 s 的那块资源
```

而现在 `s` 持有的是副本里的资源，内容仍然是 `"hello"`，整个过程完全正确。

因此：

> **Copy-and-Swap 的核心思想就是：先复制，再交换。真正开始修改当前对象之前，已经有了一份完整、安全的副本，因此天然支持自赋值。**

---

# 为什么现代写法还能保证异常安全？

传统写法：

```cpp
delete[] _str;      // 旧资源没了
_str = new char[...] // 如果这里抛异常
```

对象已经丢失原来的数据。

而现代写法：

```cpp
string tmp(s); // 先复制成功
swap(tmp);     // 再交换
```

如果复制失败（例如 `new` 抛异常），`swap` 根本不会执行，当前对象保持原状，因此满足**强异常安全保证（Strong Exception Guarantee）**。

---

# 总结：为什么传统写法要判断 `if (this != &s)`？

* **目的**：防止对象给自己赋值（自赋值）。
* **原因**：传统实现通常会先释放当前对象持有的资源，再重新申请并复制。如果源对象就是自己，就会先把自己的数据释放掉，导致原始数据丢失，最终产生未定义行为。
* **判断作用**：当 `this == &s` 时直接返回，不进行任何操作，避免资源被错误释放。
* **现代 `Copy-and-Swap` 写法**：参数按值传递，先利用拷贝构造生成一个独立副本，再交换资源，因此**天然支持自赋值**，无需再写 `if (this != &s)` 判断。


## 02
引用计数和写时拷贝（了解即可，可以不听）
vs2022是深拷贝，
linux是写时拷贝。
具体实现是：

总结：引用计数与写时拷贝（Copy-On-Write）
深拷贝：每次拷贝对象都会重新申请一块内存并复制数据，两个对象互不影响，实现简单、安全，也是现代 std::string 的实现方式。
写时拷贝（COW）：多个对象最初共享同一份数据，并通过引用计数记录共享对象数量；只有当某个对象准备修改数据时，才进行真正的深拷贝，因此称为“写时拷贝”。
引用计数：每新增一个共享对象，计数加一；对象析构时计数减一；当计数减为 0 时，才真正释放内存。
COW 的优点：减少不必要的数据复制，在大量只读场景下能够节省时间和内存。
COW 被淘汰的原因：多线程下维护引用计数成本高、所有修改操作都要额外判断、C++11 引入移动语义后复制成本降低，以及现代标准对字符串行为提出了更严格的要求，因此主流 STL 已全面采用深拷贝实现。
需要记住的事实：现代 MSVC、GCC、Clang 的 std::string 都采用深拷贝；写时拷贝主要是历史实现思想。引用计数并没有过时，它仍然是 std::shared_ptr 等智能指针的重要底层机制。
