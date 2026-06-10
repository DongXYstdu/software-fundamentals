---
title: HashMap、Hashtable ?ConcurrentHashMap 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---

## 面试考察?

面试官提出这个问题，通常旨在考察以下五个层面的理解：

1. **基础概念掌握?* 你是否能清晰地说出这三者在**线程安全?*上的根本区别?

2. **历史演进与设计认知：** 你是否了解从 `Hashtable` ?`ConcurrentHashMap` ?Java 在解?并发安全哈希?问题上的一次重要设计演进，理解其背后的性能与设计权衡?

3. **底层实现原理?* 这不仅仅?有没有锁"的区别，更是?*锁的粒度与实现机?*理解的考察。面试官想知道你是否了解 `ConcurrentHashMap` ?JDK 不同版本（如 1.7 ?1.8）中是如何通过精巧的设计（如分段锁、CAS + synchronized）来实现高并发读写的?

4. **性能分析与场景应用：** 你是否能结合它们的实现原理，分析其在单线程、低并发、高并发等不同场景下的性能差异，并给出正确的使用建议?

5. **API 与细节认知：** 你是否注意到了它们在 API 设计（如?`null` 值的处理）和行为上的一些细微但重要的区别?

## 核心答案

简单来说，它们的核心区别在?*线程安全的实现方式与性能**?

- **HashMap**?*非线程安?*，性能最高。在多线程环境下直接使用会导致数据不一致，甚至死循环（?JDK 1.7 及之前的扩容场景下）?

- **Hashtable**?*线程安全**，但实现方式粗暴。它通过在几乎所有公开方法上添?**`synchronized`** 关键字实现同步，相当于对整张哈希表加锁，性能非常低下，在高并发场景下是性能瓶颈?

- **ConcurrentHashMap**?*线程安全**，且是高并发场景下的首选。它通过更细粒度的锁机制（JDK 1.7 ?*分段?*，JDK 1.8 及之后的 **`synchronized` + CAS + volatile**）来实现高并发下的线程安全，在保证安全的同时，性能远优?`Hashtable`?

## 深度解析

### 原理/机制

**HashMap (JDK 8+):**

- 底层?**"数组 + 链表 / 红黑?** 结构。通过哈希函数计算键的索引，发生哈希冲突时，链表解决。当链表长度超过阈值（默认?8）且数组长度达到 64 时，链表会转换为红黑树以提升查询效率?

**Hashtable:**

- 同样是数?链表结构。其线程安全性通过?`put`，`get`，`size` 等所有公开方法上声?**`synchronized`** 来保证。这意味着任意时刻，只有一个线程能访问实例的方法，锁的粒度是整?`Hashtable` 对象?

**ConcurrentHashMap (JDK 8+):**

- 放弃?JDK 1.7 的分段锁（Segment），采用了与 `HashMap` 更相似的 **Node 数组 + 链表 / 红黑?* 结构?

- 其并发控制通过 **`synchronized` 锁住单个链表头节点（或红黑树根节点）** 和大量的 **CAS (Compare-And-Swap) 无锁乐观?* 操作来实现?

    - **初始化数组、插入新节点** 等操作使?CAS，无需加锁，性能极高?

    - 只有当发生哈希冲突，需要操作某个桶（bucket）的链表或红黑树时，才使?`synchronized` 锁住该桶的头节点。这使得锁的**粒度从整个表细化到了单个?*，极大提高了并发度?

- 同时，使?`volatile` 关键字修饰节点值和 `next` 指针，保证了线程间的可见性?

### 代码示例与对?

```java
// 1. HashMap - 线程不安全示?
Map<String, String> hashMap = new HashMap<>();
// 多线程并?put，可能导致数据丢失、size计算不准，或JDK1.7下的死循环?

// 2. Hashtable - 线程安全，但效率?
Map<String, String> hashtable = new Hashtable<>();
// 任何操作都会锁住整个表，线程安全但阻塞严重?

// 3. ConcurrentHashMap - 线程安全且高?
Map<String, String> concurrentMap = new ConcurrentHashMap<>();
// 高并发读写的最佳选择，锁粒度细，并发度高?
```

### 对比分析与最佳实?

| 特?| HashMap | Hashtable | ConcurrentHashMap (JDK 8+) |
|---|---|---|---|
| **线程安全** | ?| 是（全表锁） | 是（桶级?+ CAS?|
| **性能** | 最高（单线程） | 最低（全表锁阻塞） | 很高（高并发下最优） |
| **Null ??* | **允许** 一?`null` 键和多个 `null` ?| **不允?*，会抛出 `NullPointerException` | **不允?*，会抛出 `NullPointerException` |
| **迭代?* | **快速失?* | **快速失?* | **弱一致?* |
| **底层结构** | 数组+链表/红黑?| 数组+链表 | 数组+链表/红黑?|
| **锁机?* | 无锁 | `synchronized` 方法（对象锁?| `synchronized` + CAS (?节点? |

**最佳实践：**

- **单线程环境：** 无条件使?`HashMap`?

- **遗留系统或需要绝对强一致性的读（较少见）?* 可考虑 `Hashtable`，但新项目绝不推荐?

- **多线程并发环境：** **一律使?`ConcurrentHashMap`**。它是现代高并发 Java 应用的标配，完美替代 `Hashtable` ?`Collections.synchronizedMap(new HashMap<>())`?

### 常见误区

- **认为 `ConcurrentHashMap` ?`size()` ?`isEmpty()` 是绝对精确的?* 实际上，在极高并发下，这些方法是基于估算的，以换取更高的性能，它们返回的是一?*近似?*?

- **认为 `synchronized` 一定比 `ConcurrentHashMap` 的方案慢?* ?`ConcurrentHashMap` 的上下文中，`synchronized` 配合 CAS 和锁升级（偏向锁->轻量级锁->重量级锁），在低冲突时性能极佳，方案本身非常先进?

## 总结

`HashMap` 是性能王者但非线程安全；`Hashtable` 是线程安全的"上古遗物"，因全表锁导致性能低下；?`ConcurrentHashMap` 通过**细粒度锁（桶锁）和无?CAS 操作**，在保证线程安全的同时实现了近乎 `HashMap` 的高性能，是现代 Java 并发编程?`Map` 容器的唯一正确选择?

---
> 参考来源：[HashMap、Hashtable ?ConcurrentHashMap 的区别？](https://www.quanxiaoha.com/java-interview/hashmap-vs-hashtable-vs-concurrenthashmap)
