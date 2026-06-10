---
title: 为什么重?equals 时一定要重写 hashCode?
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---

## 面试考察?

1. **契约理解**：面试官不仅仅是想知?"要一起重?，更是想考察你是否理?`equals()` ?`hashCode()` 之间?*隐式契约**——相等对象必须有相等的哈希码?

2. **集合框架原理**：这个问题通常?`HashMap`、`HashSet` 的工作原理绑定考察，看你是否理解哈希表如何利用这两个方法进行元素的存储和查找?

3. **实战踩坑**：只重写 `equals()` 不重?`hashCode()` ?Java 开发中最常见?bug 之一，考察你是否在生产环境踩过坑?

## 核心答案

**Java 规定：如果两个对?`equals()` 返回 `true`，那么它们的 `hashCode()` 必须返回相同的值。只重写 `equals()` 不重?`hashCode()` 会违反这个契约，导致 `HashMap`、`HashSet` 等哈希集合工作异常?*

| 场景 | equals() | hashCode() | 结果 |
|---|---|---|---|
| 都不重写 | 比较地址 | 基于地址 | ?符合契约 |
| 只重?equals | 比较内容 | 基于地址（不同） | ?**违反契约** |
| 两者都重写 | 比较内容 | 基于内容（相同） | ?符合契约 |

## 深度解析

### 一、hashCode ?equals 的契约关?

Java ?`Object` 类的规范中定义了 `hashCode()` ?`equals()` 必须遵守?*三条契约**?

1. **一致?*：多次调用同一对象?`hashCode()`，必须返回相同的?
2. **相等则哈希必?*：如?`equals()` 返回 `true`，`hashCode()` 必须返回相同的?
3. **哈希等不一定相?*：`hashCode()` 相同，`equals()` 不一定返?`true`（哈希冲突）

其中**契约二最关键**?

- 如果两个对象 `equals()` 相等，它们的 `hashCode()` **必须**相等
- 反过来不要求：`hashCode()` 相等，`equals()` 不一定相等（这就是哈希冲突）

### 二、HashMap 的查找原?

理解这个问题的关键在于理?`HashMap` 如何使用这两个方法：

- **第一步（定位?*：先调用 `hashCode()` 计算哈希值，确定元素在哪个桶（bucket）中
- **第二步（确认?*：遍历桶内的链表/红黑树，?`equals()` 逐一比对 key
- **顺序很重?*：先 `hashCode` 定位位置，再 `equals` 确认身份

### 三、翻车现场：只重?equals 的后?

```java
import java.util.*;

class Person {
    String name;
    int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // ?重写?equals，比较内?
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }

    // ?没有重写 hashCode，使?Object 默认实现（基于内存地址?
}

public class HashMapBugDemo {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 25);
        Person p2 = new Person("张三", 25);

        // equals 返回 true，说明是"同一??
        System.out.println(p1.equals(p2));  // 输出: true

        // ?hashCode 不同（因为基于内存地址?
        System.out.println(p1.hashCode());  // 输出: 1234567（示例值）
        System.out.println(p2.hashCode());  // 输出: 7654321（示例值，不同！）

        // 问题来了：HashSet 认为 p1 ?p2 是不同的元素?
        Set<Person> set = new HashSet<>();
        set.add(p1);
        set.add(p2);  // 本应去重，但实际添加成功了！

        System.out.println(set.size());  // 输出: 2（期望是 1！）
        // Bug：两?"相等" 的对象被存储了两?
    }
}
```

**问题分析**?

1. `p1.equals(p2)` 返回 `true`，说明逻辑上它们是 "同一个人"
2. ?`p1.hashCode()` ?`p2.hashCode()` 返回不同的值（基于内存地址?
3. `HashSet` 在添?`p2` 时，根据 `hashCode` 找到了不同的桶，没有发现冲突
4. 结果：两?"相等" 的对象被存进?`HashSet`，破坏了集合的语?

### 四、正确姿势：同时重写 equals ?hashCode

```java
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
        // 方式一：手动计算（JDK 7 之前?
        // int result = name != null ? name.hashCode() : 0;
        // result = 31 * result + age;
        // return result;

        // 方式二：使用 Objects 工具类（推荐，JDK 7+?
        return Objects.hash(name, age);
    }
}

public class CorrectHashCodeDemo {
    public static void main(String[] args) {
        Person p1 = new Person("张三", 25);
        Person p2 = new Person("张三", 25);

        System.out.println(p1.equals(p2));     // 输出: true
        System.out.println(p1.hashCode());     // 输出: 同样的?
        System.out.println(p2.hashCode());     // 输出: 同样的?

        Set<Person> set = new HashSet<>();
        set.add(p1);
        set.add(p2);  // hashCode 相同 ?定位到同一个桶 ?equals 比较相等 ?去重

        System.out.println(set.size());  // 输出: 1 ?
    }
}
```

### 五、IDEA 自动生成（最佳实践）

实际开发中，不要手?`equals()` ?`hashCode()`，使?IDE 自动生成?Lombok?

```java
// 方式一：IDEA 自动生成（Alt + Insert ?equals() and hashCode()?

// 方式二：使用 Lombok（推荐）
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
class Person {
    String name;
    int age;
}

// 方式三：Java 14+ record（自动生?equals、hashCode、toString?
record Person(String name, int age) {}
```

## 面试高频追问

1. **为什么选择 31 作为 hashCode 的乘数？**

    - 31 是奇质数，能减少哈希冲突
    - 31 \* i 等价?`(i << 5) - i`，可以用位运算优?
    - 历史原因：`String` ?`hashCode` 用的就是 31，形成了惯例

2. **只重?hashCode 不重?equals 会怎样?*

也会出问题！两个 `hashCode` 相等的对象，`equals` 返回 `false`，会导致 `HashMap` 中出现大量哈希冲突，链表变长，性能下降（但不会破坏正确性）?

3. **两个不相等的对象 hashCode 相同怎么办？**

这叫**哈希冲突**，是允许的。`HashMap` 会用链表/红黑树处理冲突，?`equals()` 区分不同?key?

## 常见面试变体

- 变体一?`HashMap` ?`put` 流程是怎样的？"
- 变体二："`HashSet` 如何保证元素不重复？"
- 变体三："`Objects.hash()` 方法的实现原理是什么？"

## 记忆口诀

**equals 相等，hashCode 必等；hashCode 相等，equals 未必等；只重?equals 不重?hashCode，HashSet 必翻车?*

## 总结

Java 规定相等对象?`hashCode` 必须相等。只重写 `equals()` 不重?`hashCode()` 会违反契约，导致 `HashMap`、`HashSet` 等哈希集合无法正确识别重复元素。实际开发中，使?IDE 自动生成?Lombok ?`@EqualsAndHashCode` 注解，避免手写出错?

---
> 参考来源：[为什么重?equals 时一定要重写 hashCode？](https://www.quanxiaoha.com/java-interview/java-equals-hashcode-zhongxie-why)
