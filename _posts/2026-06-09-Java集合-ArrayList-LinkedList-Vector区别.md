---
title: ArrayList、LinkedList Vector 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
一则或许对你有用的小广告

欢迎 [**加入小哈的星球**](https://www.quanxiaoha.com/column/) ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书

* **《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》** 已完结，基于 `Spring AI + Spring Boot 3.x + JDK 21...`， [**查看介绍**](https://www.quanxiaoha.com/column/10508.html)
* **《从零手撸：仿小红书（微服务架构）》** 已完结，基于 `Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...`， [**查看介绍**](https://www.quanxiaoha.com/column/10247.html) ；演示链接： [**http://116.62.199.48:7070/**](http://116.62.199.48:7070/)
* **《从零手撸：前后端分离博客项目（全栈开发）》** 2 期已完结，演示链接： [**http://116.62.199.48/**](http://116.62.199.48/)
* 新开坑项目： **《从零手撸：秒杀系统高并发优化实战》** 正在更新中...， [**查看介绍**](https://www.quanxiaoha.com/column/10659.html)

截止目前， [星球](https://www.quanxiaoha.com/column/) 内专栏 **累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习** ，欢迎 [**点击围观**](https://www.quanxiaoha.com/column/)

## 面试考察点

1. **集合框架基础** ：面试官不仅仅想知道你能说出这三者的区别，更想考察你是否理解 List 接口的不同实现方式及其底层原理，包括数组与链表的本质差异。
2. **性能敏感度** ：考察你是否清楚不同场景下的性能表现，能否根据实际业务需求（查询多还是增删多）选择合适的数据结构。
3. **线程安全意识** ：Vector 作为线程安全的集合，面试官想了解你是否知道它的实现方式以及为什么在实际开发中很少使用。

## 核心答案

三者都实现了 `List` 接口，但底层实现和特性差异明显：

| 特性 | ArrayList | LinkedList | Vector |
| --- | --- | --- | --- |
| 底层结构 | 动态数组 | 双向链表 | 动态数组 |
| 线程安全 | ❌ 不安全 | ❌ 不安全 | ✅ 安全（ `synchronized` ） |
| 默认容量 | 10 | 无（链表无容量概念） | 10 |
| 扩容机制 | 1.5 倍 | 无需扩容 | 2 倍 |
| 随机访问 | O(1) 快 | O(n) 慢 | O(1) 快 |
| 头部插入/删除 | O(n) 慢 | O(1) 快 | O(n) 慢 |
| 内存占用 | 连续内存，较少 | 节点额外存储前后指针 | 连续内存，较少 |
| 适用场景 | 查询多、尾部增删 | 频繁增删、尤其是头部 | 基本不用（性能差） |

**一句话总结** ：日常开发 90% 用 `ArrayList` ，频繁头部增删用 `LinkedList` ， `Vector` 基本被淘汰（可用 `Collections.synchronizedList` 或 `CopyOnWriteArrayList` 替代）。

## 深度解析

### 一、底层数据结构对比

上图展示了两种核心数据结构的内存布局差异：

* **ArrayList** ：使用连续的数组存储元素，每个元素通过下标直接定位。由于内存连续，CPU 缓存命中率高，遍历性能好。但插入删除需要移动后续元素。
* **LinkedList** ：每个元素包装成 Node 节点，包含数据、前驱指针 `prev` 和后继指针 `next` 。节点分散在堆内存各处，插入删除只需修改指针，但随机访问需要从头遍历。

### 二、性能对比详解

**1. 随机访问性能**

```
// ArrayList - O(1)
ArrayList<String> arrayList = new ArrayList<>();
arrayList.get(1000);  // 直接通过下标访问：elementData[index]

// LinkedList - O(n)
LinkedList<String> linkedList = new LinkedList<>();
linkedList.get(1000);  // 需要从头或尾遍历到第 1000 个节点
```

`ArrayList` 的 `get(int index)` 直接返回 `elementData[index]` ，时间复杂度 O(1)。

`LinkedList` 需要判断 index 在前半部分还是后半部分，然后从 head 或 tail 开始遍历：

```
// LinkedList 源码
Node<E> node(int index) {
    if (index < (size >> 1)) {  // 前半部分，从头遍历
        Node<E> x = first;
        for (int i = 0; i < index; i++)
            x = x.next;
        return x;
    } else {  // 后半部分，从尾遍历
        Node<E> x = last;
        for (int i = size - 1; i > index; i--)
            x = x.prev;
        return x;
    }
}
```

**2. 插入/删除性能**

```
// 头部插入对比
arrayList.add(0, "x");   // O(n)：需要移动所有元素
linkedList.addFirst("x"); // O(1)：只需修改两个指针

// 尾部插入对比
arrayList.add("x");       // O(1) 均摊：直接放入数组末尾
linkedList.addLast("x");  // O(1)：修改尾指针

// 中间插入对比
arrayList.add(5000, "x");   // O(n)：需要移动一半元素
linkedList.add(5000, "x");  // O(n)：需要先遍历找到位置，但插入本身 O(1)
```

**关键结论** ：

* 尾部操作： `ArrayList` 更快（无指针开销）
* 头部操作： `LinkedList` 完胜
* 中间操作：两者都是 O(n)，但 `ArrayList` 通常更快（遍历 + 移动 vs 遍历 + 指针操作）

### 三、扩容机制

**ArrayList 扩容** ：

```
// 添加元素时检查容量
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // 确保容量足够
    elementData[size++] = e;
    return true;
}

// 扩容核心逻辑
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5 倍
    // ... 省略边界检查
    elementData = Arrays.copyOf(elementData, newCapacity);  // 复制到新数组
}
```

**Vector 扩容** ：

```
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    // capacityIncrement 默认为 0，所以通常是 2 倍扩容
    int newCapacity = oldCapacity + ((capacityIncrement > 0) ?
                                     capacityIncrement : oldCapacity);
    // ...
}
```

| 对比项 | ArrayList | Vector |
| --- | --- | --- |
| 扩容倍数 | 1.5 倍 | 2 倍 |
| 扩容策略 | 节省内存 | 更激进 |
| 可自定义增量 | ❌ | ✅ `capacityIncrement` |

### 四、线程安全性

**Vector 的同步实现** ：

```
// Vector 几乎所有方法都加了 synchronized
public synchronized boolean add(E e) { ... }
public synchronized E get(int index) { ... }
public synchronized E remove(int index) { ... }
```

**问题** ：粗粒度锁导致并发性能差，即使是读操作也会阻塞。

**更好的替代方案** ：

```
// 方案一：Collections.synchronizedList（适合读多写少）
List<String> list = Collections.synchronizedList(new ArrayList<>());

// 方案二：CopyOnWriteArrayList（适合读非常多、写很少）
List<String> list = new CopyOnWriteArrayList<>();
```

### 五、最佳实践

```
// ❌ 错误：不知道容量，频繁扩容
List<String> list = new ArrayList<>();
for (int i = 0; i < 100000; i++) {
    list.add("item" + i);  // 触发多次扩容，性能差
}

// ✅ 正确：预估容量，避免扩容
List<String> list = new ArrayList<>(100000);

// ✅ 场景选择
// 场景1：查询为主（如缓存列表、配置项）→ ArrayList
// 场景2：频繁头部增删（如消息队列）→ LinkedList 或 ArrayDeque
// 场景3：需要线程安全 → CopyOnWriteArrayList 或 Collections.synchronizedList
```

## 面试高频追问

1. **ArrayList 的扩容为什么是 1.5 倍？**

   * 折中方案：既避免频繁扩容（如 1.1 倍），又减少内存浪费（如 2 倍）
   * 通过位运算 `oldCapacity + (oldCapacity >> 1)` 高效计算
2. **LinkedList 既然插入删除快，为什么实际很少用？**

   * CPU 缓存不友好（内存不连续）
   * 节点对象有额外内存开销（32 字节 vs 数组的 4-8 字节引用）
   * 实际场景中尾部操作更多， `ArrayList` 更优
3. **为什么阿里开发手册建议初始化 ArrayList 时指定容量？**

   * 避免多次扩容导致的数组复制开销
   * 扩容期间会同时存在两个数组，内存峰值翻倍

## 常见面试变体

* "ArrayList 和 LinkedList 谁更节省内存？"
* "频繁在列表中间插入元素，选哪个？"
* "如何实现一个线程安全的 ArrayList？"

## 记忆口诀

**选择口诀** ：

* **查询多用 ArrayList** ：数组连续好定位
* **头插多用 LinkedList** ：链表指针改得快
* **Vector 几乎不用** ：同步太粗性能差

## 总结

`ArrayList` 基于动态数组，随机访问 O(1)、尾部增删 O(1)，适合查询为主的场景； `LinkedList` 基于双向链表，头部增删 O(1) 但随机访问 O(n)，适合频繁头部操作； `Vector` 虽然线程安全但使用粗粒度锁性能差，已被 `CopyOnWriteArrayList` 等并发集合替代。实际开发中，预估容量初始化 `ArrayList` ，特殊场景再考虑 `LinkedList` 。
