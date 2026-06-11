---
title: ConcurrentHashMap 是如何保证线程安全的
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>版本差异理解</strong> ：面试官不仅仅是想知道 "用了锁" 这个结论，更是想知道你是否了解 JDK 1.7（分段锁）和 JDK 1.8（CAS + synchronized）两种截然不同的实现方式。</p> </li> <li> <p><strong>并发原理深度</strong> ：考察你是否理解 CAS 无锁操作、synchronized 锁升级、volatile 可见性等底层机制，以及它们如何协同工作。</p> </li> <li> <p><strong>对比分析能力</strong> ：能否说清楚 ConcurrentHashMap 与 Hashtable、 <code>Collections.synchronizedMap()</code> 的区别，以及为什么性能更好。</p> </li> </ol> <H2>核心答案</H2> <p>ConcurrentHashMap 在 <strong>JDK 1.8</strong> 中通过 <strong>"CAS + synchronized + volatile"</strong> 三者协同保证线程安全：</p> <table> <thead> <tr> <th>机制</th> <th>作用</th> <th>应用场景</th> </tr> </thead> <tbody> <tr> <td><strong>CAS</strong></td> <td>无锁更新</td> <td>空桶插入、size 计数</td> </tr> <tr> <td><strong>synchronized</strong></td> <td>锁桶头节点</td> <td>哈希冲突时的插入/更新/删除</td> </tr> <tr> <td><strong>volatile</strong></td> <td>保证可见性</td> <td>Node 的 val 和 next 字段</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ：JDK 1.8 用 <strong>CAS 尝试无锁插入</strong> ，失败则 <strong>synchronized 锁单个桶</strong> ，配合 <strong>volatile 保证可见性</strong> ，实现高并发安全。</p> <H2>深度解析</H2> <H3>一、JDK 1.7 vs JDK 1.8 实现对比</H3>   <p>上图对比了两个版本的核心差异。关键理解：</p> <ul> <li> <p><strong>JDK 1.7 分段锁</strong> ：将数据分成多个 Segment（默认 16 个），每个 Segment 是一个小的 HashMap，用 <code>ReentrantLock</code> 保护。并发度受限于 Segment 数量。</p> </li> <li> <p><strong>JDK 1.8 桶级锁</strong> ：放弃 Segment，直接对每个桶的头节点加锁。并发度等于桶数量，远高于分段锁。</p> </li> <li> <p><strong>为什么改？</strong> 分段锁的 Segment 数量固定，无法动态扩展；桶级锁更细粒度，并发度更高。</p> </li> </ul> <H3>二、JDK 1.8 put 操作流程</H3>   <p>上图展示了 <code>put()</code> 方法的核心流程。关键点：</p> <ul> <li><strong>步骤 2 - CAS 无锁插入</strong> ：如果桶为空，用 CAS 操作直接插入，无需加锁，性能最优</li> <li><strong>步骤 3 - 协助扩容</strong> ：如果检测到正在扩容，当前线程会帮忙迁移数据</li> <li><strong>步骤 4 - synchronized 锁桶头</strong> ：只有桶不为空时才加锁，且只锁当前桶的头节点</li> <li><strong>锁粒度</strong> ：不同桶的操作可以完全并发，互不影响</li> </ul> <H3>三、三大安全机制详解</H3>   <p>上图详细解释了三大安全机制。关键理解：</p> <ul> <li><strong>CAS</strong> ：用于无竞争场景，比如空桶插入，不需要阻塞等待</li> <li><strong>synchronized</strong> ：用于有竞争场景，但只锁单个桶，不影响其他桶的操作</li> <li><strong>volatile</strong> ：保证读操作的可见性，读操作完全无锁</li> </ul> <H3>四、核心源码解析</H3> <pre><code class="language-java" data-lang="java">// ConcurrentHashMap.putVal() 核心逻辑（简化版）
final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());

    for (Node&lt;K,V&gt;[] tab = table;;) {
        Node&lt;K,V&gt; f; int n, i, fh;

        // 1. 延迟初始化 table
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();

        // 2. 桶为空，CAS 无锁插入
        else if ((f = tabAt(tab, i = (n - 1) &amp; hash)) == null) {
            if (casTabAt(tab, i, null, new Node&lt;K,V&gt;(hash, key, value, null)))
                break;  // CAS 成功，插入完成
            // CAS 失败，自旋重试
        }

        // 3. 正在扩容，帮忙迁移
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);

        // 4. 桶不为空，synchronized 锁桶头节点
        else {
            V oldVal = null;
            synchronized (f) {  // 锁桶头节点
                if (tabAt(tab, i) == f) {  // 双重检查
                    // 链表遍历
                    if (fh &gt;= 0) {
                        for (Node&lt;K,V&gt; e = f;; ++binCount) {
                            K ek;
                            // 找到相同 key，更新 value
                            if (e.hash == hash &amp;&amp;
                                ((ek = e.key) == key ||
                                 (ek != null &amp;&amp; key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            // 没找到，尾插新节点
                            Node&lt;K,V&gt; pred = e;
                            if ((e = e.next) == null) {
                                pred.next = new Node&lt;K,V&gt;(hash, key, value, null);
                                break;
                            }
                        }
                    }
                    // 红黑树处理...
                }
            }
            // 检查是否需要树化
            if (binCount != 0) {
                if (binCount &gt;= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);  // 更新 size（CAS + LongAdder 思想）
    return null;
}

// volatile 读操作（Unsafe 类实现）
static final &lt;K,V&gt; Node&lt;K,V&gt; tabAt(Node&lt;K,V&gt;[] tab, int i) {
    return (Node&lt;K,V&gt;)U.getObjectVolatile(tab, ((long)i &lt;&lt; ASHIFT) + ABASE);
}

// CAS 写操作
static final &lt;K,V&gt; boolean casTabAt(Node&lt;K,V&gt;[] tab, int i,
                                    Node&lt;K,V&gt; c, Node&lt;K,V&gt; v) {
    return U.compareAndSwapObject(tab, ((long)i &lt;&lt; ASHIFT) + ABASE, c, v);
}</code></pre> <H3>五、与 Hashtable、Collections.synchronizedMap 对比</H3> <table> <thead> <tr> <th>对比项</th> <th>Hashtable</th> <th>Collections.synchronizedMap</th> <th>ConcurrentHashMap</th> </tr> </thead> <tbody> <tr> <td><strong>锁粒度</strong></td> <td>整个表</td> <td>整个表</td> <td>单个桶</td> </tr> <tr> <td><strong>锁类型</strong></td> <td>synchronized</td> <td>synchronized</td> <td>CAS + synchronized</td> </tr> <tr> <td><strong>读操作</strong></td> <td>加锁</td> <td>加锁</td> <td>无锁（volatile）</td> </tr> <tr> <td><strong>写操作</strong></td> <td>阻塞其他所有操作</td> <td>阻塞其他所有操作</td> <td>只阻塞同桶操作</td> </tr> <tr> <td><strong>并发度</strong></td> <td>1（串行）</td> <td>1（串行）</td> <td>桶数量（极高）</td> </tr> <tr> <td><strong>null 键值</strong></td> <td>❌ 不允许</td> <td>✅ 允许（1 个 null key）</td> <td>❌ 不允许</td> </tr> <tr> <td><strong>性能</strong></td> <td>⭐</td> <td>⭐</td> <td>⭐⭐⭐⭐⭐</td> </tr> </tbody> </table>   <H3>六、读操作为什么不需要加锁？</H3> <pre><code class="language-java" data-lang="java">// get() 方法：完全无锁
public V get(Object key) {
    Node&lt;K,V&gt; e;
    return (e = find(hash(key), key)) == null ? null : e.val;
}

// Node 的 val 和 next 都是 volatile 的
static class Node&lt;K,V&gt; {
    final int hash;
    final K key;
    volatile V val;           // volatile 保证可见性
    volatile Node&lt;K,V&gt; next;  // volatile 保证可见性
}</code></pre> <p><strong>为什么读不需要加锁？</strong></p> <ul> <li><strong>volatile 保证可见性</strong> ：一个线程修改了 <code>val</code> 或 <code>next</code> ，其他线程立即能看到最新值</li> <li><strong>不可变结构</strong> ：Node 的 <code>hash</code> 和 <code>key</code> 是 <code>final</code> 的，不会被修改</li> <li><strong>安全发布</strong> ：新节点通过 CAS 或 synchronized 写入，保证构造完成后再发布</li> </ul> <H2>面试高频追问</H2> <ol> <li> <p><strong>ConcurrentHashMap 能完全替代 Hashtable 吗？</strong></p> <ul> <li>几乎可以！但要注意：ConcurrentHashMap <strong>不允许 null 键值</strong> ，Hashtable 也不允许</li> <li>如果代码依赖 null 键值，需要修改</li> </ul> </li> <li> <p><strong>ConcurrentHashMap 的迭代器是 fail-fast 还是 fail-safe？</strong></p> <ul> <li><strong>fail-safe</strong> ！迭代时不会抛 <code>ConcurrentModificationException</code></li> <li>但可能读到 "弱一致性" 的数据（迭代期间的修改可能看不到）</li> </ul> </li> <li> <p><strong>size() 方法如何保证准确性？</strong></p> <ul> <li>JDK 1.8 使用 <code>LongAdder</code> 思想：分散热点，多个计数器累加</li> <li>返回的是一个 "近似值"，在并发环境下不完全准确</li> </ul> </li> <li> <p><strong>为什么用 synchronized 而不是 ReentrantLock？</strong></p> <ul> <li>synchronized 在 JDK 1.6 后有大量优化（锁升级）</li> <li>内存开销更小（不需要额外创建 Lock 对象）</li> <li>在低竞争场景性能相当，高竞争场景更省内存</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"ConcurrentHashMap 和 Hashtable 的区别？"</li> <li>"JDK 1.7 和 1.8 的 ConcurrentHashMap 有什么不同？"</li> <li>"ConcurrentHashMap 的 get() 需要加锁吗？为什么？"</li> <li>"ConcurrentHashMap 如何统计 size？"</li> </ul> <H2>记忆口诀</H2> <p><strong>JDK 1.8 三大机制</strong> ：CAS 先试无锁插，失败 synchronized 锁桶头，volatile 保可见读无锁。</p> <p><strong>锁粒度</strong> ：只锁桶头不锁表，不同桶并发跑。</p> <p><strong>对比</strong> ：Hashtable 全表锁性能差，ConcurrentHashMap 桶级锁并发高。</p> <H2>总结</H2> <p>ConcurrentHashMap 在 JDK 1.8 通过 <strong>CAS + synchronized + volatile</strong> 三者协同保证线程安全： <strong>CAS</strong> 用于空桶无锁插入， <strong>synchronized</strong> 用于哈希冲突时锁单个桶头节点， <strong>volatile</strong> 保证 Node 的 val 和 next 可见性。与 Hashtable 的全表锁相比，ConcurrentHashMap 的 <strong>桶级锁</strong> 实现了极高的并发度， <strong>读操作完全无锁</strong> 。记住： <strong>锁粒度细、读无锁、写只锁桶</strong> 。</p> </div></main>