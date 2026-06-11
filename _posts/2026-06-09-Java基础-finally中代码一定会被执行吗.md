---
title: finally 中代码一定会被执行吗
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

1. **异常处理机制理解** ：面试官不仅仅是想知道 "会" 或 "不会"，更是想考察你对 Java 异常处理机制的深入理解，包括 `try-catch-finally` 的执行流程和字节码层面的实现。
2. **边界情况掌握** ：考察你是否了解 `finally` 不执行的特殊场景，如 `System.exit()` 、线程异常终止等，这是区分 "会用" 和 "精通" 的关键点。
3. **代码执行顺序理解** ：看你是否清楚 `finally` 与 `return` 语句的执行顺序，以及 `finally` 中修改返回值的影响，这是常见的面试陷阱。

## 核心答案

**答案是：不一定** 。 `finally` 中的代码在 **绝大多数情况下** 会执行，但存在 **特殊情况** 会导致 `finally` 不执行。

| 场景分类 | finally 是否执行 | 说明 |
| --- | --- | --- |
| 正常执行完 try | ✅ 执行 | 最常见情况 |
| try 中抛出异常 | ✅ 执行 | catch 处理后执行 finally |
| try 中有 return | ✅ 执行 | return 前执行 finally |
| catch 中有 return | ✅ 执行 | return 前执行 finally |
| 调用 `System.exit()` | ❌ **不执行** | JVM 直接退出 |
| 线程死亡 | ❌ **不执行** | 线程被杀死 |
| 断电/系统崩溃 | ❌ **不执行** | 物理层面的不可抗力 |
| 死循环/死锁 | ⏸️ 无法到达 | 理论上会执行，但永远到不了 |

**一句话概括** ：只要 JVM 正常运行且线程存活， `finally` 就一定会执行。

## 深度解析

### 一、finally 的正常执行场景

在绝大多数情况下， `finally` 都会执行。无论 `try` 块中是正常执行、抛出异常，还是有 `return` 语句。

上图展示了 `finally` 的正常执行流程。无论从 `try` 块的哪个路径出来（正常完成、异常抛出、return 返回），都会先经过 `finally` 块。

```
// 场景一：正常执行
public void normalCase() {
    try {
        System.out.println("try 执行");
    } finally {
        System.out.println("finally 执行");  // ✅ 会执行
    }
}

// 场景二：抛出异常
public void exceptionCase() {
    try {
        throw new RuntimeException("异常");
    } catch (RuntimeException e) {
        System.out.println("catch 处理异常");
    } finally {
        System.out.println("finally 执行");  // ✅ 会执行
    }
}

// 场景三：try 中有 return
public int returnInTry() {
    try {
        return 1;
    } finally {
        System.out.println("finally 执行");  // ✅ 会执行（在 return 之前）
    }
}
```

### 二、finally 不执行的特殊场景

虽然 `finally` 几乎总会执行，但以下几种情况 **不会执行** ：

上图列出了 `finally` 不执行的所有场景，下面详细说明：

* **`System.exit()` 调用** ：这是最常见的 `finally` 不执行场景。 `System.exit()` 会立即终止 JVM，所有代码都不会继续执行。注意 `System.exit()` 内部调用 `Runtime.getRuntime().exit()` ，会触发 shutdown hooks，但不会执行 finally。
* **线程死亡** ：如果线程在执行 `try` 块时被强制终止（如 `Thread.stop()` ，已废弃）， `finally` 不会执行。但正常的中断（ `interrupt()` ）不会阻止 `finally` 执行。
* **断电/系统崩溃** ：这是物理层面的不可抗力，JVM 进程被强制终止，所有代码都无法执行。
* **`finally` 块本身抛出异常** ： `finally` 会开始执行，但如果 `finally` 块内部抛出未捕获的异常， `finally` 剩余的代码不会执行，异常会向外传播。

```
// System.exit() 导致 finally 不执行
public void exitCase() {
    try {
        System.out.println("try");
        System.exit(0);        // JVM 退出
    } finally {
        System.out.println("finally");  // ❌ 不会执行
    }
}

// 即使在 catch 中调用 exit 也不行
public void exitInCatch() {
    try {
        throw new RuntimeException();
    } catch (Exception e) {
        System.exit(0);        // JVM 退出
    } finally {
        System.out.println("finally");  // ❌ 不会执行
    }
}
```

### 三、finally 与 return 的执行顺序

这是面试中的高频考点，需要理解 `finally` 和 `return` 的执行顺序。

上图展示了 `finally` 与 `return` 的执行顺序，关键点在于：

* **返回值在 `finally` 执行前就已经计算并存储** ：Java 会把 `return` 的值存入临时变量
* **`finally` 执行后，使用之前存储的返回值** ：即使 `finally` 修改了局部变量，返回值也不变
* **唯一例外** ： `finally` 中有新的 `return` 语句，会覆盖原来的返回值

```
// 经典面试题：返回值是多少？
public int test1() {
    int x = 1;
    try {
        return x;  // 返回值已经确定为 1，存入临时变量
    } finally {
        x = 100;   // 修改 x，但不影响返回值
    }
}
// 调用 test1() 返回：1（不是 100！）

// 引用类型的情况
public int[] test2() {
    int[] arr = {1, 2, 3};
    try {
        return arr;  // 返回的是数组引用
    } finally {
        arr[0] = 100;  // 修改数组内容
    }
}
// 调用 test2() 返回：[100, 2, 3]
// 因为返回的是引用，引用没变，但数组内容被修改了
```

### 四、finally 中的 return：强烈不推荐

虽然可以在 `finally` 中使用 `return` ，但这是 **极其糟糕的实践** ，会导致多个问题：

```
// finally 中的 return 会覆盖 try/catch 的 return
public int badPractice() {
    try {
        return 1;
    } finally {
        return 2;  // ⚠️ 覆盖了 try 中的 return 1
    }
}
// 调用结果：2

// finally 中的 return 会吞掉异常！
public int swallowException() {
    try {
        throw new RuntimeException("异常");
    } finally {
        return 2;  // ⚠️ 异常被吞掉，外部无法感知
    }
}
// 调用结果：2，异常消失了！

// finally 中抛出异常会覆盖原来的异常
public int overrideException() throws Exception {
    try {
        throw new Exception("原始异常");
    } finally {
        throw new Exception("finally 异常");  // 覆盖了原始异常
    }
}
// 抛出的是 "finally 异常"，原始异常丢失
```

**最佳实践** ： **永远不要在 `finally` 块中使用 `return` 语句** 。这会导致代码难以理解和调试，还会吞掉异常。

### 五、字节码层面的理解

从字节码层面看， `finally` 的实现原理是将 `finally` 块的代码复制到所有可能的出口路径上：

```
// 源代码
public void test() {
    try {
        doSomething();
    } finally {
        cleanup();
    }
}

// 编译后等价于（简化版）
public void test() {
    try {
        doSomething();
        cleanup();  // 正常路径
    } catch (Throwable t) {
        cleanup();  // 异常路径
        throw t;
    }
}
```

这也是为什么 `finally` 总会执行——因为它的代码被插入到了所有可能的执行路径中。

## 面试高频追问

1. **`try` 块中有 `return` ， `finally` 还会执行吗？** 会。 `finally` 在 `return` 之前执行，但返回值已经确定。
2. **`finally` 中修改返回值有效吗？** 对于基本类型无效（返回值已存入临时变量），对于引用类型的引用也无效，但可以修改对象内容。
3. **`System.exit()` 和 `return` 有什么区别？** `return` 是方法返回， `finally` 会执行； `System.exit()` 是 JVM 退出， `finally` 不会执行。
4. **为什么不要在 `finally` 中写 `return` ？** 会覆盖原始返回值，还会吞掉异常，导致问题难以排查。

## 常见面试变体

* "什么情况下 `finally` 不会执行？"
* " `try` 里有 `return` ， `finally` 的执行时机是什么？"
* "如果在 `finally` 中修改返回值，会生效吗？"
* " `System.exit(0)` 会影响 `finally` 执行吗？"

## 记忆口诀

**finally 三原则** ：

1. **正常必执行** ：只要 JVM 活着，finally 总会跑
2. **exit 也不行** ：System.exit 一调用，finally 没戏唱
3. **return 前执行** ：return 前先 finally，返回值已定好

## 总结

`finally` 中的代码在 **绝大多数情况下会执行** ，只有在 JVM 退出（ `System.exit()` ）、线程死亡、系统崩溃等极端情况下才不会执行。 `finally` 的执行时机在 `return` 之前，但 `return` 的值在 `finally` 执行前就已确定。 **强烈不建议** 在 `finally` 中使用 `return` ，这会覆盖返回值并吞掉异常。
