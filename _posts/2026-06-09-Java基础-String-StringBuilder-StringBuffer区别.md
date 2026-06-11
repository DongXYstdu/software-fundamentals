---
title: "String、StringBuilder StringBuffer 的区别？"
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>基础掌握度</strong> ：面试官不仅仅是想知道这三者的区别，更是想确认你是否理解 Java 字符串的不可变性设计，以及为什么需要 <code>StringBuilder</code> 和 <code>StringBuffer</code> 。</p> </li> <li> <p><strong>线程安全意识</strong> ：考察你是否清楚 <code>StringBuilder</code> 和 <code>StringBuffer</code> 在线程安全上的差异，能否根据业务场景选择合适的类。</p> </li> <li> <p><strong>性能优化意识</strong> ：是否了解字符串拼接在不同场景下的性能差异，能否写出高性能的字符串处理代码。</p> </li> </ol> <H2>核心答案</H2> <table> <thead> <tr> <th>对比项</th> <th><code>String</code></th> <th><code>StringBuilder</code></th> <th><code>StringBuffer</code></th> </tr> </thead> <tbody> <tr> <td><strong>可变性</strong></td> <td>不可变</td> <td>可变</td> <td>可变</td> </tr> <tr> <td><strong>线程安全</strong></td> <td>安全（不可变）</td> <td>不安全</td> <td>安全（ <code>synchronized</code> ）</td> </tr> <tr> <td><strong>性能</strong></td> <td>拼接差</td> <td>最快</td> <td>较快</td> </tr> <tr> <td><strong>适用场景</strong></td> <td>少量字符串、常量</td> <td>单线程拼接</td> <td>多线程拼接</td> </tr> <tr> <td><strong>出现版本</strong></td> <td>JDK 1.0</td> <td>JDK 1.5</td> <td>JDK 1.0</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ：单线程用 <code>StringBuilder</code> ，多线程用 <code>StringBuffer</code> ，常量用 <code>String</code> 。</p> <H2>深度解析</H2> <H3>一、String 的不可变性</H3> <p><code>String</code> 是 Java 中最常用的类之一，它的核心特性是 <strong>不可变（Immutable）</strong> 。</p>   <p>上图展示了 <code>String</code> 不可变性的核心原理，整体需要关注以下几点：</p> <ul> <li> <p><strong>底层存储</strong> ： <code>String</code> 内部使用 <code>final char[] value</code> （JDK 9 之后改为 <code>byte[]</code> ）存储字符数据， <code>final</code> 修饰意味着引用不可变。</p> </li> <li> <p><strong>任何"修改"操作都会创建新对象</strong> ：如拼接、截取、大小写转换等，原对象不变，返回新对象。</p> </li> <li> <p><strong>不可变的好处</strong> ：</p> <ul> <li>线程安全：多个线程可以安全共享，无需同步</li> <li>字符串常量池优化：相同字符串只存一份</li> <li>安全性：作为参数传递时不会被修改，适合作为 <code>HashMap</code> 的 key</li> </ul> </li> </ul> <H3>二、StringBuilder 与 StringBuffer 的可变性</H3> <p>这两个类都继承自 <code>AbstractStringBuilder</code> ，底层是 <strong>可扩容的字符数组</strong> 。</p>   <p>上图展示了可变字符串的工作原理，关键点如下：</p> <ul> <li> <p><strong>直接修改内部数组</strong> ： <code>append()</code> 、 <code>insert()</code> 、 <code>delete()</code> 等方法直接操作原数组，不创建新对象。</p> </li> <li> <p><strong>自动扩容</strong> ：当容量不足时，自动扩容为原来的 <code>2 倍 + 2</code> ，并将原数据复制到新数组。</p> </li> <li> <p><strong>预分配容量</strong> ：如果能预估最终长度，建议构造时指定容量，避免多次扩容：</p> <pre><code class="language-java" data-lang="java">// 推荐：预估容量，避免扩容
StringBuilder sb = new StringBuilder(1024);</code></pre> </li> </ul> <H3>三、线程安全性对比</H3>   <p>上图展示了线程安全实现的核心差异：</p> <ul> <li> <p><strong><code>StringBuilder</code></strong> ：所有方法都没有 <code>synchronized</code> 修饰，多线程并发调用可能导致数据错乱。</p> </li> <li> <p><strong><code>StringBuffer</code></strong> ：几乎所有公共方法都用 <code>synchronized</code> 修饰，保证同一时刻只有一个线程能操作。</p> </li> <li> <p><strong><code>String</code></strong> ：因为不可变，天然线程安全，无需任何同步措施。</p> </li> </ul> <H3>四、性能对比实验</H3> <pre><code class="language-java" data-lang="java">// 测试字符串拼接性能
public class StringPerformanceTest {

    public static void main(String[] args) {
        int count = 100000;

        // 方式一：String 拼接（最慢）
        long start1 = System.currentTimeMillis();
        String s1 = "";
        for (int i = 0; i &lt; count; i++) {
            s1 += i;  // 每次循环都创建新 String 对象
        }
        System.out.println("String: " + (System.currentTimeMillis() - start1) + "ms");

        // 方式二：StringBuilder（最快）
        long start2 = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder(count * 4);  // 预分配容量
        for (int i = 0; i &lt; count; i++) {
            sb.append(i);  // 直接追加，不创建新对象
        }
        System.out.println("StringBuilder: " + (System.currentTimeMillis() - start2) + "ms");

        // 方式三：StringBuffer（略慢于 StringBuilder）
        long start3 = System.currentTimeMillis();
        StringBuffer sbuf = new StringBuffer(count * 4);
        for (int i = 0; i &lt; count; i++) {
            sbuf.append(i);  // 有同步开销
        }
        System.out.println("StringBuffer: " + (System.currentTimeMillis() - start3) + "ms");
    }
}</code></pre> <p><strong>典型运行结果</strong> （10 万次拼接）：</p> <table> <thead> <tr> <th>方式</th> <th>耗时</th> <th>说明</th> </tr> </thead> <tbody> <tr> <td><code>String</code></td> <td>~5000ms</td> <td>创建大量临时对象，频繁 GC</td> </tr> <tr> <td><code>StringBuilder</code></td> <td>~5ms</td> <td>直接追加，性能最优</td> </tr> <tr> <td><code>StringBuffer</code></td> <td>~8ms</td> <td>同步开销约 50%</td> </tr> </tbody> </table> <H3>五、使用场景指南</H3> <pre><code class="language-java" data-lang="java">// ✅ 场景一：常量、配置项、少量拼接 → 用 String
String name = "张三";
String greeting = "Hello, " + name;  // 编译器自动优化为 StringBuilder

// ✅ 场景二：单线程大量拼接 → 用 StringBuilder
public String buildSql(List&lt;String&gt; conditions) {
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
for (int i = 0; i &lt; 10000; i++) {
    result += i;  // 创建 10000 个 String 对象！
}</code></pre> <H2>面试高频追问</H2> <ol> <li> <p><strong><code>String s = new String("abc")</code> 创建了几个对象？</strong></p> <p>分情况讨论：</p> <ul> <li>如果字符串常量池中已存在 <code>"abc"</code> ：创建 <strong>1 个</strong> 堆对象</li> <li>如果字符串常量池中不存在 <code>"abc"</code> ：创建 <strong>2 个</strong> 对象（1 个常量池对象 + 1 个堆对象）</li> </ul> </li> <li> <p><strong>为什么 <code>String</code> 设计为不可变？</strong></p> <ul> <li>安全性：防止被恶意修改，适合作为敏感信息存储</li> <li>线程安全：无需同步，可安全共享</li> <li>哈希缓存： <code>hashCode</code> 只需计算一次，提升 <code>HashMap</code> 性能</li> <li>字符串常量池：相同字符串只存一份，节省内存</li> </ul> </li> <li> <p><strong><code>String</code> 的 <code>+</code> 拼接和 <code>StringBuilder</code> 的 <code>append()</code> 有什么区别？</strong></p> <ul> <li><strong>编译期常量</strong> ： <code>"a" + "b" + "c"</code> 会被编译器直接优化为 <code>"abc"</code></li> <li><strong>变量拼接</strong> ： <code>a + b + c</code> 会被编译器自动转换为 <code>new StringBuilder().append(a).append(b).append(c).toString()</code></li> <li><strong>循环拼接</strong> ：循环内用 <code>+</code> 每次都会创建新的 <code>StringBuilder</code> ，性能极差</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"为什么 <code>String</code> 是不可变的？有什么好处？"</li> <li>" <code>String s = new String('abc')</code> 创建了几个对象？"</li> <li>"字符串拼接哪种方式性能最好？"</li> <li>" <code>StringBuilder</code> 和 <code>StringBuffer</code> 的区别是什么？"</li> </ul> <H2>记忆口诀</H2> <p><strong>可变性</strong> ： <code>String</code> 不可变， <code>Builder</code> 和 <code>Buffer</code> 都可变</p> <p><strong>线程安全</strong> ： <code>Buffer</code> 有锁安全， <code>Builder</code> 无锁快</p> <p><strong>使用场景</strong> ：单线程用 <code>Builder</code> ，多线程用 <code>Buffer</code> ，常量用 <code>String</code></p> <H2>总结</H2> <p><code>String</code> 不可变、线程安全但拼接性能差； <code>StringBuilder</code> 可变、单线程性能最优； <code>StringBuffer</code> 可变、多线程安全但略有同步开销。实际开发中，单线程场景优先使用 <code>StringBuilder</code> ，循环拼接必须避免使用 <code>String</code> 的 <code>+</code> 操作。</p> </div></main>