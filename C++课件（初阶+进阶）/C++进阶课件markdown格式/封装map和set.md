# 封装 map 和 set（一个红黑树复用出两个容器）

> 📎 对应课程：[[规划/01_规划/规划路线项目/课程/课程最终版|C++直播主线课表]] · 第 28 课《封装map和set》（博客）

我们来对map和set进行一下封装，我们来学习一下库里面是怎么封装map和set的

## 一、库里 map 和 set 的源码及框架分析
本质：set和map继承红黑树！
但是呢，set只要一个key即可，map要key/value两个值，怎么办呢？
即，我们要让
```cpp
set<int> s1;
map<int,string> m1;
```
map和set都继承红黑树并且达到效果，要怎么办呢？可以这样
```cpp
template <class K>
class set
{
public:

	private:
		RBTree< K, const K, keyofset> _set;
	};
}
template <class K ,class V>
	class map
	{
	public:
	private:
		RBTree<K, std::pair<const K, V>, keyofmap > _map;
	};
}
```
也就是，红黑树有三个参数，键值key，底层存储的什么（set就是一个key，map是pair类型的kv，以及第三个获取key的仿函数）
问题1：为什么要用仿函数来获取key而不是直接利用第一个参数？
首先我们要搞明白，什么函数我们需要使用key 键值？

其实就两个：一个是插入（insert）的函数，还有一个是查找（find）的。
你使用的时候都是传的T类型,，即
```cpp
s1.insert(2);
m1.insert(2,"hello");
```

所以，我们可以看到，红黑树（RBTree）里面这两个函数，你使用的时候，传的参数都是 T 类型的。即对应的第二个参数   ^ed4463

```cpp
template<class K, class	T ,class keyoftree>
class RBTree
{
// 插入
pair<Iterator,bool> Insert(const T& data)
```
所以现在问题就变成了：我们要从你传的 T 类型中，来获得这个键值 Key（为什么要从你传的 T 类型来获取这个键值 key？）

因为红黑树（RBTree）不知道外面是 set 在调用还是 map 在调用，它不知道 T 是一个参数的 key 类型，还是两个参数的 pair 类型）
所以，我们就需要提供一个仿函数 KeyOfT！

###  仿函数 KeyOfT

```cpp
template <class K>
class set
{
public:
	struct keyofset//因为要和map保持一致，所以，也要写一个仿函数
	{
		const K& operator()(const K& k)
		{
			return k;
		}
	};

template <class K ,class V>
class map
{
public:
	class keyofmap//仿函数
	{
	public:
		const K& operator()(const pair<K,V>& kv)
		{
			return kv.first;
		}
	};
```
红黑树的底层实现中，利用 KeyOfValue 这个仿函数来调用并得到键值 Key，其实也很简单。
```cpp
	// 插入
	pair<Iterator,bool> Insert(const T& data)
	{
		......
		keyoftree kof;
		while (cur)
		{
			if (kof(data) < kof(cur->_data))
```
那么现在，Map 和 Set 与底层红黑树的关系已经搭建好了。后面我们只需要再来看底层的红黑树需要改动哪些地方即可。
### 红黑树的改动
节点：全部存 T（即 map 和 set 底层存的都是 T 类型，也就是第二个参数，红黑树参数表见：[[封装map和set#^ed4463]]）

```cpp
template<class T>
struct RBTreeNode
{
......
}
```
节点的具体代码：[[封装map和set#^e18c42]]
那我们改正完树的节点，就可以写树的结构了
### 红黑树的结构
```cpp
template<class K, class	T ,class keyoftree>
class RBTree
{
	//typedef RBTreeNode<K,T> Node;当然可以这么设计，但是STL 选择存 T，是为了让底层 RBTree 更通用。
	typedef RBTreeNode<T> Node;
	private:
	Node* _root = nullptr;
};
```
那么，我们就可以对相应的函数进行改写，即引入仿函数，把key换为：kof(data)
即，例如原来：
```cpp
if(key<cur->_key)
```
换成：
```cpp
keyoftree kof;
......
if (kof(data) < kof(cur->_data))
```
等等
## 迭代器的实现
### 迭代器的结构
与之前的学习一样，我们要支持 const 迭代器也要支持普通迭代器，所以我们要利用模板；另外，相较于原来只存储一个节点的指针，我们在这里增加了一个根节点的指针 `_root`，原因是：`--end()` 时要从根出发找整棵树的**最右节点**（中序最后一个）
```cpp
template<class T, class Ref, class Ptr>
struct RBTreeIterator//struct 因为你这个肯定要给外面的用，就是，比较公有，
{
	typedef RBTreeNode<T> Node;
	typedef RBTreeIterator<T, Ref, Ptr> Self;
	//成员：两个指针,
	Node* _node;
	Node* _root;
```
### operator++
我们要清楚，这里的 ++ 是按照**中序遍历**来走的，我们在这里实现 operator++ 看似很复杂，其实很简单
当我们走到某个节点时，我们要++，可以分为以下几种情况：
1，**右**孩子为空：向上找祖先，直到当前节点是父亲的**左**孩子，那个父亲就是下一个节点
![[Pasted image 20260814221918.png]]
2，**右**孩子不为空——找到**右**孩子里面的最**左**孩子（最**小**孩子）
![[Pasted image 20260814222239.png]]
完整代码：[[封装map和set#^e640ae]]
### operator--
和operator++类似，
当我们走到某个节点时，我们要--，可以分为以下几种情况：
1，**左**孩子为空：向上找祖先，直到当前节点是父亲的**右**孩子，那个父亲就是下一个节点（即中序前驱）
![[Pasted image 20260814234732.png]]
2，**左**孩子不为空——找到**左**孩子里面的最**右**孩子（最**大**孩子）
![[Pasted image 20260814234941.png]]

### operator*、==、->、!=

```cpp
	Ptr operator->()
	{
		return &_node->_data;//it->要达到的效果就是，it->可以访问到data里面的东西，那就要返回_node->_data;的地址
	}
	bool operator==(const RBTreeIterator& it)const//一般只读属性的就要加const
	{
		return _node == it._node;
	}
	bool operator!=(const RBTreeIterator& it)const
	{
		return _node != it._node;
	}
```
那么，我们现在就可以实现红黑树的迭代器相关函数：begin和end了
### begin和end
begin：最左节点
end：最右节点的下一个节点——nullptr
```cpp
	Iterator begin()
	{
		Node* cur = _root;
		if (_root == nullptr)
			return Iterator(nullptr,_root);
		while (cur&&cur->_left)
		{
			cur = cur->_left;
		}
		return Iterator(cur,_root);
	}
	Iterator end()
{
	return Iterator(nullptr, _root);
}
```
### map支持的operator[]
operator[]仅仅是map支持，所以，我们只需要在map里面实现，operator[]底层调用的函数是insert函数，但是，我们要改一下insert函数的返回值，由bool改为：pair<iterator,bool>
```cpp
pair<Iterator,bool> Insert(const T& data)
```
这里的insert函数，插入T，返回值pair<Iterator,bool>，第二个bool对应的就是是否插入成功，第一个为T对应的迭代器，
所以，我们的operator[]可以这样实现
```cpp
	V& operator[](const K& key)
	{
		pair<iterator, bool> ret = insert(make_pair(key, V()));
		return ret.first->second;
	}
```
### 库里面的实现
库里面对RBTree的结构与我们这里设计的有一点区别：库里面加入了一个哨兵节点。
![[Pasted image 20260815155924.png]]
## 附：完整实现代码
文件：RBTree.h
```cpp
#pragma once

#include <utility>    // std::pair
#include <algorithm>  // std::max
#include <cassert>    // assert

enum Colour
{
	RED,
	BLACK
};


template<class T>
struct RBTreeNode
{
	T _data;

	RBTreeNode<T>* _left;
	RBTreeNode<T>* _right;
	RBTreeNode<T>* _parent;

	Colour _col;

	RBTreeNode(const T& data)
		:_data(data)
		,_left(nullptr)
		,_right(nullptr)
		,_parent(nullptr)
		,_col(RED)
	{ }
};
```
^e18c42
```cpp
template<class T, class Ref, class Ptr>
struct RBTreeIterator//struct 因为你这个肯定要给外面的用，就是，比较公有，
{
	typedef RBTreeNode<T> Node;
	typedef RBTreeIterator<T, Ref, Ptr> Self;
	//成员：两个指针,
	Node* _node;
	Node* _root;
	//默认构造
	RBTreeIterator(Node* node,Node* root)
		:_node(node)
		,_root(root)
	{ }
	/*RBTreeIterator& operator++()
	{
	
		Node* cur = _node;
		Node* parent = cur->_parent;
		if (cur->_right)
		{
			while (cur->_left)
			{
				cur = cur->_left;
			}
			return RBTreeIterator(cur);
		}
		else if (parent->_left == cur)
			return RBTreeIterator(parent);
		else if (parent->_right == cur)
		{
			while (parent && parent->_right == cur)
			{
				cur = cur->_parent;
				parent = parent->_parent;
			}
			return RBTreeIterator(parent);
		}
		else assert(false);



	}*/
	Self& operator++()
	{
		assert(_node);
		Node* cur = _node;
		Node* parent = cur->_parent;
		if (cur->_right)//如果右孩子不为空，访问右孩子的最小节点，即最左孩子
		{
			cur = cur->_right;
			while (cur->_left)
			{
				cur = cur->_left;
			}
			_node = cur;
		}
		else//找到/访问孩子是父亲的左孩子的父亲
		{
			while (parent && parent->_right == cur)
			{
				cur = cur->_parent;
				parent = parent->_parent;
			}
			_node = parent;
		}
		return *this;


	}
	Self& operator--()
	{
		Node* cur = _node;
		
		if (cur == nullptr)
		{
			Node* ccur = _root;
			while (ccur&&ccur->_right)
			{
				ccur = ccur->_right;
			}
			_node = ccur;
		}
		else
		{
			Node* parent = cur->_parent;
			if (cur->_left)//左边不为空，左边找最右节点
			{
				cur = cur->_left;
				while (cur->_right)
				{
					cur = cur->_right;
				}
				_node = cur;
			}
			else
			{
				//如果孩子是父亲的右孩子，那就是访问完了的,要找的就是这个
				while (parent && parent->_left == cur)
				{
					cur = parent;
					parent = parent->_parent;
				}
				_node = parent;
			}
			
		}
		return *this;
	}
	//Self& operator--()
	//{
	//	Node* cur = _node;

	//	if (cur == nullptr)
	//	{
	//		// --end()
	//		cur = _root;

	//		while (cur && cur->_right)
	//		{
	//			cur = cur->_right;
	//		}

	//		_node = cur;
	//	}
	//	else
	//	{
	//		Node* parent = cur->_parent;

	//		if (cur->_left)
	//		{
	//			// 左子树最大节点
	//			cur = cur->_left;

	//			while (cur->_right)
	//			{
	//				cur = cur->_right;
	//			}

	//			_node = cur;
	//		}
	//		else
	//		{
	//			// 往上找：当前节点是父亲右孩子的祖先

	//			while (parent && cur == parent->_left)
	//			{
	//				cur = parent;
	//				parent = parent->_parent;
	//			}

	//			_node = parent;
	//		}
	//	}

	//	return *this;
	//}
	//Self operator--()
	//{
	//	if (_node == nullptr)  // --end()
	//	{
	//		// --end()，特殊处理，走到中序最后一个结点，整棵树的最右结点
	//		Node* rightMost = _root;
	//		while (rightMost && rightMost->_right)
	//		{
	//			rightMost = rightMost->_right;
	//		}
	//		_node = rightMost;
	//	}
	//	else if (_node->_left)
	//	{
	//		// 左子树不为空，中序左子树最后一个
	//		Node* rightMost = _node->_left;
	//		while (rightMost->_right)
	//		{
	//			rightMost = rightMost->_right;
	//		}
	//		_node = rightMost;
	//	}
	//	else
	//	{
	//		// 孩子是父亲右的那个祖先
	//		Node* cur = _node;
	//		Node* parent = cur->_parent;
	//		while (parent && cur == parent->_left)
	//		{
	//			cur = parent;
	//			parent = cur->_parent;
	//		}
	//		_node = parent;
	//	}

	//	return *this;
	//}
	Ref operator*()
	{
		return _node->_data;
	}
	Ptr operator->()
	{
		return &_node->_data;//it->要达到的效果就是，it->可以访问到data里面的东西，那就要返回_node->_data;的地址
	}
	bool operator==(const RBTreeIterator& it)const//一般只读属性的就要加const
	{
		return _node == it._node;
	}
	bool operator!=(const RBTreeIterator& it)const
	{
		return _node != it._node;
	}

};
```
^e640ae
```cpp
template<class K, class	T ,class keyoftree>
class RBTree
{
	//typedef RBTreeNode<K,T> Node;当然可以这么设计，但是 STL 选择存 T，是为了让底层 RBTree 更通用。
	typedef RBTreeNode<T> Node;

public:
	typedef RBTreeIterator<T, T&, T*> Iterator;
	typedef RBTreeIterator<T, const T&, const T*> Const_Iterator;//加 const 是为了兼容返回值为 const 类型的函数，T不加 const 是因为RBTreeIterator里面没有返回 const T 的函数
	Iterator begin()
	{
		Node* cur = _root;
		if (_root == nullptr)
			return Iterator(nullptr,_root);
		while (cur&&cur->_left)
		{
			cur = cur->_left;
		}
		return Iterator(cur,_root);
	}
	Const_Iterator begin()const
	{
		Node* cur = _root;
		if (_root == nullptr)
			return Const_Iterator(nullptr,_root);
		while (cur && cur->_left)
		{
			cur = cur->_left;
		}
		return Const_Iterator(cur, _root);
	}
	Iterator end()
	{
		return Iterator(nullptr, _root);
	}
	Const_Iterator end()const
	{
		
		return Const_Iterator(nullptr, _root);
	}

	// 插入
	std::pair<Iterator, bool> Insert(const T& data)
	{
		if (_root == nullptr)
		{
			_root = new Node(data);
			_root->_col = BLACK;
			return { Iterator(_root,_root),true };
		}
		//依旧先找到插入位置
		keyoftree kof;
		Node* cur = _root;
		Node* parent = _root;
		while (cur)
		{
			if (kof(data) < kof(cur->_data))
			{
				parent = cur;
				cur = cur->_left;
			}
			else if (kof(data) > kof(cur->_data))
			{
				parent = cur;
				cur = cur->_right;
			}
			else
				return { Iterator(cur,_root),false };
		}
		cur = new Node(data);
		Node* newnode = cur;
		if (kof(data) < kof(parent->_data))
		{
			parent->_left = cur;
			cur->_parent = parent;
		}
		else if (kof(data) > kof(parent->_data))
		{
			parent->_right = cur;
			cur->_parent = parent;
		}
		else
			assert(false);
		while (parent&&parent->_col==RED)//父亲为红
		{
			Node* grandfather = parent->_parent;
			Node* uncle = nullptr;
			if (parent == grandfather->_left)//父亲是爷爷的左孩子
			{
				uncle = grandfather->_right;//得到叔叔
					if (uncle && uncle->_col == RED)//叔叔存在且为红
					{
						//仅变色
						grandfather->_col = RED;
						uncle->_col = BLACK;
						parent->_col = BLACK;
					}
					else if (parent->_left == cur) // 叔叔不存在或为黑，然后有分，我和父亲的关系和父亲和爷爷的关系是一样的，都是左孩子
					{
						//右单旋
						RotateR(grandfather);
						//变色
						parent->_col = BLACK;
						grandfather->_col = RED;
						break;
					}
					else if (parent->_right == cur)//我c是父亲p的右孩子，双旋
					{
						//左右双旋
						RotateL(parent);
						RotateR(grandfather);
						cur->_col = BLACK;
						grandfather->_col = RED;
						break;
					}
					else
						assert(false);
				
			}
			else if (parent == grandfather->_right)
			{
				uncle = grandfather->_left;
				
					if (uncle && uncle->_col == RED)
					{
						//仅变色
						grandfather->_col = RED;
						uncle->_col = BLACK;
						parent->_col = BLACK;
					}
					else if (parent->_right == cur)//uncle存在与否已经不重要了
					{
						//左单旋
						RotateL(grandfather);
						//变色
						parent->_col = BLACK;
						grandfather->_col = RED;
						break;
					}
					else if (parent->_left == cur)
					{
						//右左双旋
						RotateR(parent);
						RotateL(grandfather);
						cur->_col = BLACK;
						grandfather->_col = RED;
						break;
					}
					else
						assert(false);
			}
			else
				assert(false);
			//继续更新
			cur = grandfather;
			parent = cur->_parent;
		}
		//根一定是黑，最后统一处理，
		_root->_col = BLACK;
		return { Iterator(newnode,_root),true };

	}
	

	// 右旋
	void RotateR(Node* parent)
	{
		Node* sub = parent;
		Node* subL = parent->_left;
		Node* pparent = parent->_parent;
		Node* subLR = subL->_right;
		sub->_left = subLR;
		if (subLR)subLR->_parent = sub;
		subL->_right = sub;
		sub->_parent = subL;
		if (pparent == nullptr)
		{
			_root = subL;
			subL->_parent = nullptr;
		}
		else if (pparent->_left == sub)
		{
			pparent->_left = subL;
			subL->_parent = pparent;
		}
		else if (pparent->_right == sub)
		{
			pparent->_right = subL;
			subL->_parent = pparent;
		}
		else
			assert(false);
	}


	// 左旋
	void RotateL(Node* parent)
	{
		Node* sub = parent;
		Node* subR = parent->_right;
		Node* pparent = parent->_parent;
		Node* subRL = subR->_left;
		sub->_right = subRL;
		if (subRL) subRL->_parent = sub;
		subR->_left = sub;
		sub->_parent = subR;
		if (pparent == nullptr)
		{
			_root = subR;
			subR->_parent = nullptr;
		}
		else if (pparent->_left == sub)
		{
			pparent->_left = subR;
			subR->_parent = pparent;
		}
		else if (pparent->_right == sub)
		{
			pparent->_right = subR;
			subR->_parent = pparent;
		}
		else
			assert(false);
	}


	// 获取树高度
	int Height()
	{
		return _Height(_root);
	}


	// 获取节点数量
	int Size()
	{
		return _Size(_root);
	}


	// 查找
	Node* Find(const T& data)
	{
		if (_root == nullptr)return nullptr;
		Node* cur = _root;
		keyoftree kof;
		while (cur)
		{
			if (kof(data) <kof( cur->_data))
				cur = cur->_left;
			else if (kof( data) > kof( cur->_data))
				cur = cur->_right;
			else return cur;
		}
		return nullptr;
	}

	
private:


	// 高度辅助函数
	int _Height(Node* root)
	{
		if (root == nullptr)
			return 0;
		int left_hegint = _Height(root->_left);
		int right_height = _Height(root->_right);
		return std::max(left_hegint, right_height) + 1;
	}


	// 节点数量辅助函数
	int _Size(Node* root)
	{
		if (root == nullptr)
			return 0;
		int left = _Size(root->_left);
		int right = _Size(root->_right);
		return left + right + 1;
	}



private:

	Node* _root = nullptr;
};
```
文件：mymap
```cpp
#pragma once
#include"RBTree.h"

namespace caige
{
	template <class K ,class V>
	class map
	{
	public:
		class keyofmap//仿函数
		{
		public:
			const K& operator()(const std::pair<K, V>& kv)
			{
				return kv.first;
			}
		};
		typedef typename RBTree<K, std::pair<const K, V>, keyofmap>::Iterator iterator;
		typedef typename RBTree<K,  std::pair<const K, V>, keyofmap>::Const_Iterator const_iterator;
		iterator begin()
		{
			return _map.begin();
		}

		iterator end()
		{
			return _map.end();
		}

		const_iterator begin() const
		{
			return _map.begin();
		}

		const_iterator end()  const
		{
			return _map.end();
		}

		std::pair<iterator, bool> insert(const std::pair< K, V>& kv)
		{
			return _map.Insert(kv);
		}
		/*iterator& operator[](const V& v,const K& k)
		{
			return Insert({ v,k }).first;
		}*/
		//复习一下运算符重载，错误理解
		//单参数；返回值就是该参数
		//双参数：第二个参数做返回值，第一个参数做参数
		//正确理解
		//一元运算符：成员函数 0 个显式参数（this 就是那唯一的操作数）
		//二元运算符：成员函数 1 个显式参数（this 是左操作数，显式参数是右操作数）
		V& operator[](const K& key)
		{
			std::pair<iterator, bool> ret = insert(std::make_pair(key, V()));
			return ret.first->second;
		}

		
	private:
		RBTree<K, std::pair<const K, V>, keyofmap > _map;
	};
}
```
文件：myset
```cpp
#pragma once
#include"RBTree.h"
namespace caige
{
	template <class K>
	class set
	{
	public:
		struct keyofset//因为要和map保持一致，所以，也要写一个仿函数
		{
			const K& operator()(const K& k)
			{
				return k;
			}
		};
		typedef typename RBTree<K, const K, keyofset>::Iterator iterator;
		typedef typename RBTree<K, const K, keyofset>::Const_Iterator const_iterator;
		iterator begin()
		{
			return _set.begin();
		}

		iterator end()
		{
			return _set.end();
		}

		const_iterator begin() const
		{
			return _set.begin();
		}

		const_iterator end()  const
		{
			return _set.end();
		}

		std::pair<iterator, bool> insert(const K& key)
		{
			return _set.Insert(key);
		}
	private:
		RBTree< K, const K, keyofset> _set;
	};
}
```