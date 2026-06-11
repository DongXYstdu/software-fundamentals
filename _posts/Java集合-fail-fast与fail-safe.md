---
title: 什么是 fail-fast？什么是 fail-safe
date: 2026-06-09 09:00:00 +0800
order: 2
categories: [Java, Java集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
一则或许对你有用的小广告

欢迎 [**加入小哈的星球**](https://www.quanxiaoha.com/column/) ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书

* **《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》** 已完结，基于 `Spring AI + Spring Boot 3.x + JDK 21...`， [**查看介绍**](https://www.quanxiaoha.com/column/10508.html)
* **《从零手撸：仿小红书（微服务架构）》** 已完结，基于 `Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...`， [**查看介绍**](https://www.quanxiaoha.com/column/10247.html) ；演示链接： [**http://116.62.199.48:7070/**](http://116.62.199.48:7070/)
* **《从零手撸：前后端分离博客项目（全栈开发）》** 2 期已完结，演示链接： [**http://116.62.199.48/**](http://116.62.199.48/)
* 新开坑项目： **《从零手撸：秒杀系统高并发优化实战》** 正在更新中...， [**查看介绍**](https://www.quanxiaoha.com/column/10659.html)

截止目前， [星球](https://www.quanxiaoha.com/column/) 内专栏 **累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习** ，欢迎 [**点击围观**](https://www.quanxiaoha.com/column/)

## 面试考察点

1. **异常处理经验** ：面试官不仅仅是想知道这两个概念的定义，更是想知道你是否遇到过 `ConcurrentModificationException` ，以及是否理解它的产生原因。
2. **迭代器原理** ：考察你是否了解 Java 集合迭代器的工作机制，特别是 `modCount` 的检测机制。
3. **并发安全意识** ：是否知道在多线程或单线程迭代时修改集合的正确姿势，以及 `CopyOnWriteArrayList` 等并发集合的应用。

## 核心答案

**fail-fast（快速失败）** 和 **fail-safe（安全失败）** 是 Java 集合迭代器在遇到并发修改时的两种不同处理策略：

| 特性 | fail-fast | fail-safe |
| --- | --- | --- |
| **行为** | 检测到修改立即抛异常 | 检测到修改不抛异常，继续迭代 |
| **异常** | `ConcurrentModificationException` | 无异常 |
| **迭代方式** | 直接遍历原集合 | 遍历集合的副本 |
| **内存开销** | 低 | 高（需要复制） |
| **数据一致性** | 强一致性（失败即停止） | 弱一致性（可能读到旧数据） |
| **代表集合** | `ArrayList` 、 `HashMap` 、 `HashSet` | `CopyOnWriteArrayList` 、 `ConcurrentHashMap` |

**一句话总结** ：fail-fast **立即抛异常** 保护数据一致性，fail-safe **迭代副本** 保证不抛异常但可能读到旧数据。

## 深度解析

### 一、fail-fast 机制原理

上图展示了 fail-fast 的核心检测机制。关键点：

* **modCount** ：集合内部的修改计数器，每次 `add()` 、 `remove()` 等结构性修改都会 `modCount++`
* **expectedModCount** ：迭代器创建时记录的 modCount 快照
* **检测时机** ：每次调用 `next()` 、 `hasNext()` 、 `remove()` 时都会检查
* **不等即异常** ： `modCount != expectedModCount` 说明集合在迭代期间被修改过

### 二、fail-fast 代码示例

```
// fail-fast 异常示例
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add("C");

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    if ("B".equals(element)) {
        list.remove(element);  // ❌ 通过集合直接删除，触发 fail-fast
    }
}
// 运行结果：java.util.ConcurrentModificationException

// ✅ 正确方式 1：使用迭代器的 remove()
Iterator<String> iterator2 = list.iterator();
while (iterator2.hasNext()) {
    String element = iterator2.next();
    if ("B".equals(element)) {
        iterator2.remove();  // ✅ 迭代器的 remove() 会同步 expectedModCount
    }
}

// ✅ 正确方式 2：使用 for-each + 集合的 removeIf()
list.removeIf(e -> "B".equals(e));  // ✅ 内部使用迭代器

// ❌ 错误方式：for-each 直接删除
for (String element : list) {
    if ("B".equals(element)) {
        list.remove(element);  // ❌ 同样会触发 fail-fast
    }
}
```

### 三、fail-safe 机制原理

上图展示了 fail-safe 的副本机制。关键理解：

* **迭代副本** ：创建迭代器时复制原集合数据，迭代器只操作副本
* **不抛异常** ：原集合的修改不会影响迭代器，因为没有共享状态检测
* **弱一致性** ：可能读到 "过期" 数据，即迭代过程中原集合已被修改
* **内存开销** ：每次创建迭代器都需要复制数据，内存消耗更大

### 四、fail-safe 代码示例

```
// fail-safe 示例：CopyOnWriteArrayList
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
list.add("A");
list.add("B");
list.add("C");

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    if ("B".equals(element)) {
        list.remove(element);  // ✅ 不会抛异常！
    }
}
// 运行结果：正常完成，但迭代器可能仍然遍历到 "B"

// ConcurrentHashMap 也是 fail-safe
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.put("B", 2);

Iterator<String> keyIterator = map.keySet().iterator();
while (keyIterator.hasNext()) {
    String key = keyIterator.next();
    map.remove("B");  // ✅ 不会抛异常
    // 但 keyIterator 可能仍然遍历到 "B"
}
```

### 五、两类集合对比

### 六、源码分析：ArrayList 迭代器

```
// ArrayList.Itr 源码（简化版）
private class Itr implements Iterator<E> {
    int cursor;       // 下一个要返回的元素索引
    int lastRet = -1; // 上一个返回的元素索引
    int expectedModCount = modCount;  // 关键：记录创建时的 modCount

    public boolean hasNext() {
        return cursor != size;
    }

    public E next() {
        // 关键：每次 next() 都检查 modCount
        checkForComodification();
        int i = cursor;
        Object[] elementData = ArrayList.this.elementData;
        cursor = i + 1;
        return (E) elementData[lastRet = i];
    }

    public void remove() {
        if (lastRet < 0)
            throw new IllegalStateException();
        checkForComodification();

        try {
            ArrayList.this.remove(lastRet);  // 调用 ArrayList 的 remove
            cursor = lastRet;
            lastRet = -1;
            expectedModCount = modCount;  // 关键：同步 modCount！
        } catch (IndexOutOfBoundsException ex) {
            throw new ConcurrentModificationException();
        }
    }

    // 核心：检测方法
    final void checkForComodification() {
        if (modCount != expectedModCount)
            throw new ConcurrentModificationException();
    }
}
```

**关键发现** ：迭代器的 `remove()` 方法在删除后会执行 `expectedModCount = modCount` ，这就是为什么用迭代器删除不会抛异常。

## 面试高频追问

1. **为什么 Java 集合大多采用 fail-fast？**

   * 快速暴露问题，避免在错误状态下继续运行
   * 防止数据不一致导致的更严重后果
   * 性能更好（不需要复制数据）
2. **fail-fast 一定会在并发修改时抛异常吗？**

   * 不一定！只是 "尽力而为"（best-effort）
   * 单线程也可能触发（迭代时直接调用集合的 remove）
   * 多线程时不能依赖它来做并发控制
3. **如何在迭代时安全删除元素？**

   * 单线程：用迭代器的 `remove()` 方法
   * 单线程：用 `removeIf()` 方法（Java 8+）
   * 多线程：用 `CopyOnWriteArrayList` 等并发集合

## 常见面试变体

* "ConcurrentModificationException 是什么？什么时候会抛出？"
* "如何在遍历 ArrayList 时删除元素？"
* "CopyOnWriteArrayList 的原理是什么？"
* "ArrayList 和 CopyOnWriteArrayList 的区别？"

## 记忆口诀

**fail-fast** ：modCount 不等就抛异常，迭代器删除才安全，直接删除必报错。

**fail-safe** ：遍历副本不报错，可能读到旧数据，适合并发场景用。

**选择** ：单线程用 fail-fast，多线程用 fail-safe。

## 总结

**fail-fast** 通过 `modCount` 检测机制，发现集合被修改立即抛出 `ConcurrentModificationException` ，代表集合有 `ArrayList` 、 `HashMap` 等。 **fail-safe** 通过迭代副本实现，不会抛异常但可能读到旧数据，代表集合有 `CopyOnWriteArrayList` 、 `ConcurrentHashMap` 等。记住： **单线程迭代删除用迭代器的 `remove()` ，多线程用并发集合** 。
