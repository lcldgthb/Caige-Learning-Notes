# vector 01 vector的使用，后面再讲vector的实现
vector，中文：向量
vector的构造，遍历，加例子
reserve与string 不同！！
对于reserve()小于capacity时
string :
vs2022 不缩，g++4.8,会缩
vector，都不缩
void test_vector1()
{
	vector<int> v1;
	vector<int> v2(10, 1);

	vector<int> v3(++v2.begin(), --v2.end());

	for (size_t i = 0; i < v3.size(); i++)
	{
		cout << v3[i] << " ";
	}
	cout << endl;

	vector<int>::iterator it = v3.begin();
	while (it != v3.end())
	{
		cout << *it << " ";
		++it;
	}
	cout << endl;

	for (auto e : v3)
	{
		cout << e << " ";
	}
	cout << endl;
}


void TestVectorExpand()
{
	size_t sz;
	vector<int> v;
	v.reserve(100);

	sz = v.capacity();
	cout << "capacity changed: " << sz << '\n';

	cout << "making v grow:\n";
	for (int i = 0; i < 100; ++i)
	{
		v.push_back(i);
		if (sz != v.capacity())
		{
			sz = v.capacity();
			cout << "capacity changed: " << sz << '\n';
		}
	}
}

void test_vector2()
{
	//TestVectorExpand();

	vector<int> v(10, 1);
	v.reserve(20);
	cout << v.size() << endl;
	cout << v.capacity() << endl;

	v.reserve(15);
	cout << v.size() << endl;
	cout << v.capacity() << endl;

	v.reserve(5);
	cout << v.size() << endl;
	cout << v.capacity() << endl;
}

void test_vector3()
{
	//TestVectorExpand();

	vector<int> v(10, 1);
	v.reserve(20);
	cout << v.size() << endl;
	cout << v.capacity() << endl;

	v.resize(15, 2);
	cout << v.size() << endl;
	cout << v.capacity() << endl;

	v.resize(25, 3);
	cout << v.size() << endl;
	cout << v.capacity() << endl;

	v.resize(5);
	cout << v.size() << endl;
	cout << v.capacity() << endl;
}
### 总结：vector 的基本使用、构造与 reserve、resize
- vector 本质：vector 是一种动态顺序表（动态数组），底层使用连续内存存储元素，支持随机访问和自动扩容。
- 与 string 的关系：两者设计思想高度一致，都具有 size()、capacity()、reserve()、resize()、push_back() 等接口，可以将 string 看作是面向字符的特殊动态序列（思想类似，而不是继承关系）。
- 构造方式：支持默认构造、指定元素个数和值构造、区间构造，其中 STL 的区间均遵循 左闭右开 [first, last) 的规则。
- 遍历方式：支持下标遍历、迭代器遍历和 C++11 范围 for 遍历，其中迭代器是 STL 的统一访问方式，后续所有容器和算法都会大量使用。
- reserve()：只负责调整容量（capacity），不会改变元素个数（size），并且只能扩容，不能缩容。
- resize()：负责调整元素个数（size），当元素增多且空间不足时会自动扩容；当元素减少时，仅修改 size，通常不会缩小 capacity。
- 牢记区别：reserve 管的是预留空间，resize 管的是实际元素数量，这是学习 vector 最容易混淆、也是最重要的知识点之一。

# vector 02 接口
operater[],at,
insert,eraser，只支持迭代器。
vector的比较
为什么不能用vector<char>代替string，string的优势！
vector除了int，double等，还可以存，自定义类，string，vector（二维数组）等等
void test_vector4()
{
	vector<int> v(10, 1);
	v.push_back(2);
	v.insert(v.begin(), 0);

	for (auto e : v)
	{
		cout << e << " ";
	}
	cout << endl;

	v.insert(v.begin()+3, 10);

	for (auto e : v)
	{
		cout << e << " ";
	}
	cout << endl;

	vector<int> v1(5, 0);
	for (size_t i = 0; i < 5; i++)
	{
		cin >> v1[i];
	}

	for (auto e : v1)
	{
		cout << e << ",";
	}
	cout << endl;

	vector<char> v2;
	string s2;
	// \0

	vector<int> v3;
	// send(s2.c_str())
}

void test_vector5()
{
	vector<string> v1;
	string s1("xxxx");
	v1.push_back(s1);

	v1.push_back("yyyyy");
	for (const auto& e : v1)
	{
		cout << e << " ";
	}
	cout << endl;

	// ά
	// 10*5
	vector<int> v(5, 1);
	vector<vector<int>> vv(10, v);
	vv[2][1] = 2;
	// vv.operator[](2).operator[](1) = 2;
	for (size_t i = 0; i < vv.size(); i++)
	{
		for (size_t j = 0; j < vv[i].size(); ++j)
		{
			cout << vv[i][j] << " ";
		}
		cout << endl;
	}
	cout << endl;
}

//template<class T>
//class vector
//{
//	T& operator[](int i)
//	{
//		assert(i < _size);
//
//		return _a[i];
//	}
//private:
//	T* _a;
//	size_t _size;
//	size_t _capacity;
//};

// vector<int>
//class vector
//{
//	int& operator[](int i)
//	{
//		assert(i < _size);
//
//		return _a[i];
//	}
//private:
//	int* _a;
//	size_t _size;
//	size_t _capacity;
//};
//
//// vector<vector<int>>
//class vector
//{
//	vector<int>& operator[](int i)
//	{
//		assert(i < _size);
//
//		return _a[i];
//	}
//private:
//	vector<int>* _a;
//	size_t _size;
//	size_t _capacity;
//};

### 总结：vector 常用接口与设计思想
operator[] 与 at()：两者都用于访问元素，operator[] 速度快但通常不进行越界检查；at() 会进行边界检查，越界时抛出 std::out_of_range 异常，更安全。
insert() 与 erase()：都以迭代器作为位置参数，这是 STL 为了统一所有容器接口而设计的。由于底层需要移动元素，因此在 vector 中时间复杂度通常为 O(n)。
vector 支持比较运算：支持 ==、!=、<、<=、>、>= 等运算，其中 < 等关系运算采用字典序比较。
不能完全用 vector<char> 替代 string：vector<char> 可以存放字符，但不会自动维护 '\0'，缺少丰富的字符串操作接口，也没有许多 string 实现中的专门优化（如 SSO），因此 string 更适合表示和处理文本。
本节体现的 STL 思想：模板实现泛型、迭代器统一访问方式、运算符重载提升易用性、容器隐藏底层实现细节，这些思想贯穿整个 STL。

# vector 03 二维数组
二维数组，本质
模版实例化了两个类，一个是vector<int>,一个是vector<vector<int>>

算法题:杨辉三角
1,C语言的实现：指针数组，malloc
2，vector二维数组

## 本节总结：vector 二维数组
vector<vector<int>> 本质是 外层 vector 存放多个 vector<int> 对象，并不是一整块连续的二维内存。
模板会实例化两个类：vector<int> 和 vector<vector<int>>。
vv[i] 返回 vector<int>&，vv[i][j] 再调用一次 operator[]，最终返回 int&，因此支持直接赋值。
vv[i][j] 等价于 vv.operator[](i).operator[](j)。
杨辉三角的核心规律是：首尾为 1，中间元素 = 上一行相邻两个元素之和，实现时注意访问上一行应使用 ret[i-2]，这是最容易出错的地方。

# 03 实现
候捷老师，老师建议我们可以看书，跟着老师学习，独立思考和解决问题能力不足，
学习C++推荐的三本书
STL源码剖析，
C++Prinmer
C++effective

简单看一下源码：
先看类，看变量，看构造函数
三个指针，start,finsh,end_of_storage;
未来工作，都要靠自己，所以要提升思考能力，解决问题能力，学习能力，搜索能力，工程文件之间类联系比较大，所以，比较难，但要培养自己这方面的能力。
当前阶段不建议看太多，能力还不够！

## 本节总结：STL源码学习（03）——初识 STL 源码与学习方法
学习 STL 源码的目的不是背代码，而是学习优秀类的设计思想，理解容器为什么这样实现。
推荐阅读三本经典书籍：《STL源码剖析》《C++ Primer》《Effective C++》，分别侧重底层实现、语言基础和编程实践。
阅读源码时遵循 "先看类 → 再看成员变量 → 再看构造函数 → 最后看成员函数" 的顺序，不要一开始陷入模板细节。
vector 的核心成员变量通常是三个指针：start、finish、end_of_storage，它们分别表示数据起始位置、有效数据结束位置和整个存储空间结束位置。
当前阶段不必强行阅读完整 STL 源码，应先掌握容器使用和简化实现，再逐步阅读真实源码。
比阅读源码更重要的是培养程序员的核心能力：独立思考能力、解决问题能力、持续学习能力、搜索能力以及阅读大型工程代码的能力。这些能力才是未来学习新技术和参与实际项目开发的基础。

# 04，自己实现vector
## template
template<class T>
	void print_vector(const vector<T>& v)
	{
		// 规定，没有实例化的类模板里面取东西，编译器不能区分这里const_iterator
		// 是类型还是静态成员变量
		//typename vector<T>::const_iterator it = v.begin();
## 迭代器失效问题：
insert和erase函数：不同平台有所不同，但是记住，调用完函数还想用迭代器，必须要先更新！
	// insert以后p就是失效，不要直接访问，要访问就要更新这个失效的迭代器的值
			//v.insert(p, 40);
			//(*p) *= 10;

代码：
#pragma once
#include<assert.h>

namespace bit
{
	template<class T>
	class vector
	{
	public:
		typedef T* iterator;
		typedef const T* const_iterator;

		iterator begin()
		{
			return _start;
		}

		iterator end()
		{
			return _finish;
		}

		const_iterator begin() const
		{
			return _start;
		}

		const_iterator end() const
		{
			return _finish;
		}

		void reserve(size_t n)
		{
			if (n > capacity())
			{
				size_t old_size = size();
				T* tmp = new T[n];
				memcpy(tmp, _start, size() * sizeof(T));
				delete[] _start;

				_start = tmp;
				_finish = tmp + old_size;
				_end_of_storage = tmp + n;
			}
		}

		size_t size() const
		{
			return _finish - _start;
		}

		size_t capacity() const
		{
			return _end_of_storage - _start;
		}

		bool empty()
		{
			return _start == _finish;
		}

		void push_back(const T& x)
		{
			// 扩容
			if (_finish == _end_of_storage)
			{
				reserve(capacity() == 0 ? 4 : capacity() * 2);
			}

			*_finish = x;
			++_finish;
		}

		void pop_back()
		{
			assert(!empty());
			--_finish;
		}

		iterator insert(iterator pos, const T& x)
		{
			// 扩容
			if (_finish == _end_of_storage)
			{
				size_t len = pos - _start;
				reserve(capacity() == 0 ? 4 : capacity() * 2);
				pos = _start + len;
			}

			iterator end = _finish - 1;
			while (end >= pos)
			{
				*(end + 1) = *end;
				--end;
			}
			*pos = x;

			++_finish;

			return pos;
		}

		T& operator[](size_t i)
		{
			assert(i < size());

			return _start[i];
		}

		const T& operator[](size_t i) const
		{
			assert(i < size());

			return _start[i];
		}

	private:
		iterator _start = nullptr;
		iterator _finish = nullptr;
		iterator _end_of_storage = nullptr;
	};

	/*void print_vector(const vector<int>& v)
	{
		vector<int>::const_iterator it = v.begin();
		while (it != v.end())
		{
			cout << *it << " ";
			++it;
		}
		cout << endl;

		for (auto e : v)
		{
			cout << e << " ";
		}
		cout << endl;
	}*/

	template<class T>
	void print_vector(const vector<T>& v)
	{
		// 规定，没有实例化的类模板里面取东西，编译器不能区分这里const_iterator
		// 是类型还是静态成员变量
		//typename vector<T>::const_iterator it = v.begin();
		auto it = v.begin();
		while (it != v.end())
		{
			cout << *it << " ";
			++it;
		}
		cout << endl;

		for (auto e : v)
		{
			cout << e << " ";
		}
		cout << endl;
	}

	void test_vector1()
	{
		vector<int> v;
		v.push_back(1);
		v.push_back(2);
		v.push_back(3);
		v.push_back(4);
		v.push_back(5);

		for (size_t i = 0; i < v.size(); i++)
		{
			cout << v[i] << " ";
		}
		cout << endl;

		vector<int>::iterator it = v.begin();
		while (it != v.end())
		{
			cout << *it << " ";
			++it;
		}
		cout << endl;

		for (auto e : v)
		{
			cout << e << " ";
		}
		cout << endl;

		print_vector(v);

		vector<double> vd;
		vd.push_back(1.1);
		vd.push_back(2.1);
		vd.push_back(3.1);
		vd.push_back(4.1);
		vd.push_back(5.1);

		print_vector(vd);
	}

	void test_vector2()
	{
		vector<int> v;
		v.push_back(1);
		v.push_back(2);
		v.push_back(3);
		v.push_back(4);
		//v.push_back(5);

		print_vector(v);

		v.insert(v.begin() + 2, 30);
		print_vector(v);

		int x;
		cin >> x;
		auto p = find(v.begin(), v.end(), x);
		if (p != v.end())
		{
			// insert以后p就是失效，不要直接访问，要访问就要更新这个失效的迭代器的值
			//v.insert(p, 40);
			//(*p) *= 10;

			p = v.insert(p, 40);
			(*(p+1)) *= 10;
		}
		print_vector(v);
	}
}

## 八、本次知识点总结
operator[] 返回的是元素引用（T&），不是指针。
_start 是指向动态数组首元素的指针，而不是数组名，但可以像数组一样使用 []。
p[i] 本质等价于 *(p+i)。
p+1 表示移动 1 个元素，编译器会自动乘 sizeof(T)。
STL（vector、string、算法、迭代器等）中的指针运算，全部都是以元素为单位，而不是字节为单位。
实现模板类时，要始终牢记 T 可能是任意类型，不能按内置类型的思维去实现。
## 总结
# 04 自己实现 vector（二）总结

## 1. 模板（Template）

- 模板的本质是**类型参数化**，一份代码可以支持任意数据类型。
- `template<class T>` 中的 `T` 是类型占位符，实例化时由编译器替换为具体类型。
- 类模板和函数模板都只有在实例化时才真正生成代码。

---

## 2. typename 的作用

在模板中：

```cpp
vector<T>::iterator
```

编译器无法判断 `iterator` 是**类型**还是**静态成员变量**。因此必须写：

```cpp
typename vector<T>::iterator
```
告诉编译器：`iterator` 是一个类型。

现代 C++ 更推荐直接使用：

```cpp
auto it = v.begin();
```

利用自动类型推导，避免书写 `typename`。

---

## 3. vector 迭代器本质

模拟实现中：

```cpp
typedef T* iterator;
```

因此：

- `begin()` 返回 `_start`
- `end()` 返回 `_finish`

本质就是普通指针。

---

## 4. insert 导致迭代器失效

发生扩容时：

```
旧空间 -> delete
新空间 -> 重新申请
```
原来的迭代器仍指向旧空间，成为野指针。
即使没有扩容，插入元素后原位置元素发生移动，原迭代器的语义也可能改变。

因此：

```cpp
it = insert(it, value);
```
不要继续使用旧迭代器。
---

## 5. erase 导致迭代器失效

删除元素后：

```
后面的元素整体前移
```

原来的迭代器已经不再表示原来的元素。

STL 的 `erase` 返回：

```
删除元素下一个位置的新迭代器
```

推荐写法：

```cpp
it = erase(it);
```

---

## 6. insert 中为什么保存下标

扩容后：

```
_start
```

发生改变。

原来的：

```
pos
```

已经失效。

因此：

```cpp
size_t len = pos - _start;
reserve(...);
pos = _start + len;
```

利用偏移量恢复新的迭代器位置。

---

## 7. 易错点总结

- 模板中依赖类型必须加 `typename`。
- `auto` 可以代替复杂的迭代器类型。
- `insert`、`erase` 后不要继续使用旧迭代器。
- `reserve` 后所有指向原空间的指针、引用、迭代器都会失效。
- `vector` 的迭代器本质就是指针，因此指针失效的问题同样适用于迭代器。
- 
# 05 拷贝，构造拷贝相关问题
默认构造，，拷贝构造，operate=，析构
迭代器区间构造（函数模版）
类模版里面还可以定义函数模版，意义，
n个相同的value构造
代码：
// C++11 前置生成默认构造
		vector() = default;

		vector(const vector<T>& v)
		{
			reserve(v.size());
			for (auto& e : v)
			{
				push_back(e);
			}
		}

// 类模板的成员函数，还可以继续是函数模版
		template <class InputIterator>
		vector(InputIterator first, InputIterator last)
		{
			while (first != last)
			{
				push_back(*first);
				++first;
			}
		}

		vector(size_t n, const T& val = T())
		{
			reserve(n);
			for (size_t i = 0; i < n; i++)
			{
				push_back(val);
			}
		}

		vector(int n, const T& val = T())
		{
			reserve(n);
			for (int i = 0; i < n; i++)
			{
				push_back(val);
			}
		}
		void clear()
		{
			_finish = _start;
		}

		// v1 = v3
		/*vector<T>& operator=(const vector<T>& v)
		{
			if (this != &v)
			{
				clear();

				reserve(v.size());
				for (auto& e : v)
				{
					push_back(e);
				}
			}

			return *this;
		}*/

		void swap(vector<T>& v)
		{
			std::swap(_start, v._start);
			std::swap(_finish, v._finish);
			std::swap(_end_of_storage, v._end_of_storage);
		}

		// v1 = v3
		//vector& operator=(vector v)
		vector<T>& operator=(vector<T> v)
		{
			swap(v);

			return *this;
		}

		~vector()
		{
			if (_start)
			{
				delete[] _start;
				_start = _finish = _end_of_storage = nullptr;
			}
		}

# 总结
# 05 拷贝、构造相关问题总结

## 1. 对象生命周期四大函数

一个类最重要的四个成员函数：

- 默认构造函数（Default Constructor）
- 拷贝构造函数（Copy Constructor）
- 赋值运算符重载（operator=）
- 析构函数（Destructor）

它们共同管理对象从创建到销毁的整个生命周期。

---

## 2. 默认构造（C++11）

```cpp
vector() = default;
```

表示让编译器自动生成默认构造函数。

如果成员已经使用默认成员初始化（如 `iterator _start = nullptr;`），通常无需手写默认构造。

---

## 3. 拷贝构造

```cpp
vector(const vector<T>& v)
{
    reserve(v.size());
    for (auto& e : v)
        push_back(e);
}
```

实现的是**深拷贝**。

不能直接复制指针，否则多个对象会共享同一块空间，析构时发生重复释放（Double Free）。

为了兼容任意类型 `T`，不要使用 `memcpy`，而应通过 `push_back` 或元素赋值完成复制。

---

## 4. 类模板中的函数模板

```cpp
template<class InputIterator>
vector(InputIterator first, InputIterator last);
```

这是**类模板中的函数模板**。

`T` 决定容器中存储的数据类型，而 `InputIterator` 决定区间来源。

因此不仅可以接收 `vector` 的迭代器，还可以接收数组、`list`、`set`、`string` 等任意符合输入迭代器要求的区间。

---

## 5. n 个相同元素构造

```cpp
vector(size_t n, const T& value = T());
```

表示构造包含 `n` 个元素的 `vector`，每个元素初始化为 `value`。

默认值 `T()` 表示调用类型 `T` 的默认构造函数。

---

## 6. clear()

```cpp
void clear()
{
    _finish = _start;
}
```

`clear()` 只删除元素，不释放空间。

调用后：

- `size() == 0`
- `capacity()` 保持不变

方便后续继续插入元素而无需重新申请内存。

---

## 7. Copy-and-Swap（拷贝交换法）

```cpp
vector<T>& operator=(vector<T> v)
{
    swap(v);
    return *this;
}
```

执行过程：

1. 参数按值传递，调用拷贝构造生成副本。
2. 当前对象与副本交换内部资源。
3. 临时副本析构，自动释放旧资源。

优点：

- 自动处理自赋值（`v = v`）
- 异常安全
- 实现简单，代码复用性高

---

## 8. swap()

```cpp
void swap(vector<T>& v)
{
    std::swap(_start, v._start);
    std::swap(_finish, v._finish);
    std::swap(_end_of_storage, v._end_of_storage);
}
```

成员函数可以直接访问其他同类型对象的 `private` 成员，因为 **private 是类级别权限，而不是对象级别权限**。

---

## 9. 析构函数

```cpp
~vector()
{
    delete[] _start;
    _start = _finish = _end_of_storage = nullptr;
}
```

负责释放动态申请的空间，防止内存泄漏。

---

## 10. 易错点总结

- 拷贝构造必须深拷贝，不能直接复制指针。
- `operator=` 必须返回 `*this`，支持连续赋值。
- `clear()` 不释放空间，只修改 `_finish`。
- 区间构造应使用函数模板，不能限定为 `vector::iterator`。
- Copy-and-Swap 的参数必须按值传递，而不是 `const&`。
- `swap()` 可以直接访问其他同类型对象的私有成员。

---

## 11. 与 string 的联系

`vector` 与 `string` 的底层设计思想完全一致：

- 都管理一块连续的动态空间。
- 都需要实现深拷贝。
- 都需要实现 `reserve()`、`clear()`、`swap()`、析构函数等资源管理接口。
- 都遵循 RAII（资源获取即初始化）的设计思想，保证资源的正确申请与释放。

# 总结2
## 4.1 InputIterator 是什么？

```cpp
template<class InputIterator>
vector(InputIterator first, InputIterator last);
```

`InputIterator` **不是 STL 提供的类，也不是关键字**，它只是一个普通的模板参数名，可以任意修改，例如：

```cpp
template<class It>
vector(It first, It last);

template<class Iterator>
vector(Iterator first, Iterator last);
```

都完全合法。

之所以命名为 `InputIterator`，是因为 STL 中规定了 **Input Iterator（输入迭代器）** 这一类迭代器，属于一种语义化命名。

模板实例化时：

- 数组：`InputIterator` → `int*`
- `vector`：`InputIterator` → `vector<int>::iterator`
- `list`：`InputIterator` → `list<int>::iterator`
- `string`：`InputIterator` → `string::iterator`

因此，只要支持 `*`、`++`、`!=` 等迭代器操作，就可以作为区间构造的参数。

---

## 5.1 为什么 `vector<int> v(10,1)` 容易产生歧义？

类中同时存在：

```cpp
vector(size_t n, const T& value = T());

template<class InputIterator>
vector(InputIterator first, InputIterator last);
```

当写：

```cpp
vector<int> v(10,1);
```

时，编译器既可以理解为：

```cpp
vector(size_t, const int&)
```

表示 **创建 10 个值为 1 的元素**；

也可以把模板推导为：

```cpp
InputIterator = int

↓

vector(int, int)
```

误认为这是区间构造。

为了减少这种匹配歧义，一些实现会额外提供：

```cpp
vector(int n, const T& value = T());
```

让 `vector(10,1)` 优先匹配普通构造函数。

现代 STL 通常使用 `enable_if` 或 `concept` 限制模板参数必须是真正的迭代器，从根本上解决这个问题，而不是依赖重载。
# 06 memcpy的浅拷贝问题


	vector<string> v;
		v.push_back("11111111111111111111");
		v.push_back("11111111111111111111");
		v.push_back("11111111111111111111");
		v.push_back("11111111111111111111");
		print_container(v);

		v.push_back("11111111111111111111");
		print_container(v);


		void reserve(size_t n)
		{
			if (n > capacity())
			{
				size_t old_size = size();
				T* tmp = new T[n];
		memcpy(tmp, _start, old_size * sizeof(T));//浅拷贝
这里会出错，不能用memcpy，要深拷贝
# 总结
# 06 memcpy 的浅拷贝问题

## 1. 为什么 `memcpy` 在 `vector<int>` 中没问题？

对于 `int`、`char`、`double` 等基本类型，数据本身就是对象的全部内容。

例如：

```text
1 2 3 4
```

`memcpy` 只是把这些字节完整复制过去，因此不会出错。

---

## 2. 为什么 `vector<string>` 会崩溃？

`string` 对象内部维护着一块动态申请的字符数组：

```text
string对象
 ├── char* _str
 ├── size
 └── capacity
```

`memcpy` 只会复制 `_str` 指针的值，不会重新申请字符数组。

结果就是：

```text
旧string ----\
              ---> 同一块字符数组
新string ----/
```

两个对象共享同一块资源，这就是**浅拷贝**。

析构时两个对象都会释放这块空间，最终导致：

- 野指针（Dangling Pointer）
- 重复释放（Double Free）
- 程序崩溃

---

## 3. 正确做法

不要使用：

```cpp
memcpy(tmp, _start, old_size * sizeof(T));
```

而应逐个元素赋值：

```cpp
for (size_t i = 0; i < old_size; ++i)
{
    tmp[i] = _start[i];
}
```

这样：

- `int` 调用普通赋值。
- `string` 调用 `string::operator=`，自动完成深拷贝。
- 任意类型 `T` 都可以正确工作。

---

## 4. `new T[n]` 做了什么？

```cpp
T* tmp = new T[n];
```

会先调用 `T` 的默认构造函数，构造出 `n` 个对象。

随后：

```cpp
tmp[i] = _start[i];
```

调用的是赋值运算符（`operator=`），而不是拷贝构造。

---

## 5. `memcpy` 什么时候可以使用？

可以用于**平凡类型（Trivially Copyable）**：

- `int`
- `char`
- `double`
- `long`
- 仅包含基本类型成员的简单结构体

不能用于管理资源的类，例如：

- `std::string`
- `std::vector`
- `std::list`
- 自己实现的 `string`
- 自己实现的 `vector`

这些类型必须进行深拷贝。

---

## 6. 如何快速判断能否使用 `memcpy`？

一个经验法则：

> **如果一个类需要自己实现析构函数、拷贝构造函数或赋值运算符（Rule of Three），就不要使用 `memcpy` 去复制对象。**

因为这类对象通常管理着动态资源，需要进行深拷贝。

---

## 7. 与前面 `string` 的联系

在实现 `string::reserve()` 时：

```cpp
char* tmp = new char[n + 1];
strcpy(tmp, _str);
```

复制的是 **char 数组**，属于基本类型，因此没有问题。

而 `vector<T>` 中的 `T` 是模板参数，可能是 `string`、`vector` 等复杂类型，因此不能使用 `memcpy`，必须逐个元素赋值，保证调用对象自身的深拷贝逻辑。


# vector总结
这是根据我们整个对话中**所有关于 `vector` 模拟实现**整理出来的知识点。我没有展开解释，只保留结论和容易错的地方，尽量做到**完整、不遗漏**。建议你以后每实现一个容器，都整理这样一份"避坑总结"。

---

# vector 模拟实现——知识点 & 易错点总结

## 一、vector 底层结构

* `vector` 底层采用一块连续的动态数组实现。
* `vector` 维护三个迭代器（指针）：`_start`、`_finish`、`_end_of_storage`。
* `_start` 指向数据起始位置。
* `_finish` 指向最后一个元素的下一个位置（end）。
* `_end_of_storage` 指向整块空间末尾的下一个位置。
* `size()` 返回的是元素个数，而不是空间大小。
* `capacity()` 返回的是已申请空间可容纳的元素个数。
* `empty()` 判断 `_start == _finish`。

---

# 二、模板相关

* `template<class T>` 决定容器中存储的数据类型。
* 类模板中还可以继续定义函数模板。
* `template<class InputIterator>` 中的 `InputIterator` 只是模板参数名，不是 STL 类型，也不是关键字。
* `InputIterator` 可以改成任意合法名字，如 `It`、`Iterator`。
* 区间构造体现了 STL 泛型思想，只要求支持 `*`、`++`、`!=` 等迭代器操作即可。

---

# 三、reserve()

* `reserve()` 只扩容，不改变 `size()`。
* `reserve()` 扩容前应判断 `n > capacity()`。
* 扩容前必须先保存原来的 `size()`。
* 扩容完成后 `_finish` 应恢复到原来的位置。
* `_end_of_storage = _start + capacity`。
* 扩容后原来的迭代器全部失效。
* `new T[n]` 已经调用了 `T` 的默认构造函数。
* `delete[] tmp` 不能写，因为 `_start` 已经接管了这块空间。
* **不能使用 `memcpy` 拷贝任意 `T`。**
* `reserve()` 应逐个元素赋值，调用对象自己的赋值运算符。
* `memcpy` 只能用于平凡类型（如 `int`），不能用于 `string`、`vector` 等管理资源的类。

---

# 四、resize()

* `resize()` 会修改 `size()`。
* `resize()` 缩小时只需要移动 `_finish`。
* `resize()` 扩大时可能需要先扩容。
* 新增元素使用 `value` 初始化，而不是固定赋值 `0`。
* `while (_finish - _start < n)` 比较的是元素个数。
* `resize()` 不会改变已有元素。

---

# 五、push_back()

* 当 `_finish == _end_of_storage` 时需要扩容。
* 扩容策略一般采用 2 倍扩容，空容器第一次扩为 4。
* 插入元素位置是 `*_finish`。
* 插入完成后 `_finish++`。
* 不要写成 `finish++`，成员变量是 `_finish`。

---

# 六、pop_back()

* `pop_back()` 前必须判空。
* 删除元素本质上就是 `_finish--`。
* 不需要真正释放空间。

---

# 七、operator[]

* 返回类型必须是 `T&`。
* 返回的是元素，不是地址。
* `return _start[i]` 等价于 `*(_start + i)`。
* `return _start + i` 返回的是 `T*`，类型错误。
* 指针支持 `[]` 运算符，本质就是地址偏移再解引用。
* 指针加减单位是元素，不是字节。
* 不需要乘 `sizeof(T)`。

---

# 八、insert()

* `insert()` 的 `pos` 是迭代器，不是下标。
* 插入位置是在当前元素之前。
* 判断合法范围应为 `pos >= _start && pos <= _finish`。
* 扩容前必须保存下标 `index = pos - _start`。
* 扩容后原来的 `pos` 已失效，需要重新计算。
* 数据移动方向必须从后向前。
* 插入完成后 `_finish++`。
* 返回值应为插入元素的迭代器。
* 不要返回 `this`。

---

# 九、erase()

* `erase()` 删除的是当前迭代器指向的元素。
* 删除方式是后面的元素整体向前覆盖。
* 数据移动方向是从前向后。
* `_finish--` 即完成删除。
* 返回值应为删除位置后的新迭代器。
* `erase(begin())` 可以删除第一个元素。
* 删除最后一个元素时返回 `end()`。

---

# 十、迭代器

* `iterator` 本质就是 `T*`。
* `const_iterator` 本质就是 `const T*`。
* `begin()` 返回 `_start`。
* `end()` 返回 `_finish`。
* `end()` 不指向最后一个元素，而是最后元素的下一个位置。
* 插入、扩容、删除都可能导致迭代器失效。
* 调用 `insert()` 后继续使用旧迭代器属于未定义行为。
* 调用 `erase()` 后原位置及其后的迭代器全部失效。
* 使用 `insert()` 返回值更新迭代器。

---

# 十一、拷贝构造

* 拷贝构造不能直接 `swap()`。
* `const vector&` 无法作为 `swap()` 参数交换资源。
* 正确做法是重新申请空间，再逐个元素拷贝。
* 可以利用 `push_back()` 实现拷贝构造。
* 拷贝构造应保证深拷贝。

---

# 十二、operator=

* 推荐采用现代写法（Copy-Swap）。
* 参数采用值传递：`vector<T> v`。
* 利用拷贝构造生成副本。
* 再调用 `swap()` 完成资源交换。
* 自动解决自赋值问题。
* 最后返回 `*this`。
* 不要忘记写 `return *this`。

---

# 十三、swap()

* `swap()` 参数必须是引用。
* `swap()` 只交换三个指针。
* 同一个类的成员函数可以访问其他对象的私有成员。
* 不需要通过 `begin()` 等接口交换。
* 使用 `std::swap()` 分别交换三个成员。

---

# 十四、构造函数

* 默认构造可直接使用 `= default`。
* `vector(size_t n, const T& value)` 构造 `n` 个相同元素。
* 区间构造属于函数模板。
* `vector(int n, ...)` 是为了避免与区间构造发生模板匹配歧义。
* 区间构造支持数组、`list`、`set`、`string` 等所有符合输入迭代器要求的类型。

---

# 十五、模板实现

* 模板的声明和定义必须放在同一个头文件。
* 模板不能像普通函数一样分离到 `.cpp`。
* 模板只有实例化时才真正生成代码。

---

# 十六、memcpy 浅拷贝问题

* `memcpy` 只复制字节，不复制资源。
* `string` 内部包含指针，`memcpy` 会造成浅拷贝。
* 浅拷贝会导致多个对象共享同一块资源。
* 最终会发生野指针、重复释放（Double Free）等问题。
* `vector<T>` 中不能假设 `T` 是基本类型。
* 模板代码必须对所有合法类型都正确。

---

# 十七、老师重点强调

* **迭代器失效是 STL 面试高频考点。**
* **模板不是为了支持一种类型，而是为了支持所有符合要求的类型。**
* **不要使用 `memcpy` 处理拥有资源管理能力的类。**
* **扩容后一定要重新计算迭代器。**
* **写模板时不要假设 `T` 一定是 `int`。**
* **优先复用已经实现好的成员函数（如拷贝构造利用 `push_back()`），减少重复代码。**

---

# 十八、我在实现 vector 时最常犯的错误（⭐⭐⭐⭐⭐）

* 把 **迭代器当成下标** 使用。
* 忘记 **扩容后迭代器失效**。
* `operator[]` 返回了指针而不是引用。
* 混淆 **`size()` 与 `capacity()`** 的含义。
* 忘记保存扩容前的 `size()`。
* `resize()` 新元素固定赋值 `0`，没有使用 `value`。
* `push_back()` 中成员变量写成 `finish` 而不是 `_finish`。
* `insert()` 返回 `this` 而不是插入位置迭代器。
* `erase()` 返回错误的迭代器。
* 想在拷贝构造中直接使用 `swap()`。
* `swap()` 参数没有使用引用。
* 误认为成员函数不能访问其他对象的私有成员。
* 在模板代码中使用 `memcpy` 拷贝对象。
* 忘记模板不能分离编译。
* 对 `InputIterator` 的理解停留在"某种固定类型"，而实际上它只是模板参数名。
