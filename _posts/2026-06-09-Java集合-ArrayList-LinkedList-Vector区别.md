---
title: ArrayList、LinkedList ?Vector 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---

## 面试考察?

1. **集合框架基础**：面试官不仅仅想知道你能说出这三者的区别，更想考察你是否理?List 接口的不同实现方式及其底层原理，包括数组与链表的本质差异?

2. **性能敏感?*：考察你是否清楚不同场景下的性能表现，能否根据实际业务需求（查询多还是增删多）选择合适的数据结构?

3. **线程安全意识**：Vector 作为线程安全的集合，面试官想了解你是否知道它的实现方式以及为什么在实际开发中很少使用?

## 核心答案

三者都实现?`List` 接口，但底层实现和特性差异明显：

| 特?| ArrayList | LinkedList | Vector |
|---|---|---|---|
| 底层结构 | 动态数?| 双向链表 | 动态数?|
| 线程安全 | ?不安?| ?不安?| ?安全（`synchronized`?|
| 默认容量 | 10 | 无（链表无容量概念） | 10 |
| 扩容机制 | 1.5 ?| 无需扩容 | 2 ?|
| 随机访问 | O(1) ?| O(n) ?| O(1) ?|
| 头部插入/删除 | O(n) ?| O(1) ?| O(n) ?|
| 内存占用 | 连续内存，较?| 节点额外存储前后指针 | 连续内存，较?|
| 适用场景 | 查询多、尾部增?| 频繁增删、尤其是头部 | 基本不用（性能差） |

**一句话总结**：日常开?90% ?`ArrayList`，频繁头部增删用 `LinkedList`，`Vector` 基本被淘汰（可用 `Collections.synchronizedList` ?`CopyOnWriteArrayList` 替代）?

## 深度解析

### 一、底层数据结构对?

- **ArrayList**：使用连续的数组存储元素，每个元素通过下标直接定位。由于内存连续，CPU 缓存命中率高，遍历性能好。但插入删除需要移动后续元素?

- **LinkedList**：每个元素包装成 Node 节点，包含数据、前驱指?`prev` 和后继指?`next`。节点分散在堆内存各处，插入删除只需修改指针，但随机访问需要从头遍历?

### 二、性能对比详解

**1. 随机访问性能**

```java
// ArrayList - O(1)
ArrayList<String> arrayList = new ArrayList<>();
arrayList.get(1000);  // 直接通过下标访问：elementData[index]

// LinkedList - O(n)
LinkedList<String> linkedList = new LinkedList<>();
linkedList.get(1000);  // 需要从头或尾遍历到?1000 个节?
```

`ArrayList` ?`get(int index)` 直接返回 `elementData[index]`，时间复杂度 O(1)?

`LinkedList` 需要判?index 在前半部分还是后半部分，然后?head ?tail 开始遍历：

```java
// LinkedList 源码
Node<E> node(int index) {
    if (index < (size >> 1)) {  // 前半部分，从头遍?
        Node<E> x = first;
        for (int i = 0; i < index; i++)
            x = x.next;
        return x;
    } else {  // 后半部分，从尾遍?
        Node<E> x = last;
        for (int i = size - 1; i > index; i--)
            x = x.prev;
        return x;
    }
}
```

**2. 插入/删除性能**

```java
// 头部插入对比
arrayList.add(0, "x");   // O(n)：需要移动所有元?
linkedList.addFirst("x"); // O(1)：只需修改两个指针

// 尾部插入对比
arrayList.add("x");       // O(1) 均摊：直接放入数组末?
linkedList.addLast("x");  // O(1)：修改尾指针

// 中间插入对比
arrayList.add(5000, "x");   // O(n)：需要移动一半元?
linkedList.add(5000, "x");  // O(n)：需要先遍历找到位置，但插入本身 O(1)
```

**关键结论**?

- 尾部操作：`ArrayList` 更快（无指针开销?
- 头部操作：`LinkedList` 完胜
- 中间操作：两者都?O(n)，但 `ArrayList` 通常更快（遍?+ 移动 vs 遍历 + 指针操作?

### 三、扩容机?

**ArrayList 扩容**?

```java
// 添加元素时检查容?
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // 确保容量足够
    elementData[size++] = e;
    return true;
}

// 扩容核心逻辑
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5 ?
    // ... 省略边界检?
    elementData = Arrays.copyOf(elementData, newCapacity);  // 复制到新数组
}
```

**Vector 扩容**?

```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    // capacityIncrement 默认?0，所以通常?2 倍扩?
    int newCapacity = oldCapacity + ((capacityIncrement > 0) ?
                                     capacityIncrement : oldCapacity);
    // ...
}
```

| 对比?| ArrayList | Vector |
|---|---|---|
| 扩容倍数 | 1.5 ?| 2 ?|
| 扩容策略 | 节省内存 | 更激?|
| 可自定义增量 | ?| ?`capacityIncrement` |

### 四、线程安全?

**Vector 的同步实?*?

```java
// Vector 几乎所有方法都加了 synchronized
public synchronized boolean add(E e) { ... }
public synchronized E get(int index) { ... }
public synchronized E remove(int index) { ... }
```

**问题**：粗粒度锁导致并发性能差，即使是读操作也会阻塞?

**更好的替代方?*?

```java
// 方案一：Collections.synchronizedList（适合读多写少?
List<String> list = Collections.synchronizedList(new ArrayList<>());

// 方案二：CopyOnWriteArrayList（适合读非常多、写很少?
List<String> list = new CopyOnWriteArrayList<>();
```

### 五、最佳实?

```java
// ?错误：不知道容量，频繁扩?
List<String> list = new ArrayList<>();
for (int i = 0; i < 100000; i++) {
    list.add("item" + i);  // 触发多次扩容，性能?
}

// ?正确：预估容量，避免扩容
List<String> list = new ArrayList<>(100000);

// ?场景选择
// 场景1：查询为主（如缓存列表、配置项）→ ArrayList
// 场景2：频繁头部增删（如消息队列）?LinkedList ?ArrayDeque
// 场景3：需要线程安??CopyOnWriteArrayList ?Collections.synchronizedList
```

## 面试高频追问

1. **ArrayList 的扩容为什么是 1.5 倍？**
    - 折中方案：既避免频繁扩容（如 1.1 倍），又减少内存浪费（如 2 倍）
    - 通过位运?`oldCapacity + (oldCapacity >> 1)` 高效计算

2. **LinkedList 既然插入删除快，为什么实际很少用?*
    - CPU 缓存不友好（内存不连续）
    - 节点对象有额外内存开销?2 字节 vs 数组?4-8 字节引用?
    - 实际场景中尾部操作更多，`ArrayList` 更优

3. **为什么阿里开发手册建议初始化 ArrayList 时指定容量？**
    - 避免多次扩容导致的数组复制开销
    - 扩容期间会同时存在两个数组，内存峰值翻?

## 常见面试变体

- "ArrayList ?LinkedList 谁更节省内存?
- "频繁在列表中间插入元素，选哪个？"
- "如何实现一个线程安全的 ArrayList?

## 记忆口诀

**选择口诀**?

- **查询多用 ArrayList**：数组连续好定位
- **头插多用 LinkedList**：链表指针改得快
- **Vector 几乎不用**：同步太粗性能?

## 总结

`ArrayList` 基于动态数组，随机访问 O(1)、尾部增?O(1)，适合查询为主的场景；`LinkedList` 基于双向链表，头部增?O(1) 但随机访?O(n)，适合频繁头部操作；`Vector` 虽然线程安全但使用粗粒度锁性能差，已被 `CopyOnWriteArrayList` 等并发集合替代。

实际开发中，预估容量初始化 `ArrayList`，特殊场景再考虑 `LinkedList`?

---
> 参考来源：[ArrayList、LinkedList ?Vector 的区别？](https://www.quanxiaoha.com/java-interview/arraylist-vs-linkedlist-vs-vector-difference)
