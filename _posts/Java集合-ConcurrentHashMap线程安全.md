---
title: ConcurrentHashMap 是如何保证线程安全的
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

1. **版本差异理解** ：面试官不仅仅是想知道 "用了锁" 这个结论，更是想知道你是否了解 JDK 1.7（分段锁）和 JDK 1.8（CAS + synchronized）两种截然不同的实现方式。
2. **并发原理深度** ：考察你是否理解 CAS 无锁操作、synchronized 锁升级、volatile 可见性等底层机制，以及它们如何协同工作。
3. **对比分析能力** ：能否说清楚 ConcurrentHashMap 与 Hashtable、 `Collections.synchronizedMap()` 的区别，以及为什么性能更好。

## 核心答案

ConcurrentHashMap 在 **JDK 1.8** 中通过 **"CAS + synchronized + volatile"** 三者协同保证线程安全：

| 机制 | 作用 | 应用场景 |
| --- | --- | --- |
| **CAS** | 无锁更新 | 空桶插入、size 计数 |
| **synchronized** | 锁桶头节点 | 哈希冲突时的插入/更新/删除 |
| **volatile** | 保证可见性 | Node 的 val 和 next 字段 |

**一句话总结** ：JDK 1.8 用 **CAS 尝试无锁插入** ，失败则 **synchronized 锁单个桶** ，配合 **volatile 保证可见性** ，实现高并发安全。

## 深度解析

### 一、JDK 1.7 vs JDK 1.8 实现对比

上图对比了两个版本的核心差异。关键理解：

* **JDK 1.7 分段锁** ：将数据分成多个 Segment（默认 16 个），每个 Segment 是一个小的 HashMap，用 `ReentrantLock` 保护。并发度受限于 Segment 数量。
* **JDK 1.8 桶级锁** ：放弃 Segment，直接对每个桶的头节点加锁。并发度等于桶数量，远高于分段锁。
* **为什么改？** 分段锁的 Segment 数量固定，无法动态扩展；桶级锁更细粒度，并发度更高。

### 二、JDK 1.8 put 操作流程

上图展示了 `put()` 方法的核心流程。关键点：

* **步骤 2 - CAS 无锁插入** ：如果桶为空，用 CAS 操作直接插入，无需加锁，性能最优
* **步骤 3 - 协助扩容** ：如果检测到正在扩容，当前线程会帮忙迁移数据
* **步骤 4 - synchronized 锁桶头** ：只有桶不为空时才加锁，且只锁当前桶的头节点
* **锁粒度** ：不同桶的操作可以完全并发，互不影响

### 三、三大安全机制详解

上图详细解释了三大安全机制。关键理解：

* **CAS** ：用于无竞争场景，比如空桶插入，不需要阻塞等待
* **synchronized** ：用于有竞争场景，但只锁单个桶，不影响其他桶的操作
* **volatile** ：保证读操作的可见性，读操作完全无锁

### 四、核心源码解析

```
// ConcurrentHashMap.putVal() 核心逻辑（简化版）
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());

    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;

        // 1. 延迟初始化 table
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();

        // 2. 桶为空，CAS 无锁插入
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;  // CAS 成功，插入完成
            // CAS 失败，自旋重试
        }

        // 3. 正在扩容，帮忙迁移
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);

        // 4. 桶不为空，synchronized 锁桶头节点
        else {
            V oldVal = null;
            synchronized (f) {  // 锁桶头节点
                if (tabAt(tab, i) == f) {  // 双重检查
                    // 链表遍历
                    if (fh >= 0) {
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            // 找到相同 key，更新 value
                            if (e.hash == hash &&
                                ((ek = e.key) == key ||
                                 (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            // 没找到，尾插新节点
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {
                                pred.next = new Node<K,V>(hash, key, value, null);
                                break;
                            }
                        }
                    }
                    // 红黑树处理...
                }
            }
            // 检查是否需要树化
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);  // 更新 size（CAS + LongAdder 思想）
    return null;
}

// volatile 读操作（Unsafe 类实现）
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>)U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

// CAS 写操作
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                    Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}
```

### 五、与 Hashtable、Collections.synchronizedMap 对比

| 对比项 | Hashtable | Collections.synchronizedMap | ConcurrentHashMap |
| --- | --- | --- | --- |
| **锁粒度** | 整个表 | 整个表 | 单个桶 |
| **锁类型** | synchronized | synchronized | CAS + synchronized |
| **读操作** | 加锁 | 加锁 | 无锁（volatile） |
| **写操作** | 阻塞其他所有操作 | 阻塞其他所有操作 | 只阻塞同桶操作 |
| **并发度** | 1（串行） | 1（串行） | 桶数量（极高） |
| **null 键值** | ❌ 不允许 | ✅ 允许（1 个 null key） | ❌ 不允许 |
| **性能** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |

### 六、读操作为什么不需要加锁？

```
// get() 方法：完全无锁
public V get(Object key) {
    Node<K,V> e;
    return (e = find(hash(key), key)) == null ? null : e.val;
}

// Node 的 val 和 next 都是 volatile 的
static class Node<K,V> {
    final int hash;
    final K key;
    volatile V val;           // volatile 保证可见性
    volatile Node<K,V> next;  // volatile 保证可见性
}
```

**为什么读不需要加锁？**

* **volatile 保证可见性** ：一个线程修改了 `val` 或 `next` ，其他线程立即能看到最新值
* **不可变结构** ：Node 的 `hash` 和 `key` 是 `final` 的，不会被修改
* **安全发布** ：新节点通过 CAS 或 synchronized 写入，保证构造完成后再发布

## 面试高频追问

1. **ConcurrentHashMap 能完全替代 Hashtable 吗？**

   * 几乎可以！但要注意：ConcurrentHashMap **不允许 null 键值** ，Hashtable 也不允许
   * 如果代码依赖 null 键值，需要修改
2. **ConcurrentHashMap 的迭代器是 fail-fast 还是 fail-safe？**

   * **fail-safe** ！迭代时不会抛 `ConcurrentModificationException`
   * 但可能读到 "弱一致性" 的数据（迭代期间的修改可能看不到）
3. **size() 方法如何保证准确性？**

   * JDK 1.8 使用 `LongAdder` 思想：分散热点，多个计数器累加
   * 返回的是一个 "近似值"，在并发环境下不完全准确
4. **为什么用 synchronized 而不是 ReentrantLock？**

   * synchronized 在 JDK 1.6 后有大量优化（锁升级）
   * 内存开销更小（不需要额外创建 Lock 对象）
   * 在低竞争场景性能相当，高竞争场景更省内存

## 常见面试变体

* "ConcurrentHashMap 和 Hashtable 的区别？"
* "JDK 1.7 和 1.8 的 ConcurrentHashMap 有什么不同？"
* "ConcurrentHashMap 的 get() 需要加锁吗？为什么？"
* "ConcurrentHashMap 如何统计 size？"

## 记忆口诀

**JDK 1.8 三大机制** ：CAS 先试无锁插，失败 synchronized 锁桶头，volatile 保可见读无锁。

**锁粒度** ：只锁桶头不锁表，不同桶并发跑。

**对比** ：Hashtable 全表锁性能差，ConcurrentHashMap 桶级锁并发高。

## 总结

ConcurrentHashMap 在 JDK 1.8 通过 **CAS + synchronized + volatile** 三者协同保证线程安全： **CAS** 用于空桶无锁插入， **synchronized** 用于哈希冲突时锁单个桶头节点， **volatile** 保证 Node 的 val 和 next 可见性。与 Hashtable 的全表锁相比，ConcurrentHashMap 的 **桶级锁** 实现了极高的并发度， **读操作完全无锁** 。记住： **锁粒度细、读无锁、写只锁桶** 。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/Java集合-ConcurrentHashMap废弃分段锁/'><span class='context-label'>上一篇</span><span class='context-title'>ConcurrentHashMap 为什么在 JDK 1.8 中废弃分段锁</span></a>
<a class='context-link next' href='/software-fundamentals/posts/Java集合-HashMap-Hashtable-ConcurrentHashMap区别/'><span class='context-label'>下一篇</span><span class='context-title'>HashMap、Hashtable ConcurrentHashMap 的区别？</span></a>
</div>
