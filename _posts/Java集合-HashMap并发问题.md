---
title: HashMap 用在并发场景中会出现什么问题？
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

1. **线程安全意识** ：面试官不仅仅是想知道 "HashMap 不安全" 这个结论，更是想知道你是否理解具体的并发问题类型（死循环、数据丢失、脏读等），以及这些问题在不同 JDK 版本中的差异。
2. **源码理解深度** ：考察你是否了解 JDK 1.7 头插法导致的死循环根因，以及 JDK 1.8 尾插法为什么 "只是" 数据丢失而不是死循环。
3. **解决方案掌握** ：是否知道 `ConcurrentHashMap` 、 `Collections.synchronizedMap()` 等替代方案，以及它们的适用场景。

## 核心答案

HashMap 是 **非线程安全** 的，在并发场景下会出现以下问题：

| 问题类型 | JDK 1.7 | JDK 1.8 | 严重程度 |
| --- | --- | --- | --- |
| **死循环（CPU 100%）** | ✅ 会发生 | ❌ 已修复 | ⚠️⚠️⚠️ 致命 |
| **数据丢失** | ✅ 会发生 | ✅ 会发生 | ⚠️⚠️ 严重 |
| **数据覆盖** | ✅ 会发生 | ✅ 会发生 | ⚠️⚠️ 严重 |
| **脏读/不可见** | ✅ 会发生 | ✅ 会发生 | ⚠️ 一般 |
| **size 不准确** | ✅ 会发生 | ✅ 会发生 | ⚠️ 一般 |

**一句话总结** ：JDK 1.7 并发扩容会死循环，JDK 1.8 会数据丢失， **任何版本都不要在并发场景使用 HashMap** ，请用 `ConcurrentHashMap` 。

## 深度解析

### 一、JDK 1.7 死循环问题（经典面试题）

这是 HashMap 最臭名昭著的并发问题：

上图展示了 JDK 1.7 死循环的形成过程。关键点理解：

* **头插法是根源** ：JDK 1.7 的 `transfer()` 方法使用头插法迁移元素，导致链表顺序反转
* **并发竞态条件** ：两个线程同时扩容，一个记录了旧指针后被挂起，另一个完成了迁移
* **指针错乱** ：线程 1 恢复时，基于旧的 `next` 指针操作，但实际链表已经被线程 2 改变
* **形成环** ：A.next 指向 B，B.next 指向 A，形成环形链表

**死循环的触发** ：当后续操作（ `get()` 、 `put()` 、 `remove()` ）需要遍历这个桶时，会陷入 `while (e != null)` 的死循环，CPU 飙升至 100%，服务无法响应。

### 二、JDK 1.8 数据覆盖问题

JDK 1.8 改用尾插法，解决了死循环，但仍有并发问题：

上图展示了 JDK 1.8 的数据覆盖问题。关键点：

* **非原子操作** ： `判断桶是否为空` 和 `写入新节点` 是两个独立步骤，不是原子操作
* **竞态窗口** ：两个线程都判断桶为空后，后写入的线程会覆盖先写入的数据
* **数据丢失** ：被覆盖的数据永久丢失，且不会有任何异常提示

**JDK 1.8 其他并发问题** ：

### 三、JDK 1.7 vs JDK 1.8 并发问题对比

上图对比了两个版本的核心差异。理解要点：

* **JDK 1.7 更危险** ：死循环会导致整个服务不可用，是最致命的问题
* **JDK 1.8 不安全** ：虽然不会死循环，但数据丢失同样不可接受
* **共同点** ：两个版本都不是线程安全的，都不应该在并发场景使用

### 四、正确的替代方案

| 方案 | 实现原理 | 性能 | 适用场景 |
| --- | --- | --- | --- |
| `ConcurrentHashMap` | CAS + synchronized（JDK 1.8） | ⭐⭐⭐⭐⭐ | **首选方案** ，高并发 |
| `Collections.synchronizedMap()` | 全表 synchronized | ⭐⭐ | 低并发，简单场景 |
| `Hashtable` | 全表 synchronized | ⭐ | 遗留代码，不推荐 |

```
// ✅ 推荐方案 1：ConcurrentHashMap（首选）
Map<String, String> map = new ConcurrentHashMap<>();

// ✅ 推荐方案 2：Collections.synchronizedMap（低并发可用）
Map<String, String> map = Collections.synchronizedMap(new HashMap<>());

// ❌ 错误用法：直接用 HashMap
Map<String, String> map = new HashMap<>();  // 并发会出问题！
```

### 五、ConcurrentHashMap 为什么安全？

## 面试高频追问

1. **为什么 JDK 1.8 改用尾插法？**

   * 保持链表顺序不变，避免并发扩容时形成环形链表
   * 但这只是解决了死循环，并没有解决线程安全问题
2. **ConcurrentHashMap 和 Hashtable 的区别？**

   * `Hashtable` 用 synchronized 锁整个表，性能差
   * `ConcurrentHashMap` 只锁单个桶，并发度高
   * `Hashtable` 不允许 null 键值， `ConcurrentHashMap` 也不允许
3. **Collections.synchronizedMap 和 ConcurrentHashMap 怎么选？**

   * 低并发场景：两者都可以
   * 高并发场景：必须用 `ConcurrentHashMap` ，性能差距明显

## 常见面试变体

* "HashMap 为什么不是线程安全的？"
* "JDK 1.7 HashMap 死循环是怎么形成的？"
* "ConcurrentHashMap 如何保证线程安全？"
* "HashMap 和 Hashtable 的区别？"

## 记忆口诀

**JDK 1.7** ：头插扩容会反转，并发形成环形链，CPU 飙升服务挂。

**JDK 1.8** ：尾插顺序不变了，死循环虽修复，数据覆盖仍存在。

**解决方案** ：并发就用 `ConcurrentHashMap` ，锁粒度细性能高。

## 总结

HashMap 在并发场景下，JDK 1.7 会因头插法导致 **死循环** （CPU 100%），JDK 1.8 虽用尾插法避免了死循环，但仍存在 **数据覆盖/丢失** 问题。 **任何版本的 HashMap 都不是线程安全的** ，并发场景必须使用 `ConcurrentHashMap` ，它通过 CAS + 桶级 synchronized 实现高并发安全。
