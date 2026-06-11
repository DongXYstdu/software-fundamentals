---
title: ConcurrentHashMap 为什么在 JDK 1.8 中废弃分段锁
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---

## 面试考察?

1. **架构演进理解**：面试官不仅仅是想知?"废弃? 这个事实，更是想知道你是否理解分段锁的设计局限性，以及 JDK 1.8 新方案解决了哪些问题?

2. **性能权衡思维**：考察你是否理解锁粒度、内存开销、并发度之间的权衡，以及为什?"更简单的 synchronized" 反而比 "复杂?ReentrantLock" 更好?

3. **JVM 优化认知**：是否了?JDK 1.6 ?synchronized 的锁升级机制，以及它如何改变了并发编程的最佳实践?

## 核心答案

JDK 1.8 废弃分段锁的主要原因?*分段锁并发度固定、内存开销大、实现复?*，?**CAS + synchronized** 方案并发度更高、内存更省、实现更简洁：

| 对比维度 | JDK 1.7 分段?| JDK 1.8 CAS + synchronized |
|---|---|---|
| **并发?* | 最?16（Segment 数量?| 等于桶数量（默认 16，可扩容?|
| **锁粒?* | 一?Segment 锁多个桶 | 一个锁只锁一个桶 |
| **内存开销** | 每个 Segment 独立对象 | 无额外锁对象 |
| **扩容灵活?* | Segment 数量固定 | 桶数量动态增?|
| **实现复杂?* | 复杂（双重哈希、Segment 管理?| 简洁（直接操作桶） |

**一句话总结**：分段锁?"中间粒度" 的妥协方案，CAS + synchronized 实现?"最细粒? 的完美方案，并发度更高、内存更省?

## 深度解析

### 一、分段锁的设计局限?

![](https://aka.doubaocdn.com/s/27ew1wZNnn)

上图详细展示了分段锁的三大局限。关键理解：

- **并发度固?*：Segment 数量在创建时确定，无法随 HashMap 扩容而增加。当桶数量从 16 增长?65536 时，仍然只有 16 把锁，每把锁保护的桶?1 个变?4096 个，竞争加剧?
- **内存浪费**：每?Segment 都是一个完整的 "?HashMap"，包含独立的数组、计数器、锁状态等，比单纯?Node 数组多消耗不少内存?
- **两次哈希**：先定位 Segment，再定位桶，增加了计算开销和代码复杂度?

### 二、CAS + synchronized 的优?

![](https://aka.doubaocdn.com/s/mTae1wZNnn)

上图展示?JDK 1.8 新方案的四大优势。核心价值：

- **并发度动态增?*：随着 HashMap 扩容，并发度自动提升，理论上无上?
- **锁粒度最?*：只锁当前操作的桶，不同桶完全并?
- **内存更省**：去掉了 Segment 中间层，直接操作 Node 数组
- **读无?*：利?volatile 可见性，读操作完全不需要加?

### 三、为什么用 synchronized 而不?ReentrantLock?

![](https://aka.doubaocdn.com/s/PMHQ1wZNnn)

上图解释了为什么选择 synchronized。关键点?

- **JDK 1.6 的锁升级**：synchronized 不再?"重量级锁" 的代名词，在低竞争时性能接近 CAS
- **内存开销**：如?65536 个桶都用 ReentrantLock，需?65536 ?Lock 对象，内存开销巨大
- **自动释放**：synchronized 不需要手动释放，代码更简洁，不会忘记 unlock

### 四、性能对比实测

![](https://aka.doubaocdn.com/s/TQKg1wZNnn)

### 五、源码对?

```java
// ==================== JDK 1.7 分段锁实现（简化）====================
public V put(K key, V value) {
    if (value == null)
        throw new NullPointerException();
    int hash = hash(key.hashCode());
    // 1. 定位 Segment（第一次哈希）
    int segmentIndex = (hash >>> segmentShift) & segmentMask;
    Segment<K,V> segment = segments[segmentIndex];
    // 2. ?Segment 内部 put（第二次哈希?
    return segment.put(key, hash, value, false);
}

static final class Segment<K,V> extends ReentrantLock {
    transient volatile HashEntry<K,V>[] table;

    V put(K key, int hash, V value, boolean onlyIfAbsent) {
        // 3. 获取 Segment 的锁
        lock();
        try {
            // 4. ?Segment 内部定位?
            int index = hash & (tab.length - 1);
            HashEntry<K,V> first = tab[index];
            // ... 插入或更?
        } finally {
            unlock();
        }
    }
}

// ==================== JDK 1.8 CAS + synchronized 实现（简化）====================
public V put(K key, V value) {
    int hash = spread(key.hashCode());
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        // 1. 直接定位桶（只有一次哈希）
        if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            // 2. 空桶：CAS 无锁插入
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;
        }
        // 3. 非空桶：synchronized 锁桶?
        else {
            synchronized (f) {
                // ... 插入或更?
            }
            break;
        }
    }
    return null;
}
```

**源码对比总结**?

- JDK 1.7：两层结构（Segment ?HashEntry），需要两次哈希，?Segment
- JDK 1.8：单层结构（Node[]），一次哈希，锁桶头或 CAS 无锁

## 面试高频追问

1. **分段锁在 JDK 1.8 中完全消失了吗？**
    - 是的！JDK 1.8 完全移除?Segment 类，不再有分段锁的概?
    - ?`concurrencyLevel` 参数仍然保留，用于初始化容量估算

2. **synchronized 不会造成性能问题吗？**
    - JDK 1.6 ?synchronized 有锁升级机制，低竞争时性能很好
    - ConcurrentHashMap 中锁的是桶头节点，竞争分散，很少升级到重量级?

3. **CAS 失败后会怎样?*
    - 自旋重试！如果桶仍然为空，继续尝?CAS
    - 如果桶被其他线程占用了，则进?synchronized 分支

## 常见面试变体

- "ConcurrentHashMap ?JDK 1.7 ?1.8 有什么区别？"
- "为什?JDK 1.8 ?synchronized 替代 ReentrantLock?
- "分段锁有什么缺点？"

## 记忆口诀

**分段锁三宗罪**：并发度固定不随容量长、内存浪?Segment 对象多、两次哈希定位效率低?

**新方案四优势**：并发度随容量涨、锁粒度细到桶、内存省去中间层、读操作完全无锁?

**?synchronized**：JDK 1.6 锁升级性能好、无额外对象内存省、自动释放代码简?

## 总结

JDK 1.8 废弃分段锁的核心原因?**并发度固定、内存浪费、实现复?*。

新?**CAS + synchronized** 方案实现?**并发度动态增?*（随容量扩容）?*锁粒度最?*（只锁单个桶）?*内存更省**（无 Segment 中间层）?*读无?*（volatile 保证可见性）。

选择 synchronized 而非 ReentrantLock 是因?JDK 1.6 后的锁升级优化，以及无额外内存开销的优势。

记住：**分段锁是历史的妥协，CAS + synchronized 才是最优解**?

---
> 参考来源：[ConcurrentHashMap 为什么在 JDK 1.8 中废弃分段锁？](https://www.quanxiaoha.com/java-interview/why-concurrenthashmap-removed-segment-lock-jdk8)
