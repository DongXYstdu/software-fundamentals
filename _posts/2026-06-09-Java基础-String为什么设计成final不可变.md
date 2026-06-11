---
title: "String 为什么设计成 final 不可变的"
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>基础原理理解</strong> ：面试官不仅仅是想知道 String 是不可变的，更是想考察你是否理解 Java 设计者的深层考量，以及不可变对象的设计思想。</p> </li> <li> <p><strong>多线程安全意识</strong> ：考察你是否意识到不可变性是实现线程安全最简单、最可靠的方式之一。</p> </li> <li> <p><strong>性能优化思维</strong> ：考察你是否了解字符串常量池、哈希缓存等 JVM 底层优化机制。</p> </li> <li> <p><strong>安全性认知</strong> ：考察你对系统安全的敏感度，理解不可变性在类加载、敏感信息保护等方面的重要性。</p> </li> </ol> <H2>核心答案</H2> <p><code>String</code> 被设计成 <code>final</code> 不可变类，主要基于 <strong>5 大核心原因</strong> ：</p> <table> <thead> <tr> <th>设计原因</th> <th>核心价值</th> <th>实际效果</th> </tr> </thead> <tbody> <tr> <td><strong>字符串常量池优化</strong></td> <td>内存复用</td> <td>相同字符串只存一份，节省堆内存</td> </tr> <tr> <td><strong>线程安全</strong></td> <td>无锁并发</td> <td>不可变对象天生线程安全，无需同步</td> </tr> <tr> <td><strong>哈希值缓存</strong></td> <td>性能提升</td> <td><code>hashCode()</code> 只需计算一次，后续直接复用</td> </tr> <tr> <td><strong>安全性保障</strong></td> <td>系统稳定</td> <td>防止类加载、文件路径等被篡改</td> </tr> <tr> <td><strong>设计一致性</strong></td> <td>行为可预测</td> <td>子类无法破坏父类契约</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ：不可变性是 <code>String</code> 实现高性能、高安全、高并发的基础保障。</p> <H2>深度解析</H2> <H3>一、final 关键字如何保证不可变？</H3> <p><code>String</code> 类通过 <code>final</code> 关键字从三个维度保证不可变性：</p>   <p>上图展示了 <code>String</code> 实现不可变性的三层保障机制：</p> <ol> <li> <p><strong>第一层（类级别）</strong> ： <code>public final class String</code> 声明类为 <code>final</code> ，彻底杜绝继承。如果允许继承，恶意子类可能重写方法，将可变行为引入原本不可变的 <code>String</code> 体系，破坏所有依赖不可变性的代码。</p> </li> <li> <p><strong>第二层（字段级别）</strong> ：JDK 8 及之前使用 <code>private final char[] value</code> ，JDK 9 改为 <code>private final byte[] value</code> （Compact Strings 优化）。 <code>final</code> 修饰确保数组引用一旦赋值就永远指向同一个数组对象。</p> </li> <li> <p><strong>第三层（访问控制）</strong> ： <code>private</code> 修饰符配合没有任何 <code>setter</code> 方法的设计，外部代码既不能直接访问 <code>value</code> 数组，也无法通过方法修改其内容。所有看似"修改"的操作（如 <code>substring()</code> 、 <code>concat()</code> ）实际上都是创建新对象。</p> </li> </ol> <p><strong>源码验证</strong> （JDK 8）：</p> <pre><code class="language-java" data-lang="java">public final class String
    implements java.io.Serializable, Comparable&lt;String&gt;, CharSequence {

    // 核心存储：final 修饰，引用不可变
    private final char value[];

    // 缓存哈希值：懒加载，计算一次后永久缓存
    private int hash; // Default to 0

    // 没有 setter 方法！
    // 所有修改操作都返回新对象
    public String substring(int beginIndex) {
        // 返回新 String 对象，原对象不变
        return new String(value, beginIndex, subLen);
    }
}</code></pre> <H3>二、字符串常量池：内存优化的基石</H3>   <p>上图清晰地展示了字符串常量池的工作机制：</p> <ul> <li> <p><strong>常量池的核心逻辑</strong> ：当使用字面量创建字符串时（如 <code>String s = "hello"</code> ），JVM 首先检查常量池中是否已存在相同内容的字符串。如果存在，直接返回池中对象的引用；如果不存在，在池中创建新对象并返回引用。</p> </li> <li> <p><strong>为什么不可变性是前提</strong> ：假设 <code>String</code> 可变，s1 和 s2 指向同一个池中对象，如果通过 s1 修改了内容，s2 也会"莫名其妙"被改变，这完全违背了程序员的预期。不可变性确保了多个引用共享同一对象时，彼此完全独立、互不影响。</p> </li> <li> <p><strong>内存优化效果</strong> ：在大规模应用中，大量重复字符串（如配置项、日志格式、异常消息）只需存储一份。例如某系统有 10000 个 "success" 字符串，如果可变需要 10000 个独立对象，不可变只需 1 个对象 + 10000 个引用。</p> </li> <li> <p><strong>intern() 方法</strong> ：即使是运行时动态创建的字符串，也可以手动加入常量池：</p> </li> </ul> <pre><code class="language-java" data-lang="java">String s1 = new String("hello");  // 堆中创建新对象
String s2 = s1.intern();          // 尝试放入常量池
String s3 = "hello";              // 此时常量池已有，直接复用

// s1 != s2（不同对象）
// s2 == s3（都指向常量池中同一个对象）</code></pre> <H3>三、线程安全：无锁并发的天然保障</H3>   <p>上图对比了可变与不可变对象在多线程环境下的行为差异：</p> <p><strong>不可变 = 天然线程安全</strong> ：这是并发编程中最基本的原则之一。 <code>String</code> 一旦创建，其内部状态永远不变，任何线程在任何时刻读取到的值都是完全一致的。不需要 <code>synchronized</code> 、不需要 <code>Lock</code> 、不需要 <code>volatile</code> ，零同步开销。</p> <p><strong>实际场景</strong> ： <code>String</code> 作为方法参数、返回值、Map 的 key 在多线程间传递是家常便饭。如果可变，每次传递都需要防御性复制，性能开销巨大且容易遗漏。不可变性让 <code>String</code> 可以安全地在各线程间自由共享。</p> <p><strong>对比可变类</strong> ： <code>StringBuilder</code> 是可变的，虽然性能更好，但不是线程安全的； <code>StringBuffer</code> 通过 <code>synchronized</code> 实现线程安全，但每次操作都要加锁，性能较差。 <code>String</code> 选择了第三条路：不可变 + 无锁，既安全又高效。</p> <H3>四、哈希值缓存：性能优化的经典案例</H3> <pre><code class="language-java" data-lang="java">// String 源码中的 hashCode 实现
public int hashCode() {
    int h = hash;  // 读取缓存的哈希值
    if (h == 0 &amp;&amp; value.length &gt; 0) {
        // 只有第一次调用时才计算
        for (char c : value) {
            h = 31 * h + c;
        }
        hash = h;  // 缓存结果
    }
    return h;
}</code></pre> <p><strong>懒加载 + 永久缓存的设计</strong> ：</p> <ol> <li><strong>懒加载</strong> ： <code>hash</code> 字段初始为 0，只有第一次调用 <code>hashCode()</code> 时才计算。</li> <li><strong>永久缓存</strong> ：一旦计算完成，结果存入 <code>hash</code> 字段，后续调用直接返回缓存值。</li> <li><strong>不可变性的关键作用</strong> ：因为字符串内容永不改变，哈希值也永不改变，可以放心地缓存。如果字符串可变，修改内容后缓存失效，每次都要重新计算或维护缓存一致性，复杂度剧增。</li> </ol> <p><strong>性能提升数据</strong> ：在 HashMap、HashSet 等频繁调用 <code>hashCode()</code> 的场景中，假设某个 key 被查询 1000 次，可变字符串需要计算 1000 次哈希值，不可变字符串只需计算 1 次，性能提升 1000 倍。</p> <H3>五、安全性：系统稳定的隐形防线</H3>   <p>上图列举了 <code>String</code> 不可变性在安全领域的四个典型应用：</p> <p><strong>1. 类加载机制</strong> ：JVM 在加载类时使用 <code>String</code> 表示类名。如果 <code>String</code> 可变，攻击者可能在类加载过程中篡改类名，导致加载错误的或恶意的类。不可变性确保类名从解析到加载完成保持一致。</p> <p><strong>2. 文件路径（TOCTOU 漏洞防护）</strong> ：TOCTOU（Time-of-Check to Time-of-Use）是一类经典的安全漏洞。权限检查时路径是安全的，使用时路径已被篡改。不可变性彻底杜绝了这种可能性。</p> <p><strong>3. 敏感信息处理</strong> ：虽然 <code>String</code> 不可变带来很多好处，但在处理密码等敏感信息时反而是劣势——无法真正"清除"数据，字符串可能留在常量池或内存中。因此安全场景推荐使用 <code>char[]</code> ，用完后立即填充随机值。</p> <p><strong>4. 网络连接与 URL</strong> ：数据库连接字符串、远程服务地址等关键配置，如果可变可能被中间人攻击篡改，导致连接到恶意服务器。</p> <H3>六、设计模式：不可变对象的最佳实践</H3> <p><code>String</code> 是不可变对象设计模式的教科书级实现，其设计原则被广泛借鉴：</p> <pre><code class="language-java" data-lang="java">// 不可变对象的设计模板
public final class ImmutableClass {          // 1. final 修饰类
    private final int value;                  // 2. final 修饰所有字段
    private final String name;

    public ImmutableClass(int value, String name) {  // 3. 通过构造函数初始化
        this.value = value;
        this.name = name;
    }

    // 4. 只提供 getter，不提供 setter
    public int getValue() { return value; }
    public String getName() { return name; }

    // 5. 修改操作返回新对象
    public ImmutableClass withValue(int newValue) {
        return new ImmutableClass(newValue, this.name);
    }
}</code></pre> <p><strong>Java 中其他不可变类</strong> ：</p> <ul> <li>基本类型包装类： <code>Integer</code> 、 <code>Long</code> 、 <code>Double</code> 等</li> <li><code>BigDecimal</code> 、 <code>BigInteger</code></li> <li><code>LocalDate</code> 、 <code>LocalTime</code> 、 <code>LocalDateTime</code> （Java 8+）</li> <li><code>Optional</code> （Java 8+）</li> </ul> <H2>面试高频追问</H2> <ol> <li> <p><strong>追问一</strong> ： <code>String</code> 真的完全不可变吗？能否通过反射修改？</p> <p>理论上可以通过反射暴力修改 <code>value</code> 数组的内容，但这属于"非法操作"，违反了 <code>String</code> 的设计契约，可能导致 JVM 崩溃、安全异常或不可预测的行为。实践中绝对不要这样做。</p> </li> <li> <p><strong>追问二</strong> ：JDK 9 的 Compact Strings 是什么？</p> <p>JDK 9 将 <code>String</code> 内部存储从 <code>char[]</code> （每字符 2 字节）改为 <code>byte[]</code> + <code>coder</code> 标志。对于纯 Latin-1 字符（ASCII、欧洲语言），每字符只需 1 字节，内存占用减半；对于中文等需要 UTF-16 的字符，仍使用 2 字节。这是对不可变性的优化而非破坏。</p> </li> <li> <p><strong>追问三</strong> ：为什么 <code>StringBuilder</code> 和 <code>StringBuffer</code> 是可变的？</p> <p>它们设计用于频繁字符串拼接场景。 <code>String</code> 每次拼接都创建新对象，性能差； <code>StringBuilder</code> 在内部数组上原地修改，完成后一次性转为 <code>String</code> 。这体现了"构建时可变、使用时不可变"的设计思想。</p> </li> <li> <p><strong>追问四</strong> ： <code>String</code> 的 <code>substring()</code> 在 JDK 6 和 JDK 7+ 有什么区别？</p> <ul> <li>JDK 6：新 <code>String</code> 共享原 <code>value</code> 数组，通过 <code>offset</code> 和 <code>count</code> 标识范围。可能造成内存泄漏（大字符串截取小片段，原数组无法回收）。</li> <li>JDK 7+：新 <code>String</code> 复制数据到新数组，彻底独立，无内存泄漏风险，但截取操作有复制开销。</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"为什么 Java 中 <code>String</code> 是不可变的？"</li> <li>" <code>String</code> 为什么要用 <code>final</code> 修饰？"</li> <li>"不可变对象有哪些优缺点？"</li> <li>"为什么 <code>String</code> 适合作为 <code>HashMap</code> 的 key？"</li> <li>"JDK 9 对 <code>String</code> 做了什么优化？"</li> </ul> <H2>记忆口诀</H2> <p><strong>五大原因记忆法</strong> ： <strong>池</strong> （常量池） <strong>线</strong> （线程安全） <strong>哈</strong> （哈希缓存） <strong>安</strong> （安全性） <strong>设</strong> （设计一致性）</p> <blockquote> <p>"吃线哈安设" —— 吃米线哈，安全设计（谐音记忆）</p> </blockquote> <H2>总结</H2> <p><code>String</code> 设计成 <code>final</code> 不可变类，是为了实现 <strong>常量池内存优化、天然线程安全、哈希值缓存、系统安全保障、设计一致性</strong> 五大核心价值。不可变性是 <code>String</code> 成为 Java 中最重要、最高频使用类的基础支撑，也是不可变对象设计模式的经典范例。</p> </div></main>