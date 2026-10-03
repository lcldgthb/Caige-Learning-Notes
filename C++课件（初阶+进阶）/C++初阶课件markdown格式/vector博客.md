

@[TOC](文章目录)
<center>
    <!-- 头像部分，已修正样式解析问题 -->
<img src="https://i-blog.csdnimg.cn/direct/56485b231dde46a1a2ec0480895d4eab.png" style="width: 200px; height: 200px; object-fit: cover; clip-path: circle(50%);">
    <br>
    <!-- 博主信息文字，已修正style分号错误 -->
    <p style="font-size: 18px; font-weight: bold; margin: 10px 0;"><b>
     ◆ 博主： <font color="#ff4d4f"><b>  @此生决int</b></font>
    </b></p>
    <!-- 博主信息文字，已修正style分号错误 -->
 <b>分享编程知识！深挖底层原理！持续原创更新！</b>

</p>
 <br>
 
**热门专栏：**

 <a>[深入理解 C++系列：](https://blog.csdn.net/2502_94353935/category_13191461.html)</a>**从语法入门到底层原理，系统掌握现代 C++**
 <a>[算法系列：](https://blog.csdn.net/2502_94353935/category_13148263.html)</a>**从入门到精通，蓝桥杯、ACM、LeetCode 与面试算法全路线**
<a>[快速复习系列：](https://blog.csdn.net/2502_94353935/category_13135388.html)</a>**知识梳理、查漏补缺，考前冲刺必备**
<a>[Java 速通系列：](https://blog.csdn.net/2502_94353935/category_13190969.html)</a>**已学 C 语言，快速上手 Java，轻松备战期末考试**



</center>
<p style="font-size:16px;color:#666;">
<b>📌 本系列知识点前后关联较强，建议按照专栏顺序阅读哦</b>
</p>



>  **本系列主要面向的阅读人群**
>
> **1，学完 C 语言，准备系统学习 C++ 的同学**
>
> **2，已经学习过 C++，希望重新梳理知识体系的同学**
>
> **3，想深入理解 C++ 设计思想与底层原理，而不仅仅停留在语法层面的同学**

<p style="font-size:16px;color:#666;">
<b>不止教你会写代码，更带你理解代码为什么这样设计！</b>
</p>
---

## 上期回顾

  上一篇我们主要学习了 **（string**，重点掌握了 **string的使用，相关接口，以及底层实现！**。本文更进一步，学习结构类似的vector，正式进入STL的学习。

---
# C++ vector 复习总结





本节主要围绕两个层面展开：

1. **会使用 `std::vector`**
   - 构造、遍历、容量、增删查改、二维 `vector`。
2. **简单模拟实现vector**
   - 扩容机制、迭代器失效、模拟实现时的拷贝问题。



---

## 一、vector 的使用

### 1. vector 是什么？

一句话概括：**`vector` 就是支持动态扩容的数组。**

1，vector 本质：vector 是**一种动态顺序表（动态数组）**，底层使用连续内存存储元素，支持随机访问和自动扩容。
2，与 我们上一期学的string 的关系：**两者设计思想高度一致**，都具有 size()、capacity()、reserve()、resize()、push_back() 等接口，可以将 string 看作是面向字符的特殊动态序列，但二者也有很多不同！
### 2，vector的构造、遍历、


#### vector 的常见构造
构造方式：支持默认构造、指定元素个数和值构造、区间构造，其中 **STL 的区间均遵循 左闭右开 [first, last)** 的规则。

| 构造形式 | 含义 |
|---|---|
| `vector()` | 空 `vector` |
| `vector(n, val)` | 构造 `n` 个 `val` |
| `vector(const vector& x)` | 拷贝构造 |
| `vector(first, last)` | 使用迭代器区间构造 |

示例：

```cpp
vector<int> v1;
vector<int> v2(5, 1);
vector<int> v3(v2);
int a[] = {1, 2, 3, 4};
vector<int> v4(a, a + 4);
```

重点：

- `vector<int>(5, 1)` 表示 5 个元素，每个值是 1。
- 迭代器区间构造非常常用，尤其在数组、字符串、其他容器之间转换时。

---

#### 迭代器与遍历
- 遍历方式：支持下标遍历、迭代器遍历和 C++11 范围 for 遍历，其中迭代器是 STL 的统一访问方式，后续所有容器和算法都会大量使用！
#### 1，迭代器遍历
 1. begin 和 end

```cpp
vector<int> v{1, 2, 3, 4};
for (auto it = v.begin(); it != v.end(); ++it)
{
    cout << *it << " ";
}
```

 2. rbegin 和 rend

```cpp
for (auto rit = v.rbegin(); rit != v.rend(); ++rit)
{
    cout << *rit << " ";
}
```
含义：

- `begin()`：指向第一个元素。
- `end()`：指向**最后一个元素的下一个位置**。
-  `rbegin()`：最后一个元素。
- `rend()`：**第一个元素前一个逻辑位置**。

注意：

> `end()` 不是有效元素位置，不能解引用。

---


### 2. 下标遍历

`vector` 最常用的遍历方式之一：

```cpp
for (size_t i = 0; i < v.size(); ++i)
{
    cout << v[i] << " ";
}
```
---

### 3. 范围 for 遍历

```cpp
for (auto e : v)
{
    cout << e << " ";
}
```

**修改元素时要传引用！**

```cpp
for (auto& e : v)
{
    e *= 2;
}
```

---

### 2，vector 常用接口

常用接口：

| 接口 | 作用 |
|---|---|
| `size()` | 返回当前有效元素个数 |
| `capacity()` | 返回当前容量 |
| `empty()` | 判断容器是否为空 |
| `resize()` | 修改有效元素个数 |
| `reserve()` | 修改容量（预留空间） |
| `operator[]` | 快速访问指定位置元素（不检查越界） |
| `at()` | 访问指定位置元素（会检查越界） |
| `front()` | 返回第一个元素 |
| `back()` | 返回最后一个元素 |
| `push_back()` | 尾部插入元素 |
| `pop_back()` | 删除尾部元素 |
| `insert()` | 在指定位置插入元素 |
| `erase()` | 删除指定位置元素 |
| `clear()` | 清空所有元素 |
| `swap()` | 交换两个 `vector` 的数据 |
---
部分不常用接口
| 接口 | 作用 |
|---|---|
| `assign()` | 用指定内容重新赋值 |
| `begin()` | 返回首元素迭代器 |
| `end()` | 返回尾后迭代器 |
| `rbegin()` | 返回反向首迭代器 |
| `rend()` | 返回反向尾后迭代器 |
| `data()` | 返回底层数组首地址 |
---
细节补充

 1. reserve()：只负责调整容量（capacity），不会改变元素个数（size），并且**只能扩容，不能缩容**。
 2. resize()：负责调整元素个数（size），当元素增多且空间不足时会自动扩容；当元素减少时，仅修改 size，通常不会缩小 capacity。
 3. 牢记区别：**reserve 管的是预留空间，resize 管的是实际元素数量，**
 4. operator[] 与 at()：两者都用于访问元素，operator[] 速度快但通常不进行越界检查；at() 会进行边界检查，越界时抛出 std::out_of_range 异常，更安全。**竞赛用[]，工程用at！**
 5. insert() 与 erase()：都**以迭代器作为位置参数**，这是 STL 为了统一所有容器接口而设计的。由于底层需要移动元素，因此在vector 中时间复杂度通常为 O(n)。
 6. vector 支持比较运算：支持 ==、!=、<、<=、>、>= 等运算，其中 <等关系运算采用字典序比较。
 7. **vector<char> 与 string的比较**

 **不能完全用 vector<char> 替代 string：**
 vector<char> 可以存放字符，但**不会自动维护 '\0'，缺少丰富的字符串操作接口，也没有许多 string 实现中的专门优化**（如 SSO），因此string 更适合表示和处理文本。
 ### vector二维数组
 

```cpp
caige::vector<int> v1(10, 1);
caige::vector<caige::vector<int>> v2(5, v1);
```

 vector<vector<int>> 本质是 **外层 vector 存放多个 vector<int> 对象，并不是一整块连续的二维内存**。**模板会实例化两个类：vector<int> 和 vector<vector<int>>。**
 

```cpp
caige::vector<int> v1(10, 1);
caige::vector<caige::vector<int>> v2(5, v1);
v2[0][0] = 2;
for (int i = 0; i < v2[0].size(); i++)
	for (int j = 0; j < v2.size(); j++)
		v2[i][j] = 10086;
```

vv[i] 返回 vector<int>&，vv[i][j] 再调用一次 operator[]，最终返回 int&，因此支持直接赋值。
vv[i][j] 等价于 vv.operator[](i).operator[](j)。

## 二维数组练习题：杨辉三角⭐⭐

### 题目链接

[杨辉三角](https://leetcode.cn/problems/pascals-triangle/)

---

### 题目描述

给定一个非负整数 `numRows`，生成「杨辉三角」的前 `numRows` 行。

在杨辉三角中，每个数等于它左上方和右上方两个数之和。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b3289e2209af4cfe94b74f2c143f0784.png)


---

### 解题思路

利用杨辉三角的性质逐行构造。前两行固定，从第三行开始，首尾元素为 `1`，中间元素等于上一行相邻两个元素之和，直到生成 `numRows` 行即可。

---

### 解题代码

```cpp
class Solution {
    // 1
    // 1 1
    // 1 2 1
    // 1 3 3 1
    // 1 4 6 4 1
public:
    vector<vector<int>> generate(int numRows) {

        vector<vector<int>> ret;

        // 第一行
        vector<int> tmp1(1, 1);
        ret.push_back(tmp1);

        if (numRows == 1)
            return ret;

        // 第二行
        vector<int> tmp2(2, 1);
        ret.push_back(tmp2);

        if (numRows == 2)
            return ret;

        // 从第三行开始逐行构造
        for (int i = 3; i <= numRows; i++)
        {
            vector<int> tmp(i);

            // 每一行首尾都为 1
            tmp[0] = 1;
            tmp[i - 1] = 1;

            // 中间元素等于上一行相邻两个元素之和
            for (int j = 1; j < i - 1; j++)
            {
                // 注意这里访问的是上一行，即 i-2
                tmp[j] = ret[i - 2][j] + ret[i - 2][j - 1];
            }

            ret.push_back(tmp);
        }

        return ret;
    }
};
```

---

没懂？看看大神的解题代码！！

### 大神解题代码

```cpp
class Solution {
public:
    vector<vector<int>> generate(int numRows) {

        // 先创建 numRows 行，每行长度分别为 1~numRows
        vector<vector<int>> ret(numRows);

        for (int i = 0; i < numRows; i++)
        {
            ret[i].resize(i + 1);

            // 每行首尾元素都是 1
            ret[i][0] = ret[i][i] = 1;

            // 中间元素由上一行两个元素相加得到
            for (int j = 1; j < i; j++)
            {
                ret[i][j] = ret[i - 1][j - 1] + ret[i - 1][j];
            }
        }

        return ret;
    }
};
```

## 二，vector 模拟实现——知识点 & 易错点总结
具体实现见博主的Gitee仓库，博主的Gitee链接：[财哥](https://gitee.com/wealthy-forest-li)
## 一、vector 底层结构

* `vector` 底层采用一块连续的动态数组实现。
* `vector` 维护**三个迭代器（指针）：`_start`**（指向数据起始位置）、**`_finish`**（指向最后一个元素的下一个位置（end））、**`_end_of_storage`**（指向整块空间末尾的下一个位置）。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/80e550a9d05a490b8c58df7ca35ac67e.png)

---

# 二、关于模板

* `template<class T>` 决定容器中存储的数据类型。
* **类模板中还可以继续定义函数模板，（具体见下面的`template<class InputIterator>`实现部分）**。
* 下面的区间构造体现了 STL 泛型思想，只要求支持 `*`、`++`、`!=` 等迭代器操作即可。

---
## 三，重要接口实现


### 1、reserve()⭐️⭐️⭐️

首先，我们要知道：`reserve()` 只扩容，不改变 `size()`。

**坑：**

1. `reserve()` 扩容前应判断 `n > capacity()`。
2. **扩容前必须先保存原来的 `size()`**。
3. **扩容后原来的迭代器全部失效**。所以，扩容完成后 `_finish` 应恢复到原来的位置，`_finish = _start + size`，`_end_of_storage = _start + capacity`。
4. **不能使用 `memcpy` 拷贝任意 `T`。**
5. `memcpy` 只能用于平凡类型（如 `int`），不能用于 `string`、`vector` 等管理资源的类。
6. `reserve()` 应逐个元素赋值，调用对象自己的赋值运算符。

```cpp
void reserve(size_t n)
{
    if (n >capacity())
    {
        size_t old_size = size();
     //   T tmp = new T[n];,注意new出来的要用指针接收
        T* tmp = new T[n];
      //  memcpy(tmp, _start,old_size);注意第三个参数是字节数而不是大小！！
       // memcpy(tmp, _start, old_size*sizeof(T));不能用memcpy，因为如果是string等类就会发生浅拷贝，拷贝地址！！
        for (size_t i = 0; i < old_size; i++)
        {
            tmp[i] = _start[i];
        }
        delete[] _start;
        _start = tmp;
       // _finish = tmp + size();这样的话，finsh就一定为空了
        _finish = tmp + old_size;
        _end_of_storage = tmp + n;
       // delete[] tmp;不可以delete 因为这块空间已经是_start指向的了
    }
}
```

---

### 2、resize()

**坑：**

1. `resize()` 会修改 `size()`。所以，`resize()` 缩小时只需要移动 `_finish`。
2. `resize()` **扩大时可能需要先扩容**。
3. 新增元素使用 `value` 初始化，而不是固定赋值 `0`。
4. `while (_finish - _start < n)` 比较的是元素个数。
5. `resize()` 不会改变已有元素。

```cpp
void resize(size_t n, const T& value = T())
{
    if (n <= size())
    {
        _finish = _start + n;
    }
    else
    {
        if (n > capacity())
        {
            reserve(n);
        }
        while (_finish-_start<n)
        {
            *(_finish++) = value;
       }
    }
}
```

---

### 3、push_back()

**坑：**

1. 当 `_finish == _end_of_storage` 时需要扩容。
2. 插入元素位置是 `*_finish`。
3. 插入完成后 `_finish++`。

```cpp
void push_back(const T& x)
{
    if (capacity() == size())
    {
        reserve(capacity() == 0 ? 4 : capacity() * 2);
    }
    *_finish = x;
    _finish++;
}
```

---

### 4、pop_back()

**坑：**

* `pop_back()` 前必须**判空**。
* 删除元素本质上就是 `_finish--`。
* 不需要真正释放空间。

```cpp
void pop_back()
{
    //要判空
    if (size() == 0)
        return;
    _finish--;
}
```

---

### 5、operator[]

1. 返回类型是 `T&`。
2. **返回的是 `return _start[i]`，等价于 `*(_start + i)`**，因为，指针支持 `[]` 运算符，本质就是地址偏移再解引用。
3. 指针加减单位是元素，不是字节。
4. `return _start + i` 返回的是 `T*`，类型错误。

```cpp
// 元素访问
T& operator[](size_t i)
{
    assert(i < size());
   // return _start + size();为什么这里错了，这里返回的是什么？
    //_start是首元素的地址，_start+1是指针运算，*(_start+1)=_start[1]
    return _start[i];//为什么可以用[]?哦，因为_start是T*,T*类型就是T指针，那么，_start就是T类型数组的数组名（不准确），可以通过[]访问
    //还要注意，这里的T不能默认是内置类型，还可能是string等类型，

    // _start 是 T*，指向动态数组的首元素。
    // 指针也可以使用 [] 运算符，因为 p[i] 本质上等价于 *(p + i)。
    // 返回 T& 而不是 T，这样既避免拷贝，又可以支持 v[i] = x 的修改操作。
    // 注意：T 不一定是内置类型，还可能是 string、vector 或自定义类型，
    // 所以这里不能假设 T 是 int、char 等基本类型。
}
```

---

### 6、insert()

**坑：**

1. `insert()` 的 **`pos` 是迭代器，不是下标**。插入位置是在当前元素之前。
2. 扩容前必须保存下标 `index = pos - _start`。
3. 扩容后原来的 `pos` 已失效，需要重新计算。
4. 数据移动方向必须从后向前。
5. 返回值应为插入元素的迭代器。

```cpp
iterator insert(iterator pos, const T& x)//注意这里的pos是迭代器不是下标！！！
{
    assert(pos>=_start&&pos <= _finish);
    size_t index = pos - _start;//扩容后pos不可用了！！！！！！！
    if (_finish ==_end_of_storage)
    {
        reserve(capacity() == 0 ? 4 : capacity() * 2);
    }

    iterator tmp = _finish;
    while (tmp >_start+index)
    {
        *(tmp) = *(--tmp);
       // *(tmp) = *(tmp - 1);
    }
   // _start[pos] = x;
    *(_start+index) = x;
    _finish++;
    //return this;返回迭代器啊喂！！！
    return _start + index;//返回插入的元素的迭代器！！
}
```

---

### 7、erase()

**坑：**

1. `erase()` 删除的是当前迭代器指向的元素。
2. 删除方式是后面的元素整体向前覆盖。
3. 数据移动方向是从前向后。
4. 返回值应为删除位置后的新迭代器。

```cpp
iterator erase(iterator pos)//删除当前元素
{
    assert(pos < _finish && pos >= _start);
  /*  for (size_t i = pos; i < size(); i++)
    {
        _start[i - 1] = _start[i];
    }*/
    iterator tmp = pos;
    while (tmp < _finish-1)
    {
        *(tmp) = *(++tmp);
    }
    _finish--;
    //return this;返回迭代器啊喂！！！
    return pos;
}
```

---

### 8、拷贝构造 ⭐️⭐️

1. 拷贝构造不能直接 `swap()`。因为 `const vector&` 无法作为 `swap()` 参数交换资源。
2. 可以利用 `push_back()` 实现拷贝构造。
3. 拷贝构造应保证深拷贝。

```cpp
vector(const vector<T>& v)//注意这里是const，不能用swap
{
    T* tmp = new T[v.capacity()];
    for (size_t i = 0; i < v.size(); i++)
    {
        tmp[i] = v[i];
    }
    _start = tmp;
    _finish = tmp + v.size();
    _end_of_storage = tmp + v.capacity();
}
```

---

### 9、operator=

1. 推荐采用现代写法（Copy-Swap）。参数采用值传递：`vector<T> v`。利用拷贝构造生成副本，再调用 `swap()` 完成资源交换，自动解决自赋值问题。

```cpp
vector<T>& operator=(const vector<T>& v)
{
    vector<T> tmp(v);
    swap(tmp);
    return *this;
}
```

---

### 10、swap()

* `swap()` 参数必须是引用。因为要修改变量的值。
* `swap()` **只交换三个指针**。
* 注意：同一个类的成员函数可以访问其他对象的私有成员。不需要通过 `begin()` 等接口交换。

```cpp
//类成员函数可以访问类的私有变量！！！，不需要接口
/* iterator _capacity()
{
    return _end_of_storage;
}
void swap(vector<T>&v)
{
    std::swap(_start , v.begin());
    std::swap(_finish , v.end());
    std::swap(_end_of_storage , v._capacity());
}*/
void swap(vector<T>& v)
{
    std::swap(_start, v._start);
    std::swap(_finish, v._finish);
    std::swap(_end_of_storage, v._end_of_storage);
}
```

---

### 11、构造函数

1. 默认构造可直接使用 `= default`，（给了缺省值的情况下）
2. **`vector(size_t n, const T& value)` 构造 `n` 个相同元素。还要写一个 `vector(int n, const T& value)`**，为了避免与区间构造发生模板匹配歧义。
3. 区间构造属于函数模板，区间构造支持数组、`list`、`set`、`string` 等所有符合输入迭代器要求的类型。

```cpp
// 构造/析构
vector()
    : _start(nullptr)
    , _finish(nullptr)
    , _end_of_storage(nullptr)
{

}
vector(size_t n, const T& value = T())
{
    T* tmp = new T[n];
    for (int i = 0; i < n; i++)
    {
        tmp[i] = value;
    }
    _start = tmp;
    _finish = _start + n;
    _end_of_storage = _finish;
}
vector(int n, const T& value = T())
{
    T* tmp = new T[n];
    for (int i = 0; i < n; i++)
    {
        tmp[i] = value;
    }
    _start = tmp;
    _finish = _start + n;
    _end_of_storage = _finish;
}
template<class InputIterator>
vector(InputIterator first, InputIterator last)
{
    while (first != last)
    {
        push_back(*first);
        first++;
    }
}
```
#### 1，模版函数

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

因此，只要支持 `*`、`++`、`!=` 等迭代器操作，就可以传入这个函数做参数，就可以作为区间构造的参数。

---

#### 2， `vector<int> v(10,1)` 容易产生歧义的问题

类中同时存在：

```cpp
vector(size_t n, const T& value = T());

template<class InputIterator>
vector(InputIterator first, InputIterator last);
```

当写：vector<int> v(10,1);时，编译器既可以理解为：

```cpp
vector(size_t, const int&)
```

表示 **创建 10 个值为 1 的元素**；

也可以把模板推导为：**InputIterator = int**从而vector(int, int)，误认为这是区间构造。
为了减少这种匹配歧义，一些实现会额外提供：

```cpp
vector(int n, const T& value = T());
```

让 `vector(10,1)` 优先匹配普通构造函数。


---

### 12、迭代器

* `begin()` 返回首元素位置。
* `end()` 返回最后一个元素的下一个位置。
* `const` 对象会调用 `const` 版本。

```cpp
// 迭代器
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
```

---

### 13、模板实现

1. 模板的**声明和定义必须放在同一个头文件。**模板不能像普通函数一样分离到 `.cpp`。
2. 模板只有实例化时才真正生成代码。
---

## 十三、总结（复习时直接看）

- **`vector` = 支持动态扩容的顺序表 / 动态数组。**
- **最常用遍历方式：下标、迭代器、范围 `for`。**
- **`size()` 表示元素个数，`capacity()` 表示容量。**
- **`reserve()` 预留容量，不改元素个数。**
- **`resize()` 改元素个数，必要时扩容并初始化。**
- **`push_back()` 尾插，容量不够时可能扩容。**
- **扩容后旧空间释放，旧迭代器全部可能失效。**
- **`erase()` 返回删除位置之后的新迭代器。**
- **删除过程中遍历，标准写法是 `it = v.erase(it)`。**
- **二维 `vector` 本质是“元素是 `vector` 的 `vector`”。**
- **资源管理类不能用 `memcpy` 做扩容拷贝。**
- **扩容策略不是标准固定的，不同 STL 实现可能不同。**

---



## 下期预告

---

## 结语

**&emsp;&emsp;本文到此结束，感谢大家的阅读！如果觉得本文对你有所帮助，欢迎点赞、收藏、关注，也欢迎在评论区一起交流讨论。**
**&emsp;&emsp;也欢迎订阅我的<a>[深入理解 C++系列专栏](https://blog.csdn.net/2502_94353935/category_13191461.html)</a>、<a>[快速复习系列专栏](https://blog.csdn.net/2502_94353935/category_13135388.html)</a> 、<a>[算法系列专栏。](https://blog.csdn.net/2502_94353935/category_13148263.html)</a>**

---
<center>
<font color="#ff4d4f"><b>&emsp;&emsp;愿每一次敲下键盘，都比昨天更进一步！</b></font>    
</center>
<center>
<font color="#ff4d4f"><b>&emsp;&emsp;愿每一行代码落下，都让未来多一种可能！</b></font>   
</center>
<!-- 蓝：定义（#1677ff） -->
<!-- 绿：结论（#52c41a） -->
<!-- 红：易错（#ff4d4f） -->
<!-- 黄：注意（#fadb14） -->
<!-- 紫：扩展（#722ed1） -->
<!-- 青：技巧（#13c2c2） -->
<!-- 橙：重点（#faad14） -->
<!-- 深橙：面试（#d48806） -->
