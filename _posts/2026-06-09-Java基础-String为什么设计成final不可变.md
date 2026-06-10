---
title: "String 为什么设计成 final 不可变的"
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---

## 面试考察?

1. **基础原理理解**：面试官不仅仅是想知?String 是不可变的，更是想考察你是否理?Java 设计者的深层考量，以及不可变对象的设计思想?

2. **多线程安全意?*：考察你是否意识到不可变性是实现线程安全最简单、最可靠的方式之一?

3. **性能优化思维**：考察你是否了解字符串常量池、哈希缓存等 JVM 底层优化机制?

4. **安全性认?*：考察你对系统安全的敏感度，理解不可变性在类加载、敏感信息保护等方面的重要性?

## 核心答案

`String` 被设计成 `final` 不可变类，主要基?**5 大核心原?*?

| 设计原因 | 核心价?| 实际效果 |
|---|---|---|
| **字符串常量池优化** | 内存复用 | 相同字符串只存一份，节省堆内?|
| **线程安全** | 无锁并发 | 不可变对象天生线程安全，无需同步 |
| **哈希值缓?* | 性能提升 | `hashCode()` 只需计算一次，后续直接复用 |
| **安全性保?* | 系统稳定 | 防止类加载、文件路径等被篡?|
| **设计一致?* | 行为可预?| 子类无法破坏父类契约 |

**一句话总结**：不可变性是 `String` 实现高性能、高安全、高并发的基础保障?

## 深度解析

### 一、final 关键字如何保证不可变?

`String` 类通过 `final` 关键字从三个维度保证不可变性：

![](https://aka.doubaocdn.com/s/HmXQ1wZNgl)

上图展示?`String` 实现不可变性的三层保障机制?

1. **第一层（类级别）**：`public final class String` 声明类为 `final`，彻底杜绝继承。如果允许继承，恶意子类可能重写方法，将可变行为引入原本不可变的 `String` 体系，破坏所有依赖不可变性的代码?

2. **第二层（字段级别?*：JDK 8 及之前使?`private final char[] value`，JDK 9 改为 `private final byte[] value`（Compact Strings 优化）。`final` 修饰确保数组引用一旦赋值就永远指向同一个数组对象?

3. **第三层（访问控制?*：`private` 修饰符配合没有任?`setter` 方法的设计，外部代码既不能直接访?`value` 数组，也无法通过方法修改其内容。所有看?修改"的操作（?`substring()`、`concat()`）实际上都是创建新对象?

**源码验证**（JDK 8）：

```java
public final class String
    implements java.io.Serializable, Comparable<String>, CharSequence {

    // 核心存储：final 修饰，引用不可变
    private final char value[];

    // 缓存哈希值：懒加载，计算一次后永久缓存
    private int hash; // Default to 0

    // 没有 setter 方法?
    // 所有修改操作都返回新对?
    public String substring(int beginIndex) {
        // 返回?String 对象，原对象不变
        return new String(value, beginIndex, subLen);
    }
}
```

### 二、字符串常量池：内存优化的基?

![](https://aka.doubaocdn.com/s/cjc81wZNgl)

上图清晰地展示了字符串常量池的工作机制：

- **常量池的核心逻辑**：当使用字面量创建字符串时（?`String s = "hello"`），JVM 首先检查常量池中是否已存在相同内容的字符串。如果存在，直接返回池中对象的引用；如果不存在，在池中创建新对象并返回引用?

- **为什么不可变性是前提**：假?`String` 可变，s1 ?s2 指向同一个池中对象，如果通过 s1 修改了内容，s2 也会"莫名其妙"被改变，这完全违背了程序员的预期。不可变性确保了多个引用共享同一对象时，彼此完全独立、互不影响?

- **内存优化效果**：在大规模应用中，大量重复字符串（如配置项、日志格式、异常消息）只需存储一份。例如某系统?10000 ?"success" 字符串，如果可变需?10000 个独立对象，不可变只需 1 个对?+ 10000 个引用?

- **intern() 方法**：即使是运行时动态创建的字符串，也可以手动加入常量池?

```java
String s1 = new String("hello");  // 堆中创建新对?
String s2 = s1.intern();          // 尝试放入常量?
String s3 = "hello";              // 此时常量池已有，直接复用

// s1 != s2（不同对象）
// s2 == s3（都指向常量池中同一个对象）
```

### 三、线程安全：无锁并发的天然保?

不可?= 天然线程安全：这是并发编程中最基本的原则之一。`String` 一旦创建，其内部状态永远不变，任何线程在任何时刻读取到的值都是完全一致的。不需?`synchronized`、不需?`Lock`、不需?`volatile`，零同步开销?

**实际场景**：`String` 作为方法参数、返回值、Map ?key 在多线程间传递是家常便饭。如果可变，每次传递都需要防御性复制，性能开销巨大且容易遗漏。不可变性让 `String` 可以安全地在各线程间自由共享?

**对比可变?*：`StringBuilder` 是可变的，虽然性能更好，但不是线程安全的；`StringBuffer` 通过 `synchronized` 实现线程安全，但每次操作都要加锁，性能较差。`String` 选择了第三条路：不可?+ 无锁，既安全又高效?

### 四、哈希值缓存：性能优化的经典案?

```java
// String 源码中的 hashCode 实现
public int hashCode() {
    int h = hash;  // 读取缓存的哈希?
    if (h == 0 && value.length > 0) {
        // 只有第一次调用时才计?
        for (char c : value) {
            h = 31 * h + c;
        }
        hash = h;  // 缓存结果
    }
    return h;
}
```

**懒加?+ 永久缓存的设?*?

1. **懒加?*：`hash` 字段初始?0，只有第一次调?`hashCode()` 时才计算?

2. **永久缓存**：一旦计算完成，结果存入 `hash` 字段，后续调用直接返回缓存值?

3. **不可变性的关键作用**：因为字符串内容永不改变，哈希值也永不改变，可以放心地缓存。如果字符串可变，修改内容后缓存失效，每次都要重新计算或维护缓存一致性，复杂度剧增?

**性能提升数据**：在 HashMap、HashSet 等频繁调?`hashCode()` 的场景中，假设某?key 被查?1000 次，可变字符串需要计?1000 次哈希值，不可变字符串只需计算 1 次，性能提升 1000 倍?

### 五、安全性：系统稳定的隐形防?

**1. 类加载机?*：JVM 在加载类时使?`String` 表示类名。如?`String` 可变，攻击者可能在类加载过程中篡改类名，导致加载错误的或恶意的类。不可变性确保类名从解析到加载完成保持一致?

**2. 文件路径（TOCTOU 漏洞防护?*：TOCTOU（Time-of-Check to Time-of-Use）是一类经典的安全漏洞。权限检查时路径是安全的，使用时路径已被篡改。不可变性彻底杜绝了这种可能性?

**3. 敏感信息处理**：虽?`String` 不可变带来很多好处，但在处理密码等敏感信息时反而是劣势——无法真?清除"数据，字符串可能留在常量池或内存中。因此安全场景推荐使?`char[]`，用完后立即填充随机值?

**4. 网络连接?URL**：数据库连接字符串、远程服务地址等关键配置，如果可变可能被中间人攻击篡改，导致连接到恶意服务器?

### 六、设计模式：不可变对象的最佳实?

`String` 是不可变对象设计模式的教科书级实现，其设计原则被广泛借鉴?

```java
// 不可变对象的设计模板
public final class ImmutableClass {          // 1. final 修饰?
    private final int value;                  // 2. final 修饰所有字?
    private final String name;

    public ImmutableClass(int value, String name) {  // 3. 通过构造函数初始化
        this.value = value;
        this.name = name;
    }

    // 4. 只提?getter，不提供 setter
    public int getValue() { return value; }
    public String getName() { return name; }

    // 5. 修改操作返回新对?
    public ImmutableClass withValue(int newValue) {
        return new ImmutableClass(newValue, this.name);
    }
}
```

**Java 中其他不可变?*?

- 基本类型包装类：`Integer`、`Long`、`Double` ?
- `BigDecimal`、`BigInteger`
- `LocalDate`、`LocalTime`、`LocalDateTime`（Java 8+?
- `Optional`（Java 8+?

## 面试高频追问

1. **追问一**：`String` 真的完全不可变吗？能否通过反射修改?

理论上可以通过反射暴力修改 `value` 数组的内容，但这属于"非法操作"，违反了 `String` 的设计契约，可能导致 JVM 崩溃、安全异常或不可预测的行为。实践中绝对不要这样做?

2. **追问?*：JDK 9 ?Compact Strings 是什么？

JDK 9 ?`String` 内部存储?`char[]`（每字符 2 字节）改?`byte[]` + `coder` 标志。对于纯 Latin-1 字符（ASCII、欧洲语言），每字符只需 1 字节，内存占用减半；对于中文等需?UTF-16 的字符，仍使?2 字节。这是对不可变性的优化而非破坏?

3. **追问?*：为什?`StringBuilder` ?`StringBuffer` 是可变的?

它们设计用于频繁字符串拼接场景。`String` 每次拼接都创建新对象，性能差；`StringBuilder` 在内部数组上原地修改，完成后一次性转?`String`。这体现?构建时可变、使用时不可?的设计思想?

4. **追问?*：`String` ?`substring()` ?JDK 6 ?JDK 7+ 有什么区别？

    - JDK 6：新 `String` 共享?`value` 数组，通过 `offset` ?`count` 标识范围。可能造成内存泄漏（大字符串截取小片段，原数组无法回收）?

    - JDK 7+：新 `String` 复制数据到新数组，彻底独立，无内存泄漏风险，但截取操作有复制开销?

## 常见面试变体

- "为什?Java ?`String` 是不可变的？"
- "`String` 为什么要?`final` 修饰?
- "不可变对象有哪些优缺点？"
- "为什?`String` 适合作为 `HashMap` ?key?
- "JDK 9 ?`String` 做了什么优化？"

## 记忆口诀

**五大原因记忆?*?*?*（常量池?*?*（线程安全）**?*（哈希缓存）**?*（安全性）**?*（设计一致性）

"吃线哈安? —?吃米线哈，安全设计（谐音记忆?

## 总结

`String` 设计?`final` 不可变类，是为了实现 **常量池内存优化、天然线程安全、哈希值缓存、系统安全保障、设计一致?* 五大核心价值。不可变性是 `String` 成为 Java 中最重要、最高频使用类的基础支撑，也是不可变对象设计模式的经典范例?

---
> 参考来源：[String 为什么设计成 final 不可变的？](https://www.quanxiaoha.com/java-interview/why-string-final-immutable)
