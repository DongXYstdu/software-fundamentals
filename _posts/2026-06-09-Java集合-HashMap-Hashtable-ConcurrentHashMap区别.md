---
title: HashMap、Hashtable ConcurrentHashMap 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>线程安全认知</strong> ：面试官不仅仅是想知道这三者谁是线程安全的，更是想考察你是否理解不同线程安全实现方式的性能差异，以及为什么 <code>Hashtable</code> 已经被淘汰。</p> </li> <li> <p><strong>并发编程深度</strong> ：考察你是否了解 <code>ConcurrentHashMap</code> 的底层实现原理，包括 JDK 7 的分段锁和 JDK 8 的 CAS + <code>synchronized</code> 两种方案的演进。</p> </li> <li> <p><strong>生产实践能力</strong> ：能否根据实际场景（读多写少、高并发等）选择合适的 Map 实现，避免盲目使用导致的性能问题或线程安全隐患。</p> </li> </ol> <H2>核心答案</H2> <p>三者都是 <code>Map</code> 接口的实现类，但线程安全性和性能差异显著：</p> <table> <thead> <tr> <th>特性</th> <th>HashMap</th> <th>Hashtable</th> <th>ConcurrentHashMap</th> </tr> </thead> <tbody> <tr> <td>线程安全</td> <td>❌ 不安全</td> <td>✅ 安全</td> <td>✅ 安全</td> </tr> <tr> <td>锁粒度</td> <td>无锁</td> <td>整表锁（粗粒度）</td> <td>桶级别锁（细粒度）</td> </tr> <tr> <td>null 键/值</td> <td>✅ 都允许</td> <td>❌ 都不允许</td> <td>❌ 都不允许</td> </tr> <tr> <td>初始容量</td> <td>16</td> <td>11</td> <td>16</td> </tr> <tr> <td>扩容倍数</td> <td>2 倍</td> <td>2n + 1</td> <td>2 倍</td> </tr> <tr> <td>迭代器</td> <td>快速失败</td> <td>快速失败</td> <td>弱一致性</td> </tr> <tr> <td>底层结构（JDK 8）</td> <td>数组 + 链表/红黑树</td> <td>数组 + 链表</td> <td>数组 + 链表/红黑树</td> </tr> <tr> <td>性能</td> <td>最高（单线程）</td> <td>最低（全表锁）</td> <td>高（并发优秀）</td> </tr> <tr> <td>适用场景</td> <td>单线程或外部同步</td> <td>已淘汰</td> <td>高并发多线程</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ：单线程用 <code>HashMap</code> ，多线程用 <code>ConcurrentHashMap</code> ， <code>Hashtable</code> 已被淘汰（历史遗留类）。</p> <H2>深度解析</H2> <H3>一、线程安全实现对比</H3>   <p>上图展示了两种线程安全实现的核心差异：</p> <ul> <li> <p><strong>Hashtable</strong> ：使用 <code>synchronized</code> 修饰几乎所有方法，一把大锁锁住整个哈希表。任何时刻只允许一个线程操作，即使是访问不同位置的元素也会相互阻塞，并发性能极差。</p> </li> <li> <p><strong>ConcurrentHashMap (JDK 8)</strong> ：采用桶级别细粒度锁，每个桶（数组位置）独立加锁。线程 A 操作索引 2 的元素，线程 B 操作索引 5 的元素，两者互不影响，可并发执行。</p> </li> </ul> <H3>二、ConcurrentHashMap 的演进</H3> <p><strong>JDK 7：分段锁（Segment）</strong></p> <pre><code class="language-java" data-lang="java">// JDK 7 的分段锁设计
public class ConcurrentHashMap&lt;K, V&gt; {
    final Segment&lt;K,V&gt;[] segments;  // 默认 16 个分段

    static final class Segment&lt;K,V&gt; extends ReentrantLock {
        transient volatile HashEntry&lt;K,V&gt;[] table;  // 每个分段维护一个小哈希表
    }
}</code></pre> <p>分段锁将整个 Map 分成多个段（默认 16 个），每段一把 <code>ReentrantLock</code> 。并发度最高为分段数。</p> <p><strong>JDK 8：CAS + synchronized</strong></p> <pre><code class="language-java" data-lang="java">// JDK 8 的桶级别锁设计
public class ConcurrentHashMap&lt;K, V&gt; {
    transient volatile Node&lt;K,V&gt;[] table;  // 单一数组，不再分段

    // 核心插入逻辑（简化版）
    final V putVal(K key, V value, boolean onlyIfAbsent) {
        int hash = spread(key.hashCode());
        for (Node&lt;K,V&gt;[] tab = table;;) {
            Node&lt;K,V&gt; f; int n, i, fh;
            if (tab == null || (n = tab.length) == 0)
                tab = initTable();
            else if ((f = tabAt(tab, i = (n - 1) &amp; hash)) == null) {
                // 桶为空，CAS 无锁插入
                if (casTabAt(tab, i, null, new Node&lt;K,V&gt;(hash, key, value, null)))
                    break;
            }
            else {
                // 桶不为空，synchronized 加锁当前桶
                synchronized (f) {
                    // 链表遍历或红黑树插入...
                }
            }
        }
        return null;
    }
}</code></pre> <p><strong>JDK 7 vs JDK 8 对比</strong> ：</p> <table> <thead> <tr> <th>对比项</th> <th>JDK 7 分段锁</th> <th>JDK 8 CAS + synchronized</th> </tr> </thead> <tbody> <tr> <td>锁粒度</td> <td>分段级别（默认 16 段）</td> <td>桶级别（更细）</td> </tr> <tr> <td>并发度</td> <td>最大为段数</td> <td>理论上为数组长度</td> </tr> <tr> <td>内存占用</td> <td>高（多个 Segment 对象）</td> <td>低（单一数组）</td> </tr> <tr> <td>锁类型</td> <td><code>ReentrantLock</code></td> <td><code>synchronized</code> + CAS</td> </tr> <tr> <td>扩容</td> <td>分段独立扩容</td> <td>协同扩容（多线程协助）</td> </tr> </tbody> </table> <H3>三、HashMap 的线程安全问题</H3> <p><code>HashMap</code> 在多线程环境下有严重问题：</p> <p><strong>1. JDK 7 扩容死循环</strong></p> <pre><code class="language-java" data-lang="java">// JDK 7 扩容时的头插法会导致链表成环
void transfer(Entry[] newTable) {
    Entry[] src = table;
    for (int j = 0; j &lt; src.length; j++) {
        Entry&lt;K,V&gt; e = src[j];
        while (null != e) {
            Entry&lt;K,V&gt; next = e.next;      // 线程切换点
            int i = indexFor(e.hash, newCapacity);
            e.next = newTable[i];          // 头插法：后插入的在前面
            newTable[i] = e;
            e = next;
        }
    }
}
// 多线程并发扩容时，链表可能形成环，导致 get() 死循环</code></pre> <p><strong>2. JDK 8 数据丢失</strong></p> <pre><code class="language-java" data-lang="java">// JDK 8 使用尾插法避免了死循环，但仍存在数据丢失问题
final V putVal(int hash, K key, V value, boolean onlyIfAbsent) {
    // 两个线程同时判断桶为空，都执行写入
    // 后写入的会覆盖先写入的，导致数据丢失
    if ((p = tab[i = (n - 1) &amp; hash]) == null)
        tab[i] = newNode(hash, key, value, null);  // 非原子操作
}</code></pre> <H3>四、null 键值处理差异</H3> <pre><code class="language-java" data-lang="java">// HashMap - 允许 null
HashMap&lt;String, String&gt; map = new HashMap&lt;&gt;();
map.put(null, "value");  // ✅ 允许
map.put("key", null);    // ✅ 允许

// Hashtable / ConcurrentHashMap - 不允许 null
ConcurrentHashMap&lt;String, String&gt; cmap = new ConcurrentHashMap&lt;&gt;();
cmap.put(null, "value");  // ❌ NullPointerException
cmap.put("key", null);    // ❌ NullPointerException</code></pre> <p><strong>为什么不允许 null？</strong></p> <p>在多线程环境下， <code>get(key)</code> 返回 <code>null</code> 存在二义性：</p> <ul> <li>key 不存在</li> <li>key 存在但 value 为 null</li> </ul> <p>单线程的 <code>HashMap</code> 可以用 <code>containsKey()</code> 判断，但多线程下判断和获取之间存在竞态条件。</p> <H3>五、迭代器特性</H3> <pre><code class="language-java" data-lang="java">// HashMap/Hashtable - 快速失败（Fail-Fast）
HashMap&lt;String, String&gt; map = new HashMap&lt;&gt;();
Iterator&lt;String&gt; it = map.keySet().iterator();
map.put("newKey", "value");  // 结构性修改
it.next();  // 抛出 ConcurrentModificationException

// ConcurrentHashMap - 弱一致性（Weakly Consistent）
ConcurrentHashMap&lt;String, String&gt; cmap = new ConcurrentHashMap&lt;&gt;();
Iterator&lt;String&gt; cit = cmap.keySet().iterator();
cmap.put("newKey", "value");  // 不会抛异常
cit.next();  // 可能反映也可能不反映新数据，但不会抛异常</code></pre> <H3>六、最佳实践</H3> <pre><code class="language-java" data-lang="java">// ❌ 错误：多线程使用 HashMap
Map&lt;String, String&gt; map = new HashMap&lt;&gt;();
// 多线程并发写入可能导致数据丢失、死循环（JDK 7）

// ❌ 错误：使用 Hashtable
Map&lt;String, String&gt; table = new Hashtable&lt;&gt;();  // 性能太差，已淘汰

// ✅ 正确：多线程使用 ConcurrentHashMap
Map&lt;String, String&gt; cmap = new ConcurrentHashMap&lt;&gt;();

// ✅ 进阶：根据并发量调整初始容量
// 避免频繁扩容，预估元素数量 / 负载因子 + 1
Map&lt;String, String&gt; cmap = new ConcurrentHashMap&lt;&gt;(64);

// ✅ 读多写少场景可考虑 CopyOnWrite 方案（但内存开销大）
// 适合配置表、黑白名单等场景</code></pre> <H2>面试高频追问</H2> <ol> <li> <p><strong>ConcurrentHashMap 在 JDK 7 和 JDK 8 中的实现有什么区别？</strong></p> <ul> <li>JDK 7：分段锁（ <code>Segment</code> + <code>ReentrantLock</code> ），并发度受分段数限制</li> <li>JDK 8：CAS + <code>synchronized</code> 桶级别锁，并发度更高，内存占用更低</li> </ul> </li> <li> <p><strong>为什么 ConcurrentHashMap 不允许 null 键和 null 值？</strong></p> <ul> <li>多线程环境下 <code>get()</code> 返回 <code>null</code> 存在二义性（不存在 vs 值为 null）</li> <li>避免在 <code>containsKey()</code> 判断和 <code>get()</code> 获取之间出现竞态条件</li> </ul> </li> <li> <p><strong>ConcurrentHashMap 的扩容是怎样实现的？</strong></p> <ul> <li>JDK 8 采用多线程协同扩容：每个线程负责一部分桶的迁移</li> <li>通过 <code>transferIndex</code> 协调分配任务，支持并发扩容提升效率</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"HashMap 在多线程环境下会有什么问题？"</li> <li>"为什么 Hashtable 被淘汰了？"</li> <li>"ConcurrentHashMap 如何保证线程安全？"</li> </ul> <H2>记忆口诀</H2> <p><strong>选择口诀</strong> ：</p> <ul> <li><strong>单线程用 HashMap</strong> ：性能最高，允许 null</li> <li><strong>多线程用 ConcurrentHashMap</strong> ：细粒度锁，高并发</li> <li><strong>Hashtable 别用了</strong> ：全表锁，已淘汰</li> </ul> <p><strong>锁粒度记忆</strong> ：</p> <ul> <li>Hashtable = 大锅饭（一把锁）</li> <li>ConcurrentHashMap (JDK 7) = 分餐制（分段锁）</li> <li>ConcurrentHashMap (JDK 8) = 自助餐（桶级别锁）</li> </ul> <H2>总结</H2> <p><code>HashMap</code> 非线程安全但性能最高，适合单线程； <code>Hashtable</code> 使用全表 <code>synchronized</code> 锁，性能差已被淘汰； <code>ConcurrentHashMap</code> 是多线程首选，JDK 8 采用 CAS + <code>synchronized</code> 桶级别锁实现高并发，迭代器弱一致性，不允许 null 键值。生产环境多线程场景必须使用 <code>ConcurrentHashMap</code> 。</p> </div></main>