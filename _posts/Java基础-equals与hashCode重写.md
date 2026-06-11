---
title: 为什么重equals 时一定要重写 hashCode
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

1. **契约理解** ：面试官不仅仅是想知道 "要一起重写"，更是想考察你是否理解 `equals()` 和 `hashCode()` 之间的 **隐式契约** ——相等对象必须有相等的哈希码。
2. **集合框架原理** ：这个问题通常和 `HashMap` 、 `HashSet` 的工作原理绑定考察，看你是否理解哈希表如何利用这两个方法进行元素的存储和查找。
3. **实战踩坑** ：只重写 `equals()` 不重写 `hashCode()` 是 Java 开发中最常见的 bug 之一，考察你是否在生产环境踩过坑。

## 核心答案

**Java 规定：如果两个对象 `equals()` 返回 `true` ，那么它们的 `hashCode()` 必须返回相同的值。只重写 `equals()` 不重写 `hashCode()` 会违反这个契约，导致 `HashMap` 、 `HashSet` 等哈希集合工作异常。**

| 场景 | equals() | hashCode() | 结果 |
| --- | --- | --- | --- |
| 都不重写 | 比较地址 | 基于地址 | ✅ 符合契约 |
| 只重写 equals | 比较内容 | 基于地址（不同） | ❌ **违反契约** |
| 两者都重写 | 比较内容 | 基于内容（相同） | ✅ 符合契约 |

## 深度解析

### 一、hashCode 与 equals 的契约关系

Java 在 `Object` 类的规范中定义了 `hashCode()` 和 `equals()` 必须遵守的 **三条契约** ：

上图展示了 `hashCode()` 和 `equals()` 的三大契约。其中 **契约二最关键** ：

* 如果两个对象 `equals()` 相等，它们的 `hashCode()` **必须** 相等
* 反过来不要求： `hashCode()` 相等， `equals()` 不一定相等（这就是哈希冲突）

### 二、HashMap 的查找原理

理解这个问题的关键在于理解 `HashMap` 如何使用这两个方法：

上图展示了 `HashMap` 查找元素的完整流程。关键要点：

* **第一步（定位）** ：先调用 `hashCode()` 计算哈希值，确定元素在哪个桶（bucket）中
* **第二步（确认）** ：遍历桶内的链表/红黑树，用 `equals()` 逐一比对 key
* **顺序很重要** ：先 `hashCode` 定位位置，再 `equals` 确认身份

### 三、翻车现场：只重写 equals 的后果

```
import java.util.*;

class Person {
    String name;
    int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // ✅ 重写了 equals，比较内容
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }

    // ❌ 没有重写 hashCode，使用 Object 默认实现（基于内存地址）
}

public class HashMapBugDemo {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 25);
        Person p2 = new Person("张三", 25);

        // equals 返回 true，说明是"同一个"人
        System.out.println(p1.equals(p2));  // 输出: true

        // 但 hashCode 不同（因为基于内存地址）
        System.out.println(p1.hashCode());  // 输出: 1234567（示例值）
        System.out.println(p2.hashCode());  // 输出: 7654321（示例值，不同！）

        // 问题来了：HashSet 认为 p1 和 p2 是不同的元素！
        Set<Person> set = new HashSet<>();
        set.add(p1);
        set.add(p2);  // 本应去重，但实际添加成功了！

        System.out.println(set.size());  // 输出: 2（期望是 1！）
        // Bug：两个 "相等" 的对象被存储了两次
    }
}
```

**问题分析** ：

1. `p1.equals(p2)` 返回 `true` ，说明逻辑上它们是 "同一个人"
2. 但 `p1.hashCode()` 和 `p2.hashCode()` 返回不同的值（基于内存地址）
3. `HashSet` 在添加 `p2` 时，根据 `hashCode` 找到了不同的桶，没有发现冲突
4. 结果：两个 "相等" 的对象被存进了 `HashSet` ，破坏了集合的语义

### 四、正确姿势：同时重写 equals 和 hashCode

```
import java.util.*;

class Person {
    String name;
    int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        // 方式一：手动计算（JDK 7 之前）
        // int result = name != null ? name.hashCode() : 0;
        // result = 31 * result + age;
        // return result;

        // 方式二：使用 Objects 工具类（推荐，JDK 7+）
        return Objects.hash(name, age);
    }
}

public class CorrectHashCodeDemo {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 25);
        Person p2 = new Person("张三", 25);

        System.out.println(p1.equals(p2));     // 输出: true
        System.out.println(p1.hashCode());     // 输出: 同样的值
        System.out.println(p2.hashCode());     // 输出: 同样的值

        Set<Person> set = new HashSet<>();
        set.add(p1);
        set.add(p2);  // hashCode 相同 → 定位到同一个桶 → equals 比较相等 → 去重

        System.out.println(set.size());  // 输出: 1 ✅
    }
}
```

### 五、IDEA 自动生成（最佳实践）

实际开发中，不要手写 `equals()` 和 `hashCode()` ，使用 IDE 自动生成或 Lombok：

```
// 方式一：IDEA 自动生成（Alt + Insert → equals() and hashCode()）

// 方式二：使用 Lombok（推荐）
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
class Person {
    String name;
    int age;
}

// 方式三：Java 14+ record（自动生成 equals、hashCode、toString）
record Person(String name, int age) {}
```

## 面试高频追问

1. **为什么选择 31 作为 hashCode 的乘数？**

   * 31 是奇质数，能减少哈希冲突
   * 31 \* i 等价于 `(i << 5) - i` ，可以用位运算优化
   * 历史原因： `String` 的 `hashCode` 用的就是 31，形成了惯例
2. **只重写 hashCode 不重写 equals 会怎样？**

   也会出问题！两个 `hashCode` 相等的对象， `equals` 返回 `false` ，会导致 `HashMap` 中出现大量哈希冲突，链表变长，性能下降（但不会破坏正确性）。
3. **两个不相等的对象 hashCode 相同怎么办？**

   这叫 **哈希冲突** ，是允许的。 `HashMap` 会用链表/红黑树处理冲突，用 `equals()` 区分不同的 key。

## 常见面试变体

* 变体一：" `HashMap` 的 `put` 流程是怎样的？"
* 变体二：" `HashSet` 如何保证元素不重复？"
* 变体三：" `Objects.hash()` 方法的实现原理是什么？"

## 记忆口诀

**equals 相等，hashCode 必等；** **hashCode 相等，equals 未必等；** **只重写 equals 不重写 hashCode，HashSet 必翻车。**

## 总结

Java 规定相等对象的 `hashCode` 必须相等。只重写 `equals()` 不重写 `hashCode()` 会违反契约，导致 `HashMap` 、 `HashSet` 等哈希集合无法正确识别重复元素。实际开发中，使用 IDE 自动生成或 Lombok 的 `@EqualsAndHashCode` 注解，避免手写出错。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/Java基础-UUID与唯一性/'><span class='context-label'>上一篇</span><span class='context-title'>什么是 UUID，能保证唯一性吗</span></a>
<a class='context-link next' href='/software-fundamentals/posts/Java基础-final-finally-finalize的区别/'><span class='context-label'>下一篇</span><span class='context-title'>final、finally、finalize 的区别？</span></a>
</div>
