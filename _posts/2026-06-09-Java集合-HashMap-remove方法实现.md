---
title: HashMap remove 方法是如何实现的
date: 2026-06-09 09:00:00 +0800
categories: [Java, 集合]
tags: [Java, 集合, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>源码理解深度</strong> ：面试官不仅仅是想知道 "调用 remove 删除元素" 这个表面行为，更是想知道你是否理解底层的删除逻辑，包括链表节点删除、红黑树节点删除、以及退树化条件。</p> </li> <li> <p><strong>数据结构掌握</strong> ：考察你是否了解链表删除（指针操作）和红黑树删除（复杂旋转和变色）的区别，以及为什么红黑树删除更复杂。</p> </li> <li> <p><strong>边界条件意识</strong> ：是否考虑删除头节点、尾节点、中间节点的不同处理，以及删除后是否需要退树化。</p> </li> </ol> <H2>核心答案</H2> <p>HashMap 的 <code>remove()</code> 方法核心流程： <strong>定位桶 → 遍历查找 → 删除节点 → 更新指针/重构树 → 返回旧值</strong> 。</p> <table> <thead> <tr> <th>删除场景</th> <th>数据结构</th> <th>操作方式</th> <th>时间复杂度</th> </tr> </thead> <tbody> <tr> <td>桶为空</td> <td>-</td> <td>直接返回 null</td> <td>O(1)</td> </tr> <tr> <td>单节点</td> <td>链表</td> <td>桶直接置 null</td> <td>O(1)</td> </tr> <tr> <td>链表头节点</td> <td>链表</td> <td>桶指向 next</td> <td>O(1)</td> </tr> <tr> <td>链表中间/尾部</td> <td>链表</td> <td>前驱节点.next = 当前.next</td> <td>O(n)</td> </tr> <tr> <td>红黑树节点</td> <td>红黑树</td> <td>删除 + 旋转/变色</td> <td>O(log n)</td> </tr> </tbody> </table> <p><strong>一句话总结</strong> ： <code>remove()</code> 先通过 hash 定位桶，然后根据节点类型（链表或红黑树）执行不同的删除逻辑，删除后可能触发退树化（节点数 ≤ 6）。</p> <H2>深度解析</H2> <H3>一、remove 方法整体流程</H3>   <p>上图展示了 <code>remove()</code> 方法的完整执行流程。整体分为 7 个关键步骤：</p> <ul> <li><strong>步骤一 - 计算 hash</strong> ：与 <code>put()</code> 和 <code>get()</code> 一样，先计算 key 的扰动哈希值</li> <li><strong>步骤二 - 定位桶</strong> ：通过 <code>(n - 1) &amp; hash</code> 定位目标桶</li> <li><strong>步骤三 - 空桶检查</strong> ：如果桶为空，说明 key 不存在，直接返回 null</li> <li><strong>步骤四 - 遍历查找</strong> ：遍历链表或红黑树，通过 hash 和 key 找到目标节点</li> <li><strong>步骤五 - 执行删除</strong> ：根据节点类型执行不同的删除逻辑</li> <li><strong>步骤六 - 检查退树化</strong> ：如果是红黑树，删除后检查是否需要退化为链表</li> <li><strong>步骤七 - 返回旧值</strong> ：返回被删除节点的 value，如果没找到返回 null</li> </ul> <H3>二、链表节点删除</H3>   <p>上图展示了链表删除的三种情况。核心操作：</p> <ul> <li><strong>删除头节点</strong> ：直接让桶指向第二个节点，最简单</li> <li><strong>删除中间节点</strong> ：前驱节点的 <code>next</code> 指向当前节点的 <code>next</code> ，跳过当前节点</li> <li><strong>删除尾节点</strong> ：前驱节点的 <code>next</code> 置为 <code>null</code></li> </ul> <p><strong>链表删除核心代码</strong> ：</p> <pre><code class="language-java" data-lang="java">// 链表删除核心逻辑
if (node == p) {
    // 删除的是头节点，桶直接指向下一个
    tab[index] = node.next;
} else {
    // 删除的是中间或尾节点，前驱跳过当前节点
    p.next = node.next;
}
// 记录被删除节点的 value，用于返回
e = node;</code></pre> <H3>三、红黑树节点删除</H3> <p>红黑树删除比链表复杂得多，需要考虑树的平衡性：</p>   <p>上图展示了红黑树删除的复杂性。关键点：</p> <ul> <li> <p><strong>为什么要修复平衡？</strong> 红黑树要求从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点。删除黑色节点会破坏这个性质。</p> </li> <li> <p><strong>旋转和变色</strong> ：通过左旋、右旋、颜色调整来恢复平衡，可能需要多次操作。</p> </li> <li> <p><strong>退树化检查</strong> ：删除后如果红黑树节点数 ≤ 6，会调用 <code>untreeify()</code> 转回链表。</p> </li> </ul> <p><strong>红黑树删除核心代码</strong> ：</p> <pre><code class="language-java" data-lang="java">// 红黑树删除核心逻辑
if (node instanceof TreeNode) {
    // 调用 TreeNode.removeTreeNode() 方法
    // 内部处理：删除节点 + 旋转/变色修复 + 检查退树化
    ((TreeNode&lt;K,V&gt;)node).removeTreeNode(this, tab, false);
}</code></pre> <H3>四、remove 源码核心片段</H3> <pre><code class="language-java" data-lang="java">// HashMap.remove(Object key) 入口方法
public V remove(Object key) {
    Node&lt;K,V&gt; e;
    return (e = removeNode(hash(key), key, null, false, true)) == null ?
        null : e.value;
}

// 核心删除方法
final Node&lt;K,V&gt; removeNode(int hash, Object key, Object value,
                           boolean matchValue, boolean movable) {
    Node&lt;K,V&gt;[] tab; Node&lt;K,V&gt; p; int n, index;

    // 1. 定位桶
    if ((tab = table) != null &amp;&amp; (n = tab.length) &gt; 0 &amp;&amp;
        (p = tab[index = (n - 1) &amp; hash]) != null) {

        Node&lt;K,V&gt; node = null, e; K k; V v;

        // 2. 查找目标节点
        if (p.hash == hash &amp;&amp;
            ((k = p.key) == key || (key != null &amp;&amp; key.equals(k))))
            node = p;  // 头节点就是目标
        else if ((e = p.next) != null) {
            if (p instanceof TreeNode)
                // 红黑树查找
                node = ((TreeNode&lt;K,V&gt;)p).getTreeNode(hash, key);
            else {
                // 链表遍历查找
                do {
                    if (e.hash == hash &amp;&amp;
                        ((k = e.key) == key ||
                         (key != null &amp;&amp; key.equals(k)))) {
                        node = e;  // 找到了
                        break;
                    }
                    p = e;  // p 记录前驱节点
                } while ((e = e.next) != null);
            }
        }

        // 3. 执行删除
        if (node != null &amp;&amp; (!matchValue || (v = node.value) == value ||
                             (value != null &amp;&amp; value.equals(v)))) {
            if (node instanceof TreeNode)
                // 红黑树删除
                ((TreeNode&lt;K,V&gt;)node).removeTreeNode(this, tab, movable);
            else if (node == p)
                // 删除头节点
                tab[index] = node.next;
            else
                // 删除中间或尾节点
                p.next = node.next;

            ++modCount;  // 修改次数 +1
            --size;      // 元素个数 -1
            afterNodeRemoval(node);  // 回调方法（LinkedHashMap 用）
            return node;  // 返回被删除的节点
        }
    }
    return null;  // 没找到，返回 null
}</code></pre> <H3>五、删除后的退树化</H3>   <p>上图解释了退树化的设计思想。核心理解：</p> <ul> <li><strong>滞后设计</strong> ：树化和退树化阈值差 2，是为了避免在边界值附近频繁转换</li> <li><strong>性能优化</strong> ：转换本身有开销，滞后设计减少了转换次数</li> <li><strong>工程智慧</strong> ：这种 "缓冲区" 思想在很多地方都有应用</li> </ul> <H3>六、remove vs clear</H3> <table> <thead> <tr> <th>方法</th> <th>功能</th> <th>时间复杂度</th> <th>实现</th> </tr> </thead> <tbody> <tr> <td><code>remove(key)</code></td> <td>删除指定 key</td> <td>O(1) ~ O(n)</td> <td>定位 + 遍历 + 删除</td> </tr> <tr> <td><code>clear()</code></td> <td>清空所有元素</td> <td>O(n)</td> <td>遍历数组，每个桶置 null</td> </tr> </tbody> </table> <pre><code class="language-java" data-lang="java">// clear() 方法实现
public void clear() {
    Node&lt;K,V&gt;[] tab;
    modCount++;
    if ((tab = table) != null &amp;&amp; size &gt; 0) {
        size = 0;
        for (int i = 0; i &lt; tab.length; ++i)
            tab[i] = null;  // 每个桶置 null，让 GC 回收
    }
}</code></pre> <H2>面试高频追问</H2> <ol> <li> <p><strong>删除节点后，HashMap 的容量会减小吗？</strong></p> <ul> <li>不会！ <code>remove()</code> 只删除元素，不会触发缩容</li> <li>HashMap 没有缩容机制，容量只会增长</li> </ul> </li> <li> <p><strong>为什么红黑树删除比链表复杂？</strong></p> <ul> <li>链表只需修改指针，O(1)</li> <li>红黑树删除可能破坏平衡，需要旋转和变色修复，O(log n)</li> </ul> </li> <li> <p><strong>remove 和 get 的查找逻辑一样吗？</strong></p> <ul> <li>是的！都是先比 hash，再比 key（ <code>==</code> 或 <code>equals()</code> ）</li> <li>这也是为什么重写 <code>equals()</code> 必须重写 <code>hashCode()</code> 的原因</li> </ul> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"HashMap 删除元素的时间复杂度是多少？"</li> <li>"HashMap 为什么没有缩容机制？"</li> <li>"删除红黑树节点后为什么要检查退树化？"</li> </ul> <H2>记忆口诀</H2> <p><strong>删除流程</strong> ：定位桶、遍历找、改指针（链表）/ 旋转变色（红黑树）、检查退树化。</p> <p><strong>退树化</strong> ：节点少于 7 就退树，阈值差 2 防抖动。</p> <H2>总结</H2> <p>HashMap 的 <code>remove()</code> 方法通过 hash 定位桶后，根据节点类型执行不同删除逻辑： <strong>链表删除只需修改指针</strong> （O(1)）， <strong>红黑树删除需要旋转和变色修复平衡</strong> （O(log n)）。删除后如果红黑树节点数 ≤ 6，会退化为链表。注意： <strong>HashMap 只有扩容没有缩容</strong> ，删除元素不会减小容量。</p> </div></main>