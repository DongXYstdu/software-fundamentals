---
title: 什么是 fail-fast？什么是 fail-safe？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---

## 面试考察点

1. **你对 Java 集合框架迭代机制的深入理解程度**。不仅仅是知道概念，更要知道其背后的实现原理。

2. **你对 "并发修改" 这一常见问题的认知和解决方案**。这是实际开发中极易引发 bug 的场景，面试官想知道你是否具备排查和避免此类问题的能力。

3. **你对不同集合类设计哲学和适用场景的掌握**。能否根据 "快速失败" 或 "安全失败" 的特性，为不同并发场景选择合适的集合容器。

## 核心答案

**Fail-Fast（快速失败）** 和 **Fail-Safe（安全失败）** 是描述 Java 集合迭代器（`Iterator`）在面对集合**结构被修改**时，两种不同的行为策略。

- **Fail-Fast**：在迭代过程中，一旦检测到集合的**结构被修改**（通常指添加、删除元素，不包括修改元素内容），会立即抛出 `ConcurrentModificationException` 异常，强制终止迭代。
    - **代表实现**：`ArrayList`、`HashMap`、`HashSet` 等 JDK 1.2 后提供的绝大部分**非线程安全**集合。

- **Fail-Safe**：在迭代过程中，允许集合在结构上被修改。迭代器基于集合的某个"快照"或"视图"进行工作，因此不会抛出 `ConcurrentModificationException`。
    - **代表实现**：`java.util.concurrent` 包下的线程安全集合，如 `CopyOnWriteArrayList`、`ConcurrentHashMap`。注意：`java.util` 包下 `Vector` 的迭代器也非快速失败，但通常不归为此类，更准确的称呼是 **Weakly Consistent（弱一致性）**。

**一句话概括**：Fail-Fast 是 "发现问题立刻报错"，强调即时性和严格性；Fail-Safe 是 "容忍修改，保证过程不中断"，强调可用性和最终一致性。

## 深度解析

### 原理与机制

- **Fail-Fast 原理**：其核心是 **"预期修改次数"校验机制**。在 `ArrayList`、`HashMap` 等集合内部，维护了一个名为 `modCount` 的整型变量。任何会改变集合结构的操作（如 `add`，`remove`）都会使 `modCount` 自增。当创建迭代器时，迭代器会记录下当前的 `modCount` 值为 `expectedModCount`。在每次迭代操作（如 `next()`，`remove()`）前，迭代器都会检查 `modCount` 是否等于 `expectedModCount`。如果不相等，则说明集合在迭代期间被"外部"修改了，便会立即抛出 `ConcurrentModificationException`。

```java
// 以 ArrayList.Itr.next() 的简化逻辑为例
final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

- **Fail-Safe / 弱一致性原理**：其核心是 **"数据快照"或"分离视图"**。
    - **`CopyOnWriteArrayList`**：在迭代器被创建时，会获取底层数组的一个**固定不变的副本（快照）**。之后即使原集合被修改（写操作会复制新数组），迭代器遍历的依然是旧数组，因此不会感知到修改，也绝不会抛出异常。这是典型的"读写分离"思想，代价是内存占用和写性能。
    - **`ConcurrentHashMap`**：其迭代器提供 **"弱一致性"** 保证。它不会抛出异常，但不保证能反映出迭代器创建后发生的所有修改。它的迭代过程可能与数据更新过程交织进行，可能看到、也可能看不到更新的数据。这种设计平衡了性能和数据可见性。

### 代码示例

```java
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

public class FailFastVsFailSafeDemo {
    public static void main(String[] args) {
        System.out.println("=== Fail-Fast 示例 (ArrayList) ===");
        List<String> fastList = new ArrayList<>(Arrays.asList("A", "B", "C"));
        try {
            for (String s : fastList) { // 底层使用迭代器
                System.out.println(s);
                if ("B".equals(s)) {
                    fastList.remove("B"); // 在迭代中直接修改原集合
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("捕获到异常: " + e.getClass());
        }

        System.out.println("\n=== Fail-Safe 示例 (CopyOnWriteArrayList) ===");
        List<String> safeList = new CopyOnWriteArrayList<>(Arrays.asList("A", "B", "C"));
        for (String s : safeList) {
            System.out.println(s);
            if ("B".equals(s)) {
                safeList.remove("B"); // 在迭代中修改原集合
            }
        }
        System.out.println("迭代后集合内容: " + safeList); // 输出 [A, C]
    }
}
```

输出结果：

```
=== Fail-Fast 示例 (ArrayList) ===
A
B
捕获到异常: class java.util.ConcurrentModificationException

=== Fail-Safe 示例 (CopyOnWriteArrayList) ===
A
B
C
迭代后集合内容: [A, C]
```

### 对比分析与最佳实践

| 特性 | Fail-Fast | Fail-Safe / Weakly Consistent |
|---|---|---|
| **设计哲学** | **即时精确**，尽早暴露并发问题，防止数据不一致。 | **可用优先**，容忍并发修改，保证迭代过程顺利完成。 |
| **抛出异常** | 是 (`ConcurrentModificationException`) | 否 |
| **底层数据** | 直接操作原集合引用。 | 基于数据副本或弱一致性视图。 |
| **性能开销** | 每次迭代仅做整数比较，开销极小。 | 可能涉及数据拷贝（如 `CopyOnWriteArrayList`），内存和 CPU 开销较大。 |
| **适用场景** | **单线程环境**，或明确**不会在迭代中修改集合**的多线程环境。 | **高并发读多写少**的场景，允许数据短暂的弱一致性。 |

**最佳实践与常见误区**：

- **不要在 `for-each` 循环中直接修改集合**：`for-each` 循环的本质就是使用迭代器。在 `ArrayList` 的循环中调用 `remove()` 会触发 `fail-fast`。正确的做法是使用迭代器自身的 `remove()` 方法（它会同步更新 `expectedModCount`），或使用 `JDK 8+` 的 `Collection.removeIf()` 方法。

- **根据场景选择集合**：单线程或读操作为主用 `ArrayList`/`HashMap`；高并发写场景用 `ConcurrentHashMap`；读极多写极少且数据量不大时考虑 `CopyOnWriteArrayList`。

- **Fail-Safe 不意味着线程安全**：`Fail-Safe` 描述的是**迭代器行为**。`ConcurrentHashMap` 本身是线程安全的，但如果你在迭代时进行复合操作（如 "检查再执行"），仍然需要额外的同步。`CopyOnWriteArrayList` 的迭代器不反映创建后的修改，这本身也是一种最终一致性。

## 总结

Fail-Fast 和 Fail-Safe 是迭代器面对并发修改的两种对立设计：**Fail-Fast 像严格的哨兵，发现问题立刻警报；Fail-Safe 像宽容的导游，允许变化但保证你的旅程继续**。理解其本质是理解 Java 集合框架并发行为的关键。

---
> 参考来源：[什么是 fail-fast？什么是 fail-safe？](https://www.quanxiaoha.com/java-interview/fail-fast-vs-fail-safe-java)
