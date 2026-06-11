---
title: finally 中代码一定会被执行吗?
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---

## 面试考察?

面试官提出这个问题，通常意在考察以下几个层面的理解：

1. **?Java 异常处理机制基础知识的掌?*：即 `finally` 块的基本语义和保证执行的承诺?

2. **?JVM 执行流程和程序状态理解的深度**：面试官不仅仅想知道 "? ?"?，更想知?*在何种极端或特定情况下，`finally` 块会 "失约"**，这能反映出候选人是否真正理解程序执行的底层逻辑?

3. **对系统级交互和资源管理的认知**：例如，理解 `System.exit()` 或守护线程等行为如何影响程序的生命周期，这与编写健壮的、尤其是涉及资源清理的代码紧密相关?

4. **实际编程中的严谨?*：是否了解在 `finally` 块中写代码的"最佳实??常见陷阱"，避免因认知盲区引入生产 bug?

## 核心答案

不，`finally` 中的代码**不一定会被执?*。虽然它在绝大多数正常情况下都会执行，但在以下几种特殊情况下，`finally` 块将不会被执行：

1. **?`try` ?`catch` 块中调用?`System.exit(int)` 终止?JVM?*

2. 程序所在的**线程在进?`finally` 之前被意外终?*（例如，调用?`Thread.stop()` 方法，但此方法已被废弃且极其危险）?

3. **守护线程（Daemon Thread?*中，当所有非守护线程结束时，JVM 会立即退出，此时守护线程中的 `finally` 块可能来不及执行?

4. ?`try` ?`catch` 块中遇到?*无限循环**?*死锁**，导致程序无法继续执行到 `finally` 块?

5. 从操作系统层?*强制杀死了 JVM 进程**（例如，?Linux 中使?`kill -9 pid`）?

## 深度解析

### 原理/机制

`finally` ?"一定执? 语义?Java 编译器在**字节码层?*提供的一种保证。编译器会通过生成额外的字节码，将 `finally` 块中的逻辑复制?`try` 块和每个 `catch` 块的 "正常出口" ?"异常出口" 之后。你可以将其想象为，JVM 试图在离开 `try-catch` 作用域前，无论如何都?"绕路" 去执行一?`finally` 中的代码?

然而，这种保证?*?JVM 正常执行流程?*的。上述提到的例外情况，本质上都是**强行终止?JVM 的正常执行流?*，使得程序失去了继续执行任何字节码（包括复制?`finally` 代码）的机会?

### 代码示例

```java
public class FinallyNotExecuteDemo {
    public static void main(String[] args) {
        case1_SystemExit();
        // case2_InfiniteLoop();
    }

    // 情况 1：System.exit() 导致 finally 不执?
    static void case1_SystemExit() {
        try {
            System.out.println("Try block is running.");
            System.exit(0); // JVM 在此处被强制终止
        } finally {
            // 这行将永远不会被打印
            System.out.println("Finally block is running.");
        }
    }

    // 情况 2：无限循环导?finally 无法到达
    static void case2_InfiniteLoop() {
        try {
            System.out.println("Try block is running.");
            while (true) { // 无限循环，程序无法退?try ?
                // 模拟长时间操?
            }
        } finally {
            // 由于无法退?try 块，这行同样永远不会被执?
            System.out.println("Finally block is running.");
        }
    }
}
```

### 最佳实践与注意事项

1. **资源清理首?`try-with-resources`**：对于实现了 `AutoCloseable` 接口的资源（?`InputStream`、`Connection`），JDK 7 引入?`try-with-resources` 语句是比 `try-finally` 更优雅、更安全的方案。它能自动关闭资源，并且抑制的异常信息更完整?

```java
// 优于 try-finally
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 使用资源
} catch (IOException e) {
    // 处理异常
}
```

2. **避免?`finally` 中引入复杂逻辑或可能抛出异常的操作**：`finally` 块中的代码应该力求简单、可靠。如?`finally` 块中抛出了新的异常，它会 "覆盖" ?`try` ?`catch` 块中抛出的异常，导致原始的异常信息丢失，给调试带来巨大困难?

3. **守护线程中的资源管理需特别小心**：避免在守护线程中进行重要的、必须完成的资源清理或状态持久化操作，因为其执行无法得到保证?

### 常见误区

- **误区一?`finally` ?`return` 之后执行"**：这是一种非常普遍但错误的表述?*`finally` 块的执行?`return` 语句之前**。

具体来说，如果 `try` ?`catch` 中有 `return`，JVM 会先将返回值存储在一个临时变量中，然后执?`finally` 块，最后再返回那个临时变量。

即?`finally` 中修改了要返回的变量，对于基本数据类型和不可变对象（?`String`），返回值也不会改变（但对于对象引用，修改对象内部状态是有效的）?

```java
static int testFinallyReturn() {
    int i = 0;
    try {
        return i; // 1. ?i 的?(0) 存入临时?
    } finally {
        i = 10; // 2. 修改 i，但不影响临时槽中的?
        System.out.println("Finally executed. i = " + i);
        // 3. 从临时槽中取出?(0) 返回
    }
}
// 输出：Finally executed. i = 10
// 返回?
```

- **误区二："`finally` 总能进行资源回收"**：如上所述，?`System.exit()` ?JVM 崩溃等情况下，`finally` 中的 `close()` 方法也无力回天。这强调了关键资源需要有外部管理或更健壮的生命周期管理机制?

## 总结

`finally` 块为代码提供了强大的 "最后清? 保障，但其执行的前提?**JVM 能继续维持正常的执行流程**；任何导?JVM 进程被立?"杀? 或执行流被永?"卡住" 的操作，都会使这份保障失效。在现代 Java 开发中，应优先使用 `try-with-resources` 管理资源，并?`finally` 中保持逻辑简单、健壮?

---
> 参考来源：[finally 中代码一定会被执行吗？](https://www.quanxiaoha.com/java-interview/does-finally-always-execute)
