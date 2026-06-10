---
title: "String str = new String(\"abc\") 创建了几个对象？"
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---

## 面试考察�?

面试官提出这个问题，通常旨在考察候选人以下几个层面的理解：

1. **�?JVM 内存模型（特别是方法�?元空间和堆）的掌�?*：能否清晰区分字符串常量池与堆内存�?

2. **�?`String` 类两种创建方式本质的理解**：明�?`new String(...)` 与字面量赋值的根本区别�?

3. **对字符串常量池（String Pool）机制的理解**：它如何工作，以�?`intern()` 方法的作用�?

4. **严谨的思考逻辑**：能否清晰地分析代码执行时，对象是在何时、于何处创建的�?

## 核心答案

这个问题的答案是�?*1 个或 2 �?*�?

具体来说�?

- **通常情况下，会创�?2 个对象�?*

    - **对象 1 (位于堆中)**：`new String(...)` 会在 Java 堆内存中创建一个新�?`String` 实例对象�?

    - **对象 2 (位于字符串常量池�?**：字面量 `"abc"` 会促�?JVM 在字符串常量池（String Pool）中查找或创建对应的字符串对象�?

- **特殊情况下，只会创建 1 个对象�?*

    - 如果�?**此代码执行之�?*，字符串常量池中已经存在内容�?`"abc"` 的对象（例如，其他代码已经使用过 `"abc"` 字面量或调用�?`"abc".intern()`），那么 `String str = new String("abc")` 中的字面�?`"abc"` 将不会触发新的创建，而只是指向池中已存在的对象。此时，仅会在堆中创�?1 个新�?`String` 对象�?

## 深度解析

### 原理/机制

- **字符串常量池**：是 JVM 为了提升性能和减少内存开销而设计的一块特殊内存区域（�?JDK 7 之前位于方法区，JDK 7 及之后移至堆中）。它的核心机制是 **"驻留（intern�?**。当使用双引号字面量（如 `"abc"`）创建字符串时，JVM 会首先检查常量池中是否存在内容相等的字符串对象�?

    - 如果存在，则直接返回池中对象的引用�?

    - 如果不存在，则在池中创建该对象，并返回其引用�?

- **`new String(String original)` 构造函�?*：这个构造函数的官方文档说明是：`Initializes a newly created String object so that it represents the same sequence of characters as the argument; in other words, the newly created string is a copy of the argument string.` 它的作用�?**在堆上创建一个新�?`String` 对象**，并将参数字符串的字符数组拷贝（或引用，具体实现有优化）过去。因此，`new` 操作必然在堆中产生一个新对象�?

### 代码示例与内存分�?

```java
// 场景一：创�?个对�?
public class StringCreationDemo {
    public static void main(String[] args) {
        // 假设这是程序中第一次出�?"abc"
        String str = new String("abc");
        // 步骤分解�?
        // 1. 字面�?`"abc"` 出现，JVM 检查常量池，无 "abc"，于是在常量池创建对象O1�?
        // 2. `new` 关键字在堆上申请内存，创建新�?String 对象 O2�?
        // 3. 构造函数将 O1 的内容（字符数组）初始化�?O2�?
        // 4. 引用 `str` 指向堆中的对�?O2�?
    }
}

// 场景二：创建1个对�?
public class StringCreationDemo2 {
    public static void main(String[] args) {
        String constant = "abc"; // 此行代码执行后，常量池中已有 "abc" 对象 O_pool
        // ... 其他代码
        String str = new String("abc"); // 此时，字面量 `"abc"` 直接引用已存在的 O_pool，仅在堆上创�?个新对象 O_heap�?
    }
}
```

### 对比分析与最佳实�?

- **`String str = "abc";` vs `String str = new String("abc");`**

    - **字面量方�?*：可能创�?0 �?1 个对象（仅在常量池不存在时创建），且所有字面量相同的引用都指向常量池中同一个对象，**节省内存，性能更优**�?

    - **`new` 方式**：必然在堆上创建新对象（1个），且与常量池中的对象�?**两个不同的对�?*（但 `equals()` �?true）。`str == "abc"` 结果�?`false`�?

- **最佳实�?*：在绝大多数业务开发场景中�?*强烈推荐使用字面量方式（`String s = "abc"`）来创建字符�?*。除非有明确的需求（例如，需要保证得到一个全新的、与其他任何引用都不 `==` 的对象，但这种场景极少），否则应避免使用 `new String(String)` 构造函数，因为它会产生不必要的对象开销�?

### 常见误区

1. **混淆引用和对�?*：变�?`str` 只是一个引用，它本身不是对象。问题问的是 "创建了几个对�?�?

2. **忽略常量池的已存在情�?*：武断地回答 "总是 2 �?，没有考虑常量池的缓存机制�?

3. **混淆 `intern()` 方法的作�?*：`new String("abc").intern()` 这个表达式整体，在常量池已存在时**不会创建新对�?*，它会返回池中对象的引用。此时，堆中新创建的对象在没有其他引用的情况下，稍后会被 GC 回收�?

## 总结

`String str = new String("abc")` �?*大多数首次出现该字面量的情况下会创建 2 个对�?*�?个在常量池，1个在堆），但其根本机制依赖于 **JVM 的字符串常量�?*，在池中已存在对应对象时则只创建 1 个堆对象�?

---
> 参考来源：[String str = new String("abc") 创建了几个对象？](https://www.quanxiaoha.com/java-interview/string-new-abc-create-objects)
