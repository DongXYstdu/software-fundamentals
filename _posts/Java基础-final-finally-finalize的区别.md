---
title: final、finally、finalize 的区别？
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

1. **基础知识全面性** ：面试官不仅仅是想知道你能否区分这三个长得像的关键词，更是想考察你对 Java 基础知识的掌握是否全面——从修饰符、异常处理到对象生命周期。
2. **实践应用能力** ：考察你是否在实际项目中正确使用过 `final` （如不可变类、常量定义），是否理解 `finally` 在资源释放中的作用，以及是否知道 `finalize()` 已被废弃。
3. **技术敏感度** ：看你是否关注 Java 版本演进，知道 `finalize()` 从 JDK 9 开始被标记为 `@Deprecated` ，理解其被废弃的原因。

## 核心答案

这三个词虽然名字相似，但 **完全不是一类东西** ：

| 关键词 | 类型 | 作用 | 使用场景 |
| --- | --- | --- | --- |
| `final` | 关键字 | 修饰符，表示 "不可变" | 类、方法、变量 |
| `finally` | 关键字 | 异常处理代码块 | 与 `try-catch` 配合，确保代码执行 |
| `finalize()` | 方法 | 对象回收前的回调 | **已废弃** ，不推荐使用 |

**一句话概括** ： `final` 修饰不可变， `finally` 确保必执行， `finalize()` 回收前调用（已废弃）。

## 深度解析

### 一、final：不可变修饰符

`final` 是 Java 中的修饰符，可以修饰 **类、方法、变量** ，表示 "最终的、不可改变的"。

上图展示了 `final` 的三种使用场景，下面详细说明：

* **修饰类** ：该类不能被继承，所有成员方法隐式变为 `final` （无法重写）。典型应用是 Java 的包装类 `String` 、 `Integer` 等，保证不可变性从而实现线程安全和字符串常量池优化。
* **修饰方法** ：该方法不能被子类重写，但可以重载。常用于模板方法模式中，固定算法骨架不允许子类修改。
* **修饰变量** ：变量只能赋值一次，成为常量。对于基本类型，值不可变；对于引用类型，引用不可变但对象内容可以改变。

```
// final 修饰类：不能继承
final class ImmutableClass {
    private final int value;

    public ImmutableClass(int value) {
        this.value = value;
    }

    // final 修饰方法：不能重写
    public final int getValue() {
        return value;
    }
}

// final 修饰变量
public class FinalDemo {
    // 编译期常量（编译时确定值）
    private static final int MAX_COUNT = 100;

    // 运行期常量（运行时确定值）
    private final int instanceId;

    public FinalDemo(int id) {
        this.instanceId = id;  // 只能赋值一次
    }

    public void demo() {
        final List<String> list = new ArrayList<>();
        list.add("hello");     // ✅ 可以修改对象内容
        // list = new ArrayList<>();  // ❌ 编译错误：引用不可变
    }
}
```

**final 的常见面试陷阱** ：

```
public class FinalTrap {
    public static void main(String[] args) {
        final int[] arr = {1, 2, 3};
        arr[0] = 100;          // ✅ 可以，修改的是数组内容
        // arr = new int[5];   // ❌ 编译错误，引用不可变

        final StringBuilder sb = new StringBuilder("hello");
        sb.append(" world");   // ✅ 可以，修改的是对象内容
        // sb = new StringBuilder();  // ❌ 编译错误，引用不可变
    }
}
```

### 二、finally：异常处理的保障机制

`finally` 是异常处理机制中的关键字，与 `try-catch` 配合使用， **无论是否发生异常， `finally` 块中的代码都会执行** 。

上图展示了 `finally` 的执行时机，关键点在于：

* **无论是否发生异常** ： `finally` 块都会执行
* **即使 `try` 或 `catch` 中有 `return`** ： `finally` 也会在 `return` 之前执行
* **只有一种情况不执行** ：在 `try` 或 `catch` 中调用了 `System.exit()` 导致 JVM 退出

```
// finally 的典型使用场景：资源释放
public class FinallyDemo {

    // 场景一：确保资源关闭
    public void readFile(String path) {
        FileInputStream fis = null;
        try {
            fis = new FileInputStream(path);
            // 读取文件...
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } finally {
            // 无论是否异常，都关闭资源
            if (fis != null) {
                try {
                    fis.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    // 场景二：try-with-resources（JDK 7+，推荐方式）
    public void readFileBetter(String path) {
        try (FileInputStream fis = new FileInputStream(path)) {
            // 读取文件...
            // 无需手动关闭，会自动调用 close()
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**finally 的经典面试题** ：

```
public class FinallyReturn {
    public static int test() {
        try {
            return 1;
        } finally {
            return 2;  // ⚠️ 会覆盖 try 中的 return
        }
    }

    public static void main(String[] args) {
        System.out.println(test());  // 输出：2（不是 1！）
    }
}
```

**重要规则** ：如果 `finally` 中有 `return` 语句，会覆盖 `try` 或 `catch` 中的 `return` 值。但实际开发中 **强烈不建议** 在 `finally` 中使用 `return` 。

### 三、finalize()：已废弃的对象回收回调

`finalize()` 是 `Object` 类中的一个方法，在对象被垃圾回收器回收之前调用。但从 **JDK 9 开始已被标记为 `@Deprecated(forRemoval=true)`** ，计划在未来移除。

上图展示了 `finalize()` 的执行时机，但这个机制存在严重问题：

* **执行时间不确定** ：取决于 GC 的运行，可能很长时间都不执行
* **可能根本不执行** ：程序结束时 GC 可能还没运行
* **性能开销大** ：带有 `finalize()` 的对象需要特殊处理，影响 GC 效率
* **可能导致内存泄漏** ：如果在 `finalize()` 中让对象重新被引用，会导致对象无法被回收
* **不安全** ： `finalize()` 可能被恶意代码利用

```
// finalize() 的使用（不推荐！）
public class FinalizeDemo {

    @Override
    protected void finalize() throws Throwable {
        try {
            // 尝试释放资源
            System.out.println("对象即将被回收");
        } finally {
            super.finalize();
        }
    }
}

// 正确的资源释放方式：实现 AutoCloseable
public class ResourceDemo implements AutoCloseable {
    private FileInputStream fis;

    public void doSomething() {
        // 使用资源...
    }

    @Override
    public void close() throws Exception {
        if (fis != null) {
            fis.close();
        }
    }
}

// 使用方式
try (ResourceDemo resource = new ResourceDemo()) {
    resource.doSomething();
}  // 自动调用 close()
```

### 四、三者对比总结

## 面试高频追问

1. **`final` 修饰的引用类型变量，其内部属性可以修改吗？** 可以。 `final` 只保证引用不可变，对象内容仍可修改。
2. **`finally` 块一定会执行吗？** 几乎一定。唯一例外是 `try` 或 `catch` 中调用了 `System.exit()` ，或者线程/虚拟机异常终止。
3. **为什么 `finalize()` 被废弃了？** 执行时间不确定、性能差、可能导致内存泄漏、可能不执行。推荐使用 `Cleaner` （JDK 9+）或显式的 `close()` 方法。
4. **`try-with-resources` 和 `try-finally` 有什么区别？** `try-with-resources` （JDK 7+）自动调用 `close()` ，代码更简洁，异常处理更合理（不会丢失原始异常）。

## 常见面试变体

* "被 `final` 修饰的变量能修改吗？"
* "finally 和 finalize 有什么区别？"
* "为什么 `finalize()` 方法被废弃了？"
* "try 块中有 return，finally 还会执行吗？"

## 记忆口诀

**final** ：修饰不可变，类法变量三兄弟

**finally** ：异常好搭档，资源释放保平安

**finalize** ：回收前调用，已废弃别再用

**三兄弟区别** ：修饰符、代码块、废弃法，名字像但无关系

## 总结

`final` 、 `finally` 、 `finalize()` 三者除了名字相似外，没有本质联系。 `final` 是修饰符，表示 "不可变"； `finally` 是异常处理机制，确保代码一定执行； `finalize()` 是已废弃的对象回收回调方法。实际开发中， `final` 和 `finally` 经常使用，而 `finalize()` 应该避免使用，改用 `try-with-resources` 或 `Cleaner` 替代。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/Java基础-equals与hashCode重写/'><span class='context-label'>上一篇</span><span class='context-title'>为什么重equals 时一定要重写 hashCode</span></a>
<a class='context-link next' href='/software-fundamentals/posts/Java基础-finally中代码一定会被执行吗/'><span class='context-label'>下一篇</span><span class='context-title'>finally 中代码一定会被执行吗</span></a>
</div>
