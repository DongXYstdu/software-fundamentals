---
title: ConcurrentHashMap 是如何保证线程安全的?
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---

## 面试考察?

1. **版本差异理解**：面试官不仅仅是想知?"用了? 这个结论，更是想知道你是否了?JDK 1.7（分段锁）和 JDK 1.8（CAS + synchronized）两种截然不同的实现方式?

2. **并发原理深度**：考察你是否理?CAS 无锁操作、synchronized 锁升级、volatile 可见性等底层机制，以及它们如何协同工作?

3. **对比分析能力**：能否说清楚 ConcurrentHashMap ?Hashtable、`Collections.synchronizedMap()` 的区别，以及为什么性能更好?

## 核心答案

ConcurrentHashMap ?**JDK 1.8** 中通过 **"CAS + synchronized + volatile"** 三者协同保证线程安全：

| 机制 | 作用 | 应用场景 |
|---|---|---|
| **CAS** | 无锁更新 | 空桶插入、size 计数 |
| **synchronized** | 锁桶头节?| 哈希冲突时的插入/更新/删除 |
| **volatile** | 保证可见?| Node ?val ?next 字段 |

**一句话总结**：JDK 1.8 ?**CAS 尝试无锁插入**，失败则 **synchronized 锁单个桶**，配?**volatile 保证可见?*，实现高并发安全?

## 深度解析

### 一、JDK 1.7 vs JDK 1.8 实现对比

![](https://aka.doubaocdn.com/s/cLy01wZNnn)

上图对比了两个版本的核心差异。关键理解：

- **JDK 1.7 分段?*：将数据分成多个 Segment（默?16 个），每?Segment 是一个小?HashMap，用 `ReentrantLock` 保护。并发度受限?Segment 数量?
- **JDK 1.8 桶级?*：放?Segment，直接对每个桶的头节点加锁。并发度等于桶数量，远高于分段锁?
- **为什么改?* 分段锁的 Segment 数量固定，无法动态扩展；桶级锁更细粒度，并发度更高?

### 二、JDK 1.8 put 操作流程

![](https://aka.doubaocdn.com/s/hu0k1wZNnn)

上图展示?`put()` 方法的核心流程。关键点?

- **步骤 2 - CAS 无锁插入**：如果桶为空，用 CAS 操作直接插入，无需加锁，性能最?
- **步骤 3 - 协助扩容**：如果检测到正在扩容，当前线程会帮忙迁移数据
- **步骤 4 - synchronized 锁桶?*：只有桶不为空时才加锁，且只锁当前桶的头节点
- **锁粒?*：不同桶的操作可以完全并发，互不影响

### 三、三大安全机制详?

![](https://aka.doubaocdn.com/s/XMww1wZNnn)

上图详细解释了三大安全机制。关键理解：

- **CAS**：用于无竞争场景，比如空桶插入，不需要阻塞等?
- **synchronized**：用于有竞争场景，但只锁单个桶，不影响其他桶的操?
- **volatile**：保证读操作的可见性，读操作完全无?

### 四、核心源码解?

```java
// ConcurrentHashMap.putVal() 核心逻辑（简化版?
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());

    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;

        // 1. 延迟初始?table
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();

        // 2. 桶为空，CAS 无锁插入
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;  // CAS 成功，插入完?
            // CAS 失败，自旋重?
        }

        // 3. 正在扩容，帮忙迁?
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);

        // 4. 桶不为空，synchronized 锁桶头节?
        else {
            V oldVal = null;
            synchronized (f) {  // 锁桶头节?
                if (tabAt(tab, i) == f) {  // 双重检?
                    // 链表遍历
                    if (fh >= 0) {
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            // 找到相同 key，更?value
                            if (e.hash == hash &&
                                ((ek = e.key) == key ||
                                 (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            // 没找到，尾插新节?
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {
                                pred.next = new Node<K,V>(hash, key, value, null);
                                break;
                            }
                        }
                    }
                    // 红黑树处?..
                }
            }
            // 检查是否需要树?
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);  // 更新 size（CAS + LongAdder 思想?
    return null;
}

// volatile 读操作（Unsafe 类实现）
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>)U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

// CAS 写操?
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                    Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}
```

### 五、与 Hashtable、Collections.synchronizedMap 对比

| 对比?| Hashtable | Collections.synchronizedMap | ConcurrentHashMap |
|---|---|---|---|
| **锁粒?* | 整个?| 整个?| 单个?|
| **锁类?* | synchronized | synchronized | CAS + synchronized |
| **读操?* | 加锁 | 加锁 | 无锁（volatile?|
| **写操?* | 阻塞其他所有操?| 阻塞其他所有操?| 只阻塞同桶操?|
| **并发?* | 1（串行） | 1（串行） | 桶数量（极高?|
| **null 键?* | ?不允?| ?允许? ?null key?| ?不允?|
| **性能** | ?| ?| ⭐⭐⭐⭐?|

![](https://aka.doubaocdn.com/s/0lbF1wZNnn)

### 六、读操作为什么不需要加锁？

```java
// get() 方法：完全无?
public V get(Object key) {
    Node<K,V> e;
    return (e = find(hash(key), key)) == null ? null : e.val;
}

// Node ?val ?next 都是 volatile ?
static class Node<K,V> {
    final int hash;
    final K key;
    volatile V val;           // volatile 保证可见?
    volatile Node<K,V> next;  // volatile 保证可见?
}
```

**为什么读不需要加锁？**

- **volatile 保证可见?*：一个线程修改了 `val` ?`next`，其他线程立即能看到最新?
- **不可变结?*：Node ?`hash` ?`key` ?`final` 的，不会被修?
- **安全发布**：新节点通过 CAS ?synchronized 写入，保证构造完成后再发?

## 面试高频追问

1. **ConcurrentHashMap 能完全替?Hashtable 吗？**
    - 几乎可以！但要注意：ConcurrentHashMap **不允?null 键?*，Hashtable 也不允许
    - 如果代码依赖 null 键值，需要修?

2. **ConcurrentHashMap 的迭代器?fail-fast 还是 fail-safe?*
    - **fail-safe**！迭代时不会?`ConcurrentModificationException`
    - 但可能读?"弱一致? 的数据（迭代期间的修改可能看不到?

3. **size() 方法如何保证准确性？**
    - JDK 1.8 使用 `LongAdder` 思想：分散热点，多个计数器累?
    - 返回的是一?"近似?，在并发环境下不完全准确

4. **为什么用 synchronized 而不?ReentrantLock?*
    - synchronized ?JDK 1.6 后有大量优化（锁升级?
    - 内存开销更小（不需要额外创?Lock 对象?
    - 在低竞争场景性能相当，高竞争场景更省内存

## 常见面试变体

- "ConcurrentHashMap ?Hashtable 的区别？"
- "JDK 1.7 ?1.8 ?ConcurrentHashMap 有什么不同？"
- "ConcurrentHashMap ?get() 需要加锁吗？为什么？"
- "ConcurrentHashMap 如何统计 size?

## 记忆口诀

**JDK 1.8 三大机制**：CAS 先试无锁插，失败 synchronized 锁桶头，volatile 保可见读无锁?

**锁粒?*：只锁桶头不锁表，不同桶并发跑?

**对比**：Hashtable 全表锁性能差，ConcurrentHashMap 桶级锁并发高?

## 总结

ConcurrentHashMap ?JDK 1.8 通过 **CAS + synchronized + volatile** 三者协同保证线程安全：**CAS** 用于空桶无锁插入?*synchronized** 用于哈希冲突时锁单个桶头节点?*volatile** 保证 Node ?val ?next 可见性。与 Hashtable 的全表锁相比，ConcurrentHashMap ?**桶级?* 实现了极高的并发度，**读操作完全无?*。记住：**锁粒度细、读无锁、写只锁?*?

---
> 参考来源：[ConcurrentHashMap 是如何保证线程安全的？](https://www.quanxiaoha.com/java-interview/how-concurrenthashmap-thread-safe)
