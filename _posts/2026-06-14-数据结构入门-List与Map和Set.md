---
title: 数据结构入门：List、Map、Set 三大容器详解
date: 2026-06-14 08:00:00 +0800
categories: [数据结构, 入门]
tags: [List, Map, Set, 集合, 入门, 零基础]
math: true
mermaid: true
---

## 选对工具箱，事半功?

想象你要整理一堆东西：
- 需要按顺序排列？用**排队名单**
- 需要按名字查找？用**字典**
- 需要去掉重复？?*抽奖?*

不同的需求用不同的工具。编程也一样—?*List、Map、Set** 就是三种最常用?工具?，选对了，代码又快又简洁；选错了，麻烦不断?

---

## List（列表）：有序可重复的排队名?

### 生活类比：排队名?

想象一个演唱会入场名单?*张三、李四、张三、王?*。注意，张三出现了两次，而且顺序很重要——先到先入场?

List 的核心特点：
- **有序**：元素有先后顺序，第1个就是第1?
- **可重?*：同一个值可以出现多?
- **按位置访?*：可以说"给我?个人"

### ArrayList vs LinkedList

List 有两种常见实现，就像两种不同的排队方式：

| 对比?| ArrayList | LinkedList |
|:---:|:---:|:---:|
| **底层结构** | 数组 | 链表 |
| **生活类比** | 电影院座?| 手拉手排?|
| **按位置查?* | ??O(1) | 🐢 ?O(n) |
| **头部插入删除** | 🐢 ?O(n) | ??O(1) |
| **内存** | 连续空间 | 分散空间 |
| **适用场景** | 查询多、尾部增?| 频繁在头部或中间增删 |

> 💡 **简单记?*：ArrayList = 数组包装，查询快；LinkedList = 链表包装，插入快。日常开?0%用ArrayList就够了?

### Java代码示例

```java
import java.util.*;

public class ListDemo {
    public static void main(String[] args) {
        // 创建ArrayList
        List<String> nameList = new ArrayList<>();

        // 增：添加元素
        nameList.add("张三");
        nameList.add("李四");
        nameList.add("张三");  // 可以重复
        nameList.add("王五");
        System.out.println("名单? + nameList);  // [张三, 李四, 张三, 王五]

        // 查：按位置访?
        System.out.println("?个人? + nameList.get(0));  // 张三
        System.out.println("张三第一次出现的位置? + nameList.indexOf("张三"));  // 0

        // 改：修改元素
        nameList.set(1, "赵六");
        System.out.println("修改后：" + nameList);  // [张三, 赵六, 张三, 王五]

        // 删：删除元素
        nameList.remove(0);  // 按位置删?
        nameList.remove("张三");  // 删除第一个匹配的
        System.out.println("删除后：" + nameList);  // [赵六, 王五]

        // 遍历
        for (String name : nameList) {
            System.out.println("入场? + name);
        }
    }
}
```

### Python对应：list

```python
# Python的list就是ArrayList
name_list = []

# ?
name_list.append("张三")
name_list.append("李四")
name_list.append("张三")  # 可重?
print(name_list)  # ['张三', '李四', '张三']

# ?
print(name_list[0])       # 张三
print(name_list.index("李四"))  # 1

# ?
name_list[1] = "赵六"

# ?
name_list.remove("张三")  # 删除第一?
del name_list[0]          # 按位置删?
```

---

## Map（映?字典）：一键对应一?

### 生活类比：手机通讯?

打开手机通讯录，输入"妈妈"就能找到对应的电话号码?*名字 ?电话号码**，这就是Map的核心—?*键值对（Key-Value?*?

Map 的核心特点：
- **键值对**：每个键（Key）对应一个值（Value?
- **键不重复**：通讯录里不能有两?妈妈"
- **按键查找极快**：输入名字，瞬间找到号码

```mermaid
graph LR
    subgraph 通讯录["通讯录（Map?]
        K1["'妈妈'"] --> V1["138xxxx1234"]
        K2["'爸爸'"] --> V2["139xxxx5678"]
        K3["'老师'"] --> V3["137xxxx9012"]
    end

    style K1 fill:#4a90d9,color:#fff
    style K2 fill:#4a90d9,color:#fff
    style K3 fill:#4a90d9,color:#fff
    style V1 fill:#f5a623,color:#fff
    style V2 fill:#f5a623,color:#fff
    style V3 fill:#f5a623,color:#fff
```

### HashMap：最常用的Map

HashMap 就像一?*超级通讯?*，通过一种叫"哈希"的魔法，能在海量数据中瞬间找到你要的条目?

> 💡 **简单理解哈?*：就像图书馆的编号系统，根据书名算出一个编号，直接去对应书架找书，不用一本一本翻?

### Java代码示例

```java
import java.util.*;

public class MapDemo {
    public static void main(String[] args) {
        // 创建HashMap
        Map<String, String> contacts = new HashMap<>();

        // 增：添加键值对
        contacts.put("妈妈", "138xxxx1234");
        contacts.put("爸爸", "139xxxx5678");
        contacts.put("老师", "137xxxx9012");
        System.out.println("通讯录：" + contacts);

        // 查：按键查找
        System.out.println("妈妈的电话：" + contacts.get("妈妈"));  // 138xxxx1234
        System.out.println("包含'爸爸'吗？" + contacts.containsKey("爸爸"));  // true
        System.out.println("包含这个号码吗？" + contacts.containsValue("138xxxx1234"));  // true

        // 改：键相同则覆盖
        contacts.put("妈妈", "138xxxx9999");  // 妈妈换号?
        System.out.println("妈妈新号码：" + contacts.get("妈妈"));  // 138xxxx9999

        // 删：按键删除
        contacts.remove("老师");

        // 遍历
        for (Map.Entry<String, String> entry : contacts.entrySet()) {
            System.out.println(entry.getKey() + " ?" + entry.getValue());
        }
    }
}
```

### Python对应：dict

```python
# Python的dict就是HashMap
contacts = {}

# ??
contacts["妈妈"] = "138xxxx1234"
contacts["爸爸"] = "139xxxx5678"
contacts["老师"] = "137xxxx9012"

# ?
print(contacts["妈妈"])           # 138xxxx1234
print(contacts.get("同学", "未找?))  # 未找到（安全访问?

# ?
del contacts["老师"]

# 遍历
for name, phone in contacts.items():
    print(f"{name} ?{phone}")
```

---

## Set（集合）：无序不重复的抽奖箱

### 生活类比：抽奖箱

公司年会抽奖，每个人只能抽一次—?*张三抽过了就不能再抽**。抽奖箱里每个人的名字只出现一次，而且谁先被抽到是随机的（无序）?

Set 的核心特点：
- **不重?*：同一个元素只能出现一?
- **无序**：没?第几?的概?
- **判断存在极快**：张三抽过没？一查就知道

### HashSet：最常用的Set

HashSet 内部其实就是 HashMap，只用了键，值是个占位符。所以它也有"哈希"的魔法——判断一个元素是否存在，速度极快?

### Java代码示例

```java
import java.util.*;

public class SetDemo {
    public static void main(String[] args) {
        // 创建HashSet
        Set<String> lottery = new HashSet<>();

        // 增：添加元素
        lottery.add("张三");
        lottery.add("李四");
        lottery.add("王五");
        lottery.add("张三");  // 重复添加，不会生效！
        System.out.println("抽奖箱：" + lottery);  // [李四, 张三, 王五]（顺序不定）

        // 查：判断是否存在
        System.out.println("张三在箱子里吗？" + lottery.contains("张三"));  // true

        // 删：删除元素
        lottery.remove("李四");

        // 遍历
        for (String name : lottery) {
            System.out.println("参与者：" + name);
        }

        // 实用技巧：用Set给List去重
        List<Integer> numbers = Arrays.asList(1, 3, 2, 3, 1, 4, 2);
        Set<Integer> unique = new HashSet<>(numbers);
        System.out.println("去重后：" + unique);  // [1, 2, 3, 4]
    }
}
```

### Python对应：set

```python
# Python的set就是HashSet
lottery = set()

# ?
lottery.add("张三")
lottery.add("李四")
lottery.add("张三")  # 重复，不生效
print(lottery)  # {'张三', '李四'}（顺序不定）

# ?
print("张三在吗?, "张三" in lottery)  # True

# ?
lottery.discard("李四")

# 实用技巧：去重
numbers = [1, 3, 2, 3, 1, 4, 2]
unique = list(set(numbers))
print("去重后：", unique)
```

---

## 三大容器对比

| 对比?| List | Map | Set |
|:---:|:---:|:---:|:---:|
| **生活类比** | 排队名单 | 通讯?| 抽奖?|
| **是否有序** | ?有序 | ?键无?| ?无序 |
| **是否可重?* | ?可重?| ?键不可重?| ?不可重复 |
| **查找速度** | 🐢 O(n) 逐个?| ?O(1) 按键瞬间?| ?O(1) 瞬间判断 |
| **访问方式** | 按位?get(index) | 按键 get(key) | 判断存在 contains() |
| **典型场景** | 保存顺序、允许重?| 一一对应关系 | 去重、判断存?|

---

## 什么时候用哪个？决策流程图

```mermaid
graph TD
    START["我该用哪种容器？"] --> Q1{"需要键值对映射吗？<br/>（名字→电话?}
    Q1 -->|是| MAP["?Map<br/>?HashMap"]
    Q1 -->|否| Q2{"需要去重吗?br/>（同一元素只留一个）"}
    Q2 -->|是| SET["?Set<br/>?HashSet"]
    Q2 -->|否| Q3{"需要保持顺序且允许重复?}
    Q3 -->|是| LIST["?List<br/>?ArrayList"]
    Q3 -->|否| Q4{"只是判断存在?}
    Q4 -->|是| SET
    Q4 -->|否| LIST

    style START fill:#4a90d9,color:#fff
    style MAP fill:#f5a623,color:#fff
    style SET fill:#7ed321,color:#fff
    style LIST fill:#bd10e0,color:#fff
```

**简单口诀**?
- ?*映射**?Map（名字→电话?
- ?*去重**?Set（抽奖箱?
- ?*排队**?List（入场名单）

---

## 常见陷阱

### 陷阱1：Map的key可以为null吗？

| 实现?| key为null | value为null |
|:---:|:---:|:---:|
| HashMap | ?允许一个null?| ?允许多个null?|
| TreeMap | ?不允许（要排序） | ?不允?|
| ConcurrentHashMap | ?不允?| ?不允?|

> ⚠️ 建议：虽然HashMap允许null键，?*最好不要用null作为key**，容易出bug且难以调试?

### 陷阱2：Set怎么判断重复?

Set判断两个元素是否"相同"，不是用 `==`，而是?**`equals()` + `hashCode()`**?

```java
// 自定义类必须同时重写equals和hashCode
public class Student {
    private String name;
    private int age;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Student student = (Student) o;
        return age == student.age && Objects.equals(name, student.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

> 💡 **类比**：hashCode像身份证号前6位（快速筛选），equals像完整身份证号（精确比对）。先看前6位不同就肯定不是同一个人，前6位相同再精确比对?

### 陷阱3：List的subList视图问题

```java
List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
List<Integer> sub = list.subList(1, 3);  // [2, 3]

// ⚠️ sub是原list?视图"，不是副本！
sub.set(0, 99);
System.out.println(list);  // [1, 99, 3, 4, 5]  原list也被改了?

// ⚠️ 修改原list后使用sub会抛异常
list.add(6);
sub.get(0);  // ConcurrentModificationException!
```

> 💡 **安全做法**：如果需要独立的子列表，?`new ArrayList<>(list.subList(1, 3))` 创建副本?

---

## 三大容器的关系图

```mermaid
graph TB
    COL["Collection 容器家族"]

    COL --> LIST["List<br/>有序·可重?br/>排队名单"]
    COL --> SET_NODE["Set<br/>无序·不重?br/>抽奖?]

    LIST --> AL["ArrayList<br/>数组实现·查询?]
    LIST --> LL["LinkedList<br/>链表实现·插入?]

    SET_NODE --> HS["HashSet<br/>哈希实现·最常用"]
    SET_NODE --> TS["TreeSet<br/>红黑树实现·有?]

    MAP_NODE["Map<br/>键值对·一键一?br/>通讯?] --> HM["HashMap<br/>哈希实现·最常用"]
    MAP_NODE --> TM["TreeMap<br/>红黑树实现·按键排?]

    style COL fill:#4a90d9,color:#fff
    style MAP_NODE fill:#f5a623,color:#fff
    style LIST fill:#bd10e0,color:#fff
    style SET_NODE fill:#7ed321,color:#fff
```

---

## 小结

三大容器，三种用途，记住类比就够了：

- **List = 排队名单**：有序、可重复，适合保存顺序数据
- **Map = 通讯?*：键值对，按键查找极快，适合一对一映射
- **Set = 抽奖?*：不重复，判断存在极快，适合去重

选容器的口诀?*映射用Map，去重用Set，排队用List**?

下一篇文章，我们将深入C语言，学习如何用**结构?*来组织复杂的数据——这是理解数据结构底层实现的关键一步！
