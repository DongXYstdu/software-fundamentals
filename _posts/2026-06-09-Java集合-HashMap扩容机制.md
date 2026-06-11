---
title: 说说 HashMap 的扩容机制？如何扩容的？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>基础掌握度</strong> ：面试官不仅仅是想知道 "会扩容" 这个事实，更是想知道你是否理解扩容的触发条件、扩容阈值计算、以及扩容时元素如何重新分布。</p> </li> <li> <p><strong>源码理解深度</strong> ：考察你是否读过 <code>resize()</code> 方法的源码，是否理解 JDK 1.8 中 "高低位链表" 的优化设计，以及为什么扩容后元素要么在原位置，要么在 "原位置 + 原容量" 的位置。</p> </li> <li> <p><strong>版本演进意识</strong> ：JDK 1.7 和 JDK 1.8 的扩容机制有显著差异（头插法 vs 尾插法），考察你是否了解这些变化以及背后的原因（死循环问题）。</p> </li> </ol> <H2>核心答案</H2> <p>HashMap 的扩容机制可以概括为： <strong>当元素数量超过 <code>容量 × 负载因子</code> 时，容量翻倍，并重新分配所有元素</strong> 。</p> <table> <thead> <tr> <th>关键点</th> <th>说明</th> </tr> </thead> <tbody> <tr> <td><strong>默认初始容量</strong></td> <td>16</td> </tr> <tr> <td><strong>默认负载因子</strong></td> <td>0.75</td> </tr> <tr> <td><strong>扩容阈值</strong></td> <td><code>capacity × loadFactor</code> （首次为 12 = 16 × 0.75）</td> </tr> <tr> <td><strong>扩容方式</strong></td> <td>容量翻倍（ <code>newCap = oldCap &lt;&lt; 1</code> ）</td> </tr> <tr> <td><strong>触发条件</strong></td> <td><code>size &gt; threshold</code> 且当前桶位置非空</td> </tr> <tr> <td><strong>元素重分布</strong></td> <td>根据新增的最高位判断：原位置 或 原位置 + 原容量</td> </tr> </tbody> </table> <H2>深度解析</H2> <H3>一、扩容触发时机</H3> <p>扩容发生在调用 <code>putVal()</code> 方法插入元素后，满足以下两个条件时触发：</p>   <p>上图展示了扩容的两个必要条件。这里有几个关键点需要理解：</p> <ul> <li> <p><strong>为什么需要两个条件？</strong> 这是一个性能优化。如果当前桶为空，直接放入即可，不需要立即扩容。只有当发生哈希冲突时，才考虑扩容以减少冲突概率。</p> </li> <li> <p><strong>threshold 的计算</strong> ： <code>threshold = capacity × loadFactor</code> 。默认情况下，首次扩容阈值为 12（16 × 0.75）。</p> </li> <li> <p><strong>负载因子为什么是 0.75？</strong> 这是时间和空间的权衡：</p> <ul> <li>太大（如 1.0）：空间利用率高，但哈希冲突多，查询效率低</li> <li>太小（如 0.5）：哈希冲突少，查询效率高，但空间浪费</li> <li>0.75 是经过数学计算得出的平衡值，来自泊松分布</li> </ul> </li> </ul> <H3>二、扩容核心流程</H3>   <p>上图展示了 HashMap 扩容的完整流程。整个过程分为 5 个关键步骤：</p> <ul> <li> <p><strong>步骤一 - 计算新容量</strong> ：使用位运算 <code>oldCap &lt;&lt; 1</code> 实现翻倍，效率极高。容量始终保持 2 的幂次方，这是为了让 <code>(n - 1) &amp; hash</code> 能够均匀分布。</p> </li> <li> <p><strong>步骤二 - 计算新阈值</strong> ：新阈值也需要翻倍，保持负载因子的约束。</p> </li> <li> <p><strong>步骤三 - 创建新数组</strong> ：在堆中分配一个新的 <code>Node</code> 数组，大小为新容量。</p> </li> <li> <p><strong>步骤四 - 迁移元素</strong> ：这是最核心的步骤，需要遍历旧数组的每个桶，将链表或红黑树中的元素重新分配到新数组中。</p> </li> <li> <p><strong>步骤五 - 更新引用</strong> ：将 <code>table</code> 指向新数组，完成扩容。</p> </li> </ul> <H3>三、元素重分布原理（核心！）</H3> <p>这是面试中 <strong>最重要的考点</strong> 。JDK 1.8 中，扩容后元素的位置分布有一个巧妙的规律：</p>   <p>上图揭示了 JDK 1.8 扩容的核心优化。让我详细解释这个精妙的设计：</p> <ul> <li> <p><strong>为什么是两种可能？</strong> 因为容量从 2^n 变成 2^(n+1)，掩码只多了一位。这一位要么是 0，要么是 1，所以元素的新位置只有两种可能。</p> </li> <li> <p><strong>低位链表（loHead/loTail）</strong> ：第 n 位为 0 的元素，扩容后索引不变，组成 "低位链表"。</p> </li> <li> <p><strong>高位链表（hiHead/hiTail）</strong> ：第 n 位为 1 的元素，扩容后索引 = 原索引 + 原容量，组成 "高位链表"。</p> </li> <li> <p><strong>为什么用 <code>(e.hash &amp; oldCap) == 0</code> 判断？</strong> 这里不是用 <code>n-1</code> ，而是直接用 <code>oldCap</code> （如 16 = 10000）。只有 hash 的第 5 位为 0 时， <code>hash &amp; 16</code> 才等于 0。</p> </li> </ul> <H3>四、源码核心片段</H3> <pre><code class="language-java" data-lang="java">// JDK 1.8 resize() 方法核心逻辑
final Node&lt;K,V&gt;[] resize() {
    Node&lt;K,V&gt;[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;

    // 1. 计算新容量和新阈值
    if (oldCap &gt; 0) {
        if (oldCap &gt;= MAXIMUM_CAPACITY) {  // 已达最大容量，不再扩容
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        else if ((newCap = oldCap &lt;&lt; 1) &lt; MAXIMUM_CAPACITY &amp;&amp;  // 容量翻倍
                 oldCap &gt;= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr &lt;&lt; 1;  // 阈值翻倍
    }
    // ... 省略其他分支

    Node&lt;K,V&gt;[] newTab = (Node&lt;K,V&gt;[])new Node[newCap];
    table = newTab;

    // 2. 遍历旧数组，迁移元素
    if (oldTab != null) {
        for (int j = 0; j &lt; oldCap; ++j) {
            Node&lt;K,V&gt; e;
            if ((e = oldTab[j]) != null) {
                oldTab[j] = null;  // 帮助 GC
                if (e.next == null)
                    // 单个节点，直接计算新位置
                    newTab[e.hash &amp; (newCap - 1)] = e;
                else if (e instanceof TreeNode)
                    // 红黑树拆分
                    ((TreeNode&lt;K,V&gt;)e).split(this, newTab, j, oldCap);
                else {
                    // 3. 链表拆分：高低位链表
                    Node&lt;K,V&gt; loHead = null, loTail = null;  // 低位链表
                    Node&lt;K,V&gt; hiHead = null, hiTail = null;  // 高位链表
                    Node&lt;K,V&gt; next;
                    do {
                        next = e.next;
                        if ((e.hash &amp; oldCap) == 0) {
                            // 低位：索引不变
                            if (loTail == null)
                                loHead = e;
                            else
                                loTail.next = e;
                            loTail = e;
                        }
                        else {
                            // 高位：索引 = 原索引 + 原容量
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);

                    // 4. 将拆分后的链表放到新数组
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;  // 低位放原位置
                    }
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;  // 高位放原位置+原容量
                    }
                }
            }
        }
    }
    return newTab;
}</code></pre> <H3>五、JDK 1.7 vs JDK 1.8 扩容对比</H3> <table> <thead> <tr> <th>对比项</th> <th>JDK 1.7</th> <th>JDK 1.8</th> </tr> </thead> <tbody> <tr> <td><strong>链表插入方式</strong></td> <td>头插法</td> <td>尾插法</td> </tr> <tr> <td><strong>扩容后顺序</strong></td> <td>链表元素顺序 <strong>反转</strong></td> <td>链表元素顺序 <strong>保持不变</strong></td> </tr> <tr> <td><strong>元素位置计算</strong></td> <td>重新计算 <code>h &amp; (length-1)</code></td> <td>高低位链表优化，无需重新计算</td> </tr> <tr> <td><strong>并发问题</strong></td> <td>多线程扩容可能导致 <strong>死循环</strong></td> <td>死循环问题已解决</td> </tr> <tr> <td><strong>红黑树</strong></td> <td>无</td> <td>链表 ≥ 8 且容量 ≥ 64 时转红黑树</td> </tr> </tbody> </table> <p><strong>JDK 1.7 死循环问题原因</strong> ：</p>   <p>上图解释了 JDK 1.7 的经典死循环问题。关键点：</p> <ul> <li><strong>头插法</strong> ：新元素总是插到链表头部</li> <li><strong>并发场景</strong> ：两个线程同时扩容，一个暂停，另一个完成</li> <li><strong>顺序反转</strong> ：线程 2 完成后，链表顺序从 A→B 变成 B→A</li> <li><strong>形成环</strong> ：线程 1 继续执行时，基于旧的 next 指针操作，导致 A 和 B 互指</li> <li><strong>JDK 1.8 解决</strong> ：改用尾插法，顺序保持不变，避免了这个问题</li> </ul> <H2>面试高频追问</H2> <ol> <li> <p><strong>为什么容量必须是 2 的幂次方？</strong></p> <ul> <li>让 <code>(n - 1) &amp; hash</code> 等价于 <code>hash % n</code> ，位运算效率更高</li> <li>保证散列均匀，避免空间浪费</li> </ul> </li> <li> <p><strong>扩容时每个元素都需要重新计算 hash 吗？</strong></p> <ul> <li>不需要！只需判断新增的高位是 0 还是 1，用 <code>(e.hash &amp; oldCap) == 0</code> 即可</li> </ul> </li> <li> <p><strong>HashMap 是线程安全的吗？扩容时会有什么问题？</strong></p> <ul> <li>不是线程安全的。JDK 1.7 并发扩容可能死循环，JDK 1.8 可能数据丢失</li> <li>推荐使用 <code>ConcurrentHashMap</code></li> </ul> </li> <li> <p><strong>负载因子可以修改吗？什么场景需要调整？</strong></p> <ul> <li>可以，构造函数可指定 <code>loadFactor</code></li> <li>内存紧张时可调高（如 0.85），查询频繁时可调低（如 0.5）</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"HashMap 的负载因子为什么是 0.75？"</li> <li>"JDK 1.7 和 1.8 的 HashMap 扩容有什么区别？"</li> <li>"为什么 JDK 1.8 改用尾插法？解决了什么问题？"</li> <li>"扩容时元素如何重新分配？为什么只有两种可能？"</li> </ul> <H2>记忆口诀</H2> <p><strong>扩容三要素</strong> ：容量翻倍、阈值翻倍、高低位分家</p> <p><strong>位置判断</strong> ：新位为 0 留原地，新位为 1 加原容（ <code>(hash &amp; oldCap) == 0</code> → 低位链表，否则高位链表）</p> <H2>总结</H2> <p>HashMap 扩容在 <code>size &gt; threshold</code> 时触发，容量翻倍（ <code>&lt;&lt; 1</code> ），使用 <strong>高低位链表</strong> 优化元素重分布——根据 hash 新增位的值，元素要么留在原位置，要么移动到 "原位置 + 原容量"。JDK 1.8 改用尾插法解决了 JDK 1.7 并发扩容的死循环问题。记住： <strong>负载因子 0.75、容量 2 的幂、高低位分家</strong> 。</p> </div></main>