---
title: Java中的集合类有哪些？如何分类的
date: 2026-06-09 09:00:00 +0800
order: 2
categories: [Java, Java集合]
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

1. **体系结构认知** ：面试官不仅仅想知道你能背出几个集合类名，更想考察你是否理解 Java 集合框架的整体设计思想，能否从接口到实现有一个清晰的层次认知。
2. **选型能力** ：考察你是否了解不同集合类的特性差异，能否根据实际场景（有序、唯一、排序、线程安全等）选择合适的实现类。
3. **深度与广度** ：这道题是 "开门题"，面试官通常会根据你的回答深入追问某个具体集合的原理，比如 `HashMap` 的扩容机制、 `ConcurrentHashMap` 的线程安全实现等。

## 核心答案

Java 集合框架主要分为 **两大体系** ： `Collection` 和 `Map` 。

上图展示了 Java 集合框架的整体架构，分为两大核心体系：

* **Collection 体系** ：存储单列元素，根据特性细分为 `List` （有序可重复）、 `Set` （无序唯一）、 `Queue` （队列）三大接口。
* **Map 体系** ：存储键值对（Key-Value），通过 Key 快速查找 Value，Key 必须唯一。

## 深度解析

### 一、Collection 体系详解

**1. List 接口 - 有序可重复**

| 实现类 | 底层结构 | 线程安全 | 特点 | 适用场景 |
| --- | --- | --- | --- | --- |
| `ArrayList` | 动态数组 | ❌ | 查询 O(1)，尾部增删 O(1) | 大多数场景首选 |
| `LinkedList` | 双向链表 | ❌ | 头部增删 O(1)，查询 O(n) | 频繁头部增删 |
| `Vector` | 动态数组 | ✅ | 全表 `synchronized` 锁 | 已淘汰 |
| `Stack` | 动态数组 | ✅ | 继承 Vector，后进先出 | 已淘汰，用 `ArrayDeque` |

**2. Set 接口 - 无序唯一**

| 实现类 | 底层结构 | 有序性 | 特点 |
| --- | --- | --- | --- |
| `HashSet` | 哈希表 | ❌ 无序 | 性能最高，基于 `HashMap` |
| `LinkedHashSet` | 哈希表 + 链表 | ✅ 插入有序 | 保持插入顺序 |
| `TreeSet` | 红黑树 | ✅ 排序有序 | 支持自然排序或自定义排序 |

**3. Queue 接口 - 队列**

| 实现类 | 类型 | 特点 |
| --- | --- | --- |
| `LinkedList` | 双端队列 | 可作为队列、栈、列表使用 |
| `ArrayDeque` | 双端队列 | 循环数组实现，性能优于 `LinkedList` |
| `PriorityQueue` | 优先队列 | 按优先级出队，非线程安全 |
| `ArrayBlockingQueue` | 阻塞队列 | 有界，线程安全，生产者消费者模型 |
| `LinkedBlockingQueue` | 阻塞队列 | 可选有界/无界，线程安全 |

### 二、Map 体系详解

| 实现类 | 底层结构 | 线程安全 | null 键/值 | 特点 |
| --- | --- | --- | --- | --- |
| `HashMap` | 数组 + 链表/红黑树 | ❌ | ✅/✅ | 最常用，性能最高 |
| `LinkedHashMap` | `HashMap` + 双向链表 | ❌ | ✅/✅ | 保持插入顺序或 LRU 顺序 |
| `TreeMap` | 红黑树 | ❌ | ❌/✅ | 按键排序，支持范围查询 |
| `Hashtable` | 数组 + 链表 | ✅ | ❌/❌ | 全表锁，已淘汰 |
| `ConcurrentHashMap` | 数组 + 链表/红黑树 | ✅ | ❌/❌ | 高并发首选，细粒度锁 |
| `WeakHashMap` | 弱引用哈希表 | ❌ | ✅/✅ | Key 可被 GC 回收 |

### 三、如何选择合适的集合

### 四、常见误区

**误区一：Vector 和 Hashtable 还在生产使用**

```
// ❌ 错误：使用过时的同步集合
List<String> list = new Vector<>();
Map<String, String> map = new Hashtable<>();

// ✅ 正确：使用并发包中的集合
List<String> list = new CopyOnWriteArrayList<>();
Map<String, String> map = new ConcurrentHashMap<>();
```

**误区二：HashSet 真的 "无序" 吗？**

`HashSet` 的 "无序" 指的是不保证插入顺序，但实际遍历顺序由哈希值决定，在同一次运行中顺序是稳定的。

**误区三：LinkedList 比 ArrayList 插入快？**

只有在头部插入时 `LinkedList` 才更快，尾部插入 `ArrayList` 更快（无指针开销），中间插入两者都是 O(n)。

## 面试高频追问

1. **ArrayList 和 LinkedList 的区别？**

   * 底层结构、时间复杂度、内存占用、适用场景
2. **HashMap 的底层原理？**

   * 数组 + 链表 + 红黑树，扩容机制，哈希冲突解决
3. **ConcurrentHashMap 如何保证线程安全？**

   * JDK 7 分段锁 vs JDK 8 CAS + `synchronized`

## 常见面试变体

* "List、Set、Map 三者的区别？"
* "哪些集合是线程安全的？"
* "如何选择使用哪个集合类？"

## 记忆口诀

**Collection 三剑客** ：

* **List** ：有序可重复，像排队
* **Set** ：无序要唯一，像身份证号
* **Queue** ：先进先出，像排队买票

**Map 选择口诀** ：

## 总结

Java 集合框架分为 `Collection` （单列）和 `Map` （双列）两大体系。 `Collection` 下分 `List` （有序可重复）、 `Set` （无序唯一）、 `Queue` （队列）三类； `Map` 存储键值对，核心实现包括 `HashMap` 、 `LinkedHashMap` 、 `TreeMap` 、 `ConcurrentHashMap` 。选型时根据 "有序性、唯一性、线程安全、排序需求" 四个维度判断，日常开发 `ArrayList` + `HashMap` 覆盖 90% 场景。
