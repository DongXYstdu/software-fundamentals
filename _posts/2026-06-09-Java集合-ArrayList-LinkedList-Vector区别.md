---
title: ArrayList、LinkedList Vector 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>集合框架基础</strong> ：面试官不仅仅想知道你能说出这三者的区别，更想考察你是否理解 List 接口的不同实现方式及其底层原理，包括数组与链表的本质差异。</p> </li> <li> <p><strong>性能敏感度</strong> ：考察你是否清楚不同场景下的性能表现，能否根据实际业务需求（查询多还是增删多）选择合适的数据结构。</p> </li> <li> <p><strong>线程安全意识</strong> ：Vector 作为线程安全的集合，面试官想了解你是否知道它的实现方式以及为什么在实际开发中很少使用。</p> </li> </ol> <H2>核心答案</H2> <p>三者都实现了 <code>List</code> 接口，但底层实现和特性差异明显：</p> <table> <thead> <tr> <th>特性</th> <th>ArrayList</th> <th>LinkedList</th> <th>Vector</th> </tr> </thead> <tbody> <tr> <td>底层结构</td> <td>动态数组</td> <td>双向链表</td> <td>动态数组</td> </tr> <tr> <td>线程安全</td> <td>❌ 不安全</td> <td>❌ 不安全</td> <td>✅ 安全（ <code>synchronized</code> ）</td> </tr> <tr> <td>默认容量</td> <td>10</td> <td>无（链表无容量概念）</td> <td>10</td> </tr> <tr> <td>扩容机制</td> <td>1.5 倍</td> <td>无需扩容</td> <td>2 倍</td> </tr> <tr> <td>随机访问</td> <td>O(1) 快</td> <td>O(n) 慢</td> <td>O(1) 快</td> </tr> <tr> <td>头部插入/删除</td> <td>O(n) 慢</td> <td>O(1) 快</td> <td>O(n) 慢</td> </tr> <tr> <td>内存占用</td> <td>连续内存，较少</td> <td>节点额外存储前后指针</td> <td>连续内存，较少</td> </tr> <tr> <td>适用场景</td> <td>查询多、尾部增删</td> <td>频繁增删、尤其是头部</td> <td>基本不用（性能差）</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ：日常开发 90% 用 <code>ArrayList</code> ，频繁头部增删用 <code>LinkedList</code> ， <code>Vector</code> 基本被淘汰（可用 <code>Collections.synchronizedList</code> 或 <code>CopyOnWriteArrayList</code> 替代）。</p> <H2>深度解析</H2> <H3>一、底层数据结构对比</H3>   <p>上图展示了两种核心数据结构的内存布局差异：</p> <ul> <li> <p><strong>ArrayList</strong> ：使用连续的数组存储元素，每个元素通过下标直接定位。由于内存连续，CPU 缓存命中率高，遍历性能好。但插入删除需要移动后续元素。</p> </li> <li> <p><strong>LinkedList</strong> ：每个元素包装成 Node 节点，包含数据、前驱指针 <code>prev</code> 和后继指针 <code>next</code> 。节点分散在堆内存各处，插入删除只需修改指针，但随机访问需要从头遍历。</p> </li> </ul> <H3>二、性能对比详解</H3> <p><strong>1. 随机访问性能</strong></p> <pre><code class="language-java" data-lang="java">// ArrayList - O(1)
ArrayList&lt;String&gt; arrayList = new ArrayList&lt;&gt;();
arrayList.get(1000);  // 直接通过下标访问：elementData[index]

// LinkedList - O(n)
LinkedList&lt;String&gt; linkedList = new LinkedList&lt;&gt;();
linkedList.get(1000);  // 需要从头或尾遍历到第 1000 个节点</code></pre> <p><code>ArrayList</code> 的 <code>get(int index)</code> 直接返回 <code>elementData[index]</code> ，时间复杂度 O(1)。</p> <p><code>LinkedList</code> 需要判断 index 在前半部分还是后半部分，然后从 head 或 tail 开始遍历：</p> <pre><code class="language-java" data-lang="java">// LinkedList 源码
Node&lt;E&gt; node(int index) {
    if (index &lt; (size &gt;&gt; 1)) {  // 前半部分，从头遍历
        Node&lt;E&gt; x = first;
        for (int i = 0; i &lt; index; i++)
            x = x.next;
        return x;
    } else {  // 后半部分，从尾遍历
        Node&lt;E&gt; x = last;
        for (int i = size - 1; i &gt; index; i--)
            x = x.prev;
        return x;
    }
}</code></pre> <p><strong>2. 插入/删除性能</strong></p> <pre><code class="language-java" data-lang="java">// 头部插入对比
arrayList.add(0, "x");   // O(n)：需要移动所有元素
linkedList.addFirst("x"); // O(1)：只需修改两个指针

// 尾部插入对比
arrayList.add("x");       // O(1) 均摊：直接放入数组末尾
linkedList.addLast("x");  // O(1)：修改尾指针

// 中间插入对比
arrayList.add(5000, "x");   // O(n)：需要移动一半元素
linkedList.add(5000, "x");  // O(n)：需要先遍历找到位置，但插入本身 O(1)</code></pre> <p><strong>关键结论</strong> ：</p> <ul> <li>尾部操作： <code>ArrayList</code> 更快（无指针开销）</li> <li>头部操作： <code>LinkedList</code> 完胜</li> <li>中间操作：两者都是 O(n)，但 <code>ArrayList</code> 通常更快（遍历 + 移动 vs 遍历 + 指针操作）</li> </ul> <H3>三、扩容机制</H3> <p><strong>ArrayList 扩容</strong> ：</p> <pre><code class="language-java" data-lang="java">// 添加元素时检查容量
public boolean add(E e) {
    ensureCapacityInternal(size + 1);  // 确保容量足够
    elementData[size++] = e;
    return true;
}

// 扩容核心逻辑
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity &gt;&gt; 1);  // 1.5 倍
    // ... 省略边界检查
    elementData = Arrays.copyOf(elementData, newCapacity);  // 复制到新数组
}</code></pre> <p><strong>Vector 扩容</strong> ：</p> <pre><code class="language-java" data-lang="java">private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    // capacityIncrement 默认为 0，所以通常是 2 倍扩容
    int newCapacity = oldCapacity + ((capacityIncrement &gt; 0) ?
                                     capacityIncrement : oldCapacity);
    // ...
}</code></pre> <table> <thead> <tr> <th>对比项</th> <th>ArrayList</th> <th>Vector</th> </tr> </thead> <tbody> <tr> <td>扩容倍数</td> <td>1.5 倍</td> <td>2 倍</td> </tr> <tr> <td>扩容策略</td> <td>节省内存</td> <td>更激进</td> </tr> <tr> <td>可自定义增量</td> <td>❌</td> <td>✅ <code>capacityIncrement</code></td> </tr> </tbody> </table> <H3>四、线程安全性</H3> <p><strong>Vector 的同步实现</strong> ：</p> <pre><code class="language-java" data-lang="java">// Vector 几乎所有方法都加了 synchronized
public synchronized boolean add(E e) { ... }
public synchronized E get(int index) { ... }
public synchronized E remove(int index) { ... }</code></pre> <p><strong>问题</strong> ：粗粒度锁导致并发性能差，即使是读操作也会阻塞。</p> <p><strong>更好的替代方案</strong> ：</p> <pre><code class="language-java" data-lang="java">// 方案一：Collections.synchronizedList（适合读多写少）
List&lt;String&gt; list = Collections.synchronizedList(new ArrayList&lt;&gt;());

// 方案二：CopyOnWriteArrayList（适合读非常多、写很少）
List&lt;String&gt; list = new CopyOnWriteArrayList&lt;&gt;();</code></pre> <H3>五、最佳实践</H3> <pre><code class="language-java" data-lang="java">// ❌ 错误：不知道容量，频繁扩容
List&lt;String&gt; list = new ArrayList&lt;&gt;();
for (int i = 0; i &lt; 100000; i++) {
    list.add("item" + i);  // 触发多次扩容，性能差
}

// ✅ 正确：预估容量，避免扩容
List&lt;String&gt; list = new ArrayList&lt;&gt;(100000);

// ✅ 场景选择
// 场景1：查询为主（如缓存列表、配置项）→ ArrayList
// 场景2：频繁头部增删（如消息队列）→ LinkedList 或 ArrayDeque
// 场景3：需要线程安全 → CopyOnWriteArrayList 或 Collections.synchronizedList</code></pre> <H2>面试高频追问</H2> <ol> <li> <p><strong>ArrayList 的扩容为什么是 1.5 倍？</strong></p> <ul> <li>折中方案：既避免频繁扩容（如 1.1 倍），又减少内存浪费（如 2 倍）</li> <li>通过位运算 <code>oldCapacity + (oldCapacity &gt;&gt; 1)</code> 高效计算</li> </ul> </li> <li> <p><strong>LinkedList 既然插入删除快，为什么实际很少用？</strong></p> <ul> <li>CPU 缓存不友好（内存不连续）</li> <li>节点对象有额外内存开销（32 字节 vs 数组的 4-8 字节引用）</li> <li>实际场景中尾部操作更多， <code>ArrayList</code> 更优</li> </ul> </li> <li> <p><strong>为什么阿里开发手册建议初始化 ArrayList 时指定容量？</strong></p> <ul> <li>避免多次扩容导致的数组复制开销</li> <li>扩容期间会同时存在两个数组，内存峰值翻倍</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"ArrayList 和 LinkedList 谁更节省内存？"</li> <li>"频繁在列表中间插入元素，选哪个？"</li> <li>"如何实现一个线程安全的 ArrayList？"</li> </ul> <H2>记忆口诀</H2> <p><strong>选择口诀</strong> ：</p> <ul> <li><strong>查询多用 ArrayList</strong> ：数组连续好定位</li> <li><strong>头插多用 LinkedList</strong> ：链表指针改得快</li> <li><strong>Vector 几乎不用</strong> ：同步太粗性能差</li> </ul> <H2>总结</H2> <p><code>ArrayList</code> 基于动态数组，随机访问 O(1)、尾部增删 O(1)，适合查询为主的场景； <code>LinkedList</code> 基于双向链表，头部增删 O(1) 但随机访问 O(n)，适合频繁头部操作； <code>Vector</code> 虽然线程安全但使用粗粒度锁性能差，已被 <code>CopyOnWriteArrayList</code> 等并发集合替代。实际开发中，预估容量初始化 <code>ArrayList</code> ，特殊场景再考虑 <code>LinkedList</code> 。</p> </div></main>