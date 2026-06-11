---
title: "String、StringBuilder StringBuffer 的区别？"
date: 2026-06-09 09:00:00 +0800
order: 2
categories: [Java, Java基础]
tags: [Java, 基础, 面试, 小哈学Java]
---
一则或许对你有用的小广告

欢迎 [**加入小哈的星球**](https://www.quanxiaoha.com/column/) ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书

* **《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》** 已完结，基于 `Spring AI + Spring Boot 3.x + JDK 21...`， [**查看介绍**](https://www.quanxiaoha.com/column/10508.html)
* **《从零手撸：仿小红书（微服务架构）》** 已完结，基于 `Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...`， [**查看介绍**](https://www.quanxiaoha.com/column/10247.html) ；演示链接： [**http://116.62.199.48:7070/**](http://116.62.199.48:7070/)
* **《从零手撸：前后端分离博客项目（全栈开发）》** 2 期已完结，演示链接： [**http://116.62.199.48/**](http://116.62.199.48/)
* 新开坑项目： **《从零手撸：秒杀系统高并发优化实战》** 正在更新中...， [**查看介绍**](https://www.quanxiaoha.com/column/10659.html)

截止目前， [星球](https://www.quanxiaoha.com/column/) 内专栏 **累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习** ，欢迎 [**点击围观**](https://www.quanxiaoha.com/column/)

## 面试考察点

1. **基础掌握度** ：面试官不仅仅是想知道这三者的区别，更是想确认你是否理解 Java 字符串的不可变性设计，以及为什么需要 `StringBuilder` 和 `StringBuffer` 。
2. **线程安全意识** ：考察你是否清楚 `StringBuilder` 和 `StringBuffer` 在线程安全上的差异，能否根据业务场景选择合适的类。
3. **性能优化意识** ：是否了解字符串拼接在不同场景下的性能差异，能否写出高性能的字符串处理代码。

## 核心答案

| 对比项 | `String` | `StringBuilder` | `StringBuffer` |
| --- | --- | --- | --- |
| **可变性** | 不可变 | 可变 | 可变 |
| **线程安全** | 安全（不可变） | 不安全 | 安全（ `synchronized` ） |
| **性能** | 拼接差 | 最快 | 较快 |
| **适用场景** | 少量字符串、常量 | 单线程拼接 | 多线程拼接 |
| **出现版本** | JDK 1.0 | JDK 1.5 | JDK 1.0 |

**一句话总结** ：单线程用 `StringBuilder` ，多线程用 `StringBuffer` ，常量用 `String` 。

## 深度解析

### 一、String 的不可变性

`String` 是 Java 中最常用的类之一，它的核心特性是 **不可变（Immutable）** 。

上图展示了 `String` 不可变性的核心原理，整体需要关注以下几点：

* **底层存储** ： `String` 内部使用 `final char[] value` （JDK 9 之后改为 `byte[]` ）存储字符数据， `final` 修饰意味着引用不可变。
* **任何"修改"操作都会创建新对象** ：如拼接、截取、大小写转换等，原对象不变，返回新对象。
* **不可变的好处** ：

  + 线程安全：多个线程可以安全共享，无需同步
  + 字符串常量池优化：相同字符串只存一份
  + 安全性：作为参数传递时不会被修改，适合作为 `HashMap` 的 key

### 二、StringBuilder 与 StringBuffer 的可变性

这两个类都继承自 `AbstractStringBuilder` ，底层是 **可扩容的字符数组** 。

上图展示了可变字符串的工作原理，关键点如下：

* **直接修改内部数组** ： `append()` 、 `insert()` 、 `delete()` 等方法直接操作原数组，不创建新对象。
* **自动扩容** ：当容量不足时，自动扩容为原来的 `2 倍 + 2` ，并将原数据复制到新数组。
* **预分配容量** ：如果能预估最终长度，建议构造时指定容量，避免多次扩容：

  ```
  // 推荐：预估容量，避免扩容
  StringBuilder sb = new StringBuilder(1024);
  ```

### 三、线程安全性对比

上图展示了线程安全实现的核心差异：

* **`StringBuilder`** ：所有方法都没有 `synchronized` 修饰，多线程并发调用可能导致数据错乱。
* **`StringBuffer`** ：几乎所有公共方法都用 `synchronized` 修饰，保证同一时刻只有一个线程能操作。
* **`String`** ：因为不可变，天然线程安全，无需任何同步措施。

### 四、性能对比实验

```
// 测试字符串拼接性能
public class StringPerformanceTest {

    public static void main(String[] args) {
        int count = 100000;

        // 方式一：String 拼接（最慢）
        long start1 = System.currentTimeMillis();
        String s1 = "";
        for (int i = 0; i < count; i++) {
            s1 += i;  // 每次循环都创建新 String 对象
        }
        System.out.println("String: " + (System.currentTimeMillis() - start1) + "ms");

        // 方式二：StringBuilder（最快）
        long start2 = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder(count * 4);  // 预分配容量
        for (int i = 0; i < count; i++) {
            sb.append(i);  // 直接追加，不创建新对象
        }
        System.out.println("StringBuilder: " + (System.currentTimeMillis() - start2) + "ms");

        // 方式三：StringBuffer（略慢于 StringBuilder）
        long start3 = System.currentTimeMillis();
        StringBuffer sbuf = new StringBuffer(count * 4);
        for (int i = 0; i < count; i++) {
            sbuf.append(i);  // 有同步开销
        }
        System.out.println("StringBuffer: " + (System.currentTimeMillis() - start3) + "ms");
    }
}
```

**典型运行结果** （10 万次拼接）：

| 方式 | 耗时 | 说明 |
| --- | --- | --- |
| `String` | ~5000ms | 创建大量临时对象，频繁 GC |
| `StringBuilder` | ~5ms | 直接追加，性能最优 |
| `StringBuffer` | ~8ms | 同步开销约 50% |

### 五、使用场景指南

```
// ✅ 场景一：常量、配置项、少量拼接 → 用 String
String name = "张三";
String greeting = "Hello, " + name;  // 编译器自动优化为 StringBuilder

// ✅ 场景二：单线程大量拼接 → 用 StringBuilder
public String buildSql(List<String> conditions) {
    StringBuilder sql = new StringBuilder("SELECT * FROM user WHERE 1=1");
    for (String condition : conditions) {
        sql.append(" AND ").append(condition);
    }
    return sql.toString();
}

// ✅ 场景三：多线程共享 → 用 StringBuffer
public class LogCollector {
    private StringBuffer logBuffer = new StringBuffer();  // 多线程写入

    public synchronized void addLog(String log) {
        logBuffer.append(log).append("\n");
    }
}

// ❌ 反例：循环中用 String 拼接（性能灾难）
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // 创建 10000 个 String 对象！
}
```

## 面试高频追问

1. **`String s = new String("abc")` 创建了几个对象？**

   分情况讨论：

   * 如果字符串常量池中已存在 `"abc"` ：创建 **1 个** 堆对象
   * 如果字符串常量池中不存在 `"abc"` ：创建 **2 个** 对象（1 个常量池对象 + 1 个堆对象）
2. **为什么 `String` 设计为不可变？**

   * 安全性：防止被恶意修改，适合作为敏感信息存储
   * 线程安全：无需同步，可安全共享
   * 哈希缓存： `hashCode` 只需计算一次，提升 `HashMap` 性能
   * 字符串常量池：相同字符串只存一份，节省内存
3. **`String` 的 `+` 拼接和 `StringBuilder` 的 `append()` 有什么区别？**

   * **编译期常量** ： `"a" + "b" + "c"` 会被编译器直接优化为 `"abc"`
   * **变量拼接** ： `a + b + c` 会被编译器自动转换为 `new StringBuilder().append(a).append(b).append(c).toString()`
   * **循环拼接** ：循环内用 `+` 每次都会创建新的 `StringBuilder` ，性能极差

## 常见面试变体

* "为什么 `String` 是不可变的？有什么好处？"
* " `String s = new String('abc')` 创建了几个对象？"
* "字符串拼接哪种方式性能最好？"
* " `StringBuilder` 和 `StringBuffer` 的区别是什么？"

## 记忆口诀

**可变性** ： `String` 不可变， `Builder` 和 `Buffer` 都可变

**线程安全** ： `Buffer` 有锁安全， `Builder` 无锁快

**使用场景** ：单线程用 `Builder` ，多线程用 `Buffer` ，常量用 `String`

## 总结

`String` 不可变、线程安全但拼接性能差； `StringBuilder` 可变、单线程性能最优； `StringBuffer` 可变、多线程安全但略有同步开销。实际开发中，单线程场景优先使用 `StringBuilder` ，循环拼接必须避免使用 `String` 的 `+` 操作。
