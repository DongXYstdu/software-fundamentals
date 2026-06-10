---
title: "String、StringBuilder �?StringBuffer 的区别？"
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---

## 面试考察�?

面试官提出这个问题，主要想考察以下几个层面的理解：

1. **对字符串核心特性的理解**：面试官不仅想知道它�?"可变或不可变" 的结论，更想考察�?*是否理解 "不可变对�? 的设计意图、内存影响（如字符串常量池）及其带来的线程安全�?*�?

2. **对线程安全概念的掌握及应用能�?*：能否清晰阐述三者线程安全性的差异，并理解�?*实现原理**（如 `StringBuffer` �?`synchronized` 关键字），以及这�?*性能**产生的具体影响�?

3. **性能分析与场景选型能力**：是否能结合实际开发场景（例如循环拼接字符串、高并发字符串处理），分析三者性能差异的根源，并给�?*合理的选择依据和最佳实�?*�?

4. **API 熟悉程度**：虽然问题聚焦区别，但了解它们的主要 API（如 `append`，`toString`）及设计模式（如 Builder 模式）也是加分项�?

## 核心答案

最核心的区别在�?**可变�?* �?**线程安全�?*�?

- **String**�?*不可�?*字符序列。任何修改操作都会生成新�?String 对象。由于其不可变性，它是**线程安全**的�?

- **StringBuilder**（JDK 5+引入）：**可变**字符序列。提供高效的字符串修改操作�?*非线程安�?*，但在单线程环境下性能最高�?

- **StringBuffer**�?*可变**字符序列。功能与 `StringBuilder` 类似，但关键方法�?**`synchronized`** 修饰的，因此�?*线程安全**的，但同步会带来额外的性能开销�?

简单来说：需要字符串常量或少量操作时�?`String`；在单线程环境下进行大量字符串拼接或修改时，优先使用 `StringBuilder`；必须在多线程环境下进行字符串修改时，才使用 `StringBuffer`�?

## 深度解析

### 原理/机制

- **String 的不可变�?*：`String` 类内部使�?`final char[]`（JDK 9 后为 `final byte[]`）存储数据。`final` 使得该引用不可指向新数组，且类没有暴露任何修改此数组内容的方法。这种设计带来了诸多好处�?

    - **安全�?*：作为参数传递时，不用担心被意外修改（如用作 `HashMap` �?key）�?

    - **缓存 HashCode**：`String` �?`hashCode()` 方法会缓存第一次计算的结果，因为值永不变，这提升了像 `HashMap` 这类集合的性能�?

    - **实现字符串常量池**：JVM 可以池化相同的字符串字面量，节省内存�?

- **StringBuilder �?StringBuffer 的可变�?*：两者都继承�?`AbstractStringBuilder`，内部维护一个可变的字符数组 `char[] value`。进�?`append` �?`insert` 等操作时，直接修改该数组的内容，仅在数组容量不足时进行扩容（通常是翻倍），避免了 `String` 每次修改都创建新对象的开销�?

- **线程安全实现**：`StringBuffer` 通过在几乎所有公开方法上添�?`synchronized` 关键字来实现线程安全。�?`StringBuilder` 则没有此修饰，因此在多线程并发修改时，可能导致数据不一致�?

### 代码示例

```java
// 1. String �?修改"代价：产生大量中间对�?
String str = "Hello";
for (int i = 0; i < 1000; i++) {
    // 每次循环都会 new 一个新�?String 对象，效率低�?
    str = str + "World";
}

// 2. StringBuilder 的高效操作（单线程场景）
StringBuilder sb = new StringBuilder("Hello");
for (int i = 0; i < 1000; i++) {
    // 始终在同一�?StringBuilder 对象内操�?
    sb.append("World");
}
String result = sb.toString(); // 只在最后生成一�?String 对象

// 3. StringBuffer 的线程安全操作（多线程场景，但现代开发有更好选择�?
StringBuffer sbf = new StringBuffer();
// 多个线程可以安全地调�?sbf.append(...)，但会因锁竞争影响性能
```

### 对比分析与最佳实�?

| 特�?| String | StringBuilder | StringBuffer |
|---|---|---|---|
| **可变�?* | 不可�?| 可变 | 可变 |
| **线程安全** | 是（天然�?| **�?* | **是（synchronized 实现�?* |
| **性能** | 修改操作最差（大量对象创建�?| **单线程下最�?* | 低于 StringBuilder（有锁开销�?|
| **适用场景** | 字符串常量、少量操作、作为哈希键 | **单线程下大量字符串操�?* | **多线程下大量字符串操�?*（已较少使用�?|

**最佳实践与误区**�?

1. **无脑使用 StringBuilder**：在**单线程、明确需要频繁修改字符串**的场景（如循环体内拼接、动态生�?SQL/JSON 字符串），应优先使用 `StringBuilder`�?

2. **不要�?`+` 号在循环中拼接字符串**：这是最常见的性能陷阱，应使用 `StringBuilder` 替代�?

3. **`StringBuffer` 的现代替代品**：由�?`synchronized` 是粗粒度锁，在高并发下性能不佳。现�?Java 并发编程中，若需线程安全的字符串拼接�?*更推荐使�?`ThreadLocal` 为每个线程分配一�?`StringBuilder`**，或使用无锁类如 `java.util.concurrent` 包下的工具，而非直接使用 `StringBuffer`�?

4. **局部变量原�?*：`StringBuilder` 通常应作�?*方法内的局部变�?*使用。由于其非线程安全，将其作为共享的成员变量是危险的�?

## 总结

理解 `String`（不可变、安全）、`StringBuilder`（可变、高效、非线程安全）和 `StringBuffer`（可变、线程安全、性能有损耗）的核心区别，关键在于结合 **可变性、线程安全和性能** 这三个维度，并根据实际的开发场景做出最合理的选择。在当代 Java 开发中，`StringBuilder` 已成为字符串构建的首选工具�?

---
> 参考来源：[String、StringBuilder �?StringBuffer 的区别？](https://www.quanxiaoha.com/java-interview/string-stringbuilder-stringbuffer-difference)
