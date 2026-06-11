---
title: MySQL 深度分页如何优化
date: 2026-06-09 09:00:00 +0800
order: 301
categories: [数据库, MySQL]
tags: [MySQL, 面试, 小哈学Java]
---
一则或许对你有用的小广告

欢迎 [**加入小哈的星球**](https://www.quanxiaoha.com/column/) ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书

* **《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》** 已完结，基于 `Spring AI + Spring Boot 3.x + JDK 21...`， [**查看介绍**](https://www.quanxiaoha.com/column/10508.html)
* **《从零手撸：仿小红书（微服务架构）》** 已完结，基于 `Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...`， [**查看介绍**](https://www.quanxiaoha.com/column/10247.html) ；演示链接： [**http://116.62.199.48:7070/**](http://116.62.199.48:7070/)
* **《从零手撸：前后端分离博客项目（全栈开发）》** 2 期已完结，演示链接： [**http://116.62.199.48/**](http://116.62.199.48/)
* 新开坑项目： **《从零手撸：秒杀系统高并发优化实战》** 正在更新中...， [**查看介绍**](https://www.quanxiaoha.com/column/10659.html)

截止目前， [星球](https://www.quanxiaoha.com/column/) 内专栏 **累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习** ，欢迎 [**点击围观**](https://www.quanxiaoha.com/column/)

## 面试考察点

1. **问题识别能力** ：面试官不仅仅是想知道优化方案，更是想看你能否识别出深度分页的性能瓶颈——为什么 `LIMIT 1000000, 10` 会慢？MySQL 到底在做什么？
2. **原理理解深度** ：考察你是否理解 MySQL 的 `LIMIT offset, size` 执行机制——它需要扫描 offset + size 条记录再丢弃前面的，而不是"直接跳到第 offset 条"。
3. **方案选型思维** ：深度分页有多种优化方案，考察你能否根据业务场景（是否允许用户跳页、是否有连续自增主键等）选择最合适的方案。

## 核心答案

**深度分页问题** ：当使用 `LIMIT offset, size` 且 `offset` 值很大时，MySQL 需要扫描 `offset + size` 条记录后丢弃前面的 `offset` 条，性能急剧下降。

**优化方案对比** ：

| 方案 | 核心思路 | 适用场景 | 性能提升 |
| --- | --- | --- | --- |
| 子查询优化 | 先查主键 ID，再回表查数据 | 有自增主键索引 | ⭐⭐⭐⭐ |
| INNER JOIN | 同上，写法不同 | 有自增主键索引 | ⭐⭐⭐⭐ |
| 游标分页 | 记录上次最大 ID，下次从该 ID 开始 | 连续翻页、不支持跳页 | ⭐⭐⭐⭐⭐ |
| BETWEEN 范围查询 | 用 ID 范围替代 LIMIT offset | ID 连续、无断层 | ⭐⭐⭐⭐⭐ |
| 业务限制 | 限制最大页数，禁止深度跳页 | 搜索引擎类场景 | ⭐⭐⭐ |

**一句话总结** ：深度分页的本质是 `offset` 导致的全表扫描，优化核心是 **"利用索引直接定位起始点，避免扫描后丢弃"** 。

## 深度解析

### 一、问题本质：为什么深度分页会慢？

先看一个典型的深度分页 SQL：

```
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;
```

**很多人的误解** ：MySQL 会"直接跳到第 100 万条记录"，然后取 10 条。

**实际情况** ：MySQL 的执行流程是：

上图展示了 `LIMIT 1000000, 10` 的执行过程。关键问题在于：

* **扫描量大** ：MySQL 需要扫描 `1000000 + 10 = 1000010` 条记录，而不是只扫描 10 条
* **丢弃浪费** ：前 100 万条记录全部被扫描后丢弃，做了无用功
* **回表开销** ：如果查询的是 `SELECT *` ，每条记录都要回表获取完整数据，代价更大
* **时间复杂度** ：O(offset + size)，offset 越大，性能越差

这就是为什么 `LIMIT 100, 10` 很快，但 `LIMIT 1000000, 10` 会慢几个数量级。

### 二、方案一：子查询优化

**核心思想** ：先通过子查询利用覆盖索引快速定位起始 ID，再回表查数据，避免大量无意义的回表操作。

```
-- 原始慢查询（假设执行时间：5 秒）
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;

-- 优化后（假设执行时间：0.1 秒）
SELECT * FROM orders o
INNER JOIN (
    SELECT id FROM orders ORDER BY id LIMIT 1000000, 10
) t ON o.id = t.id;
```

**为什么更快？**

上图展示了子查询优化的核心原理。关键优化点在于：

* **覆盖索引** ：子查询只查 `id` 字段，可以直接在索引上完成，无需回表
* **减少回表** ：子查询阶段扫描 100 万条时不需要回表，只有最终的 10 条才回表
* **性能对比** ：原始查询回表 100 万次，优化后只回表 10 次

### 三、方案二：游标分页（Cursor-based Pagination）—— 性能最优

**核心思想** ：记录上一页最后一条记录的 ID，下次查询时直接从该 ID 之后开始，完全避开 `offset` 。

```
-- 第一页
SELECT * FROM orders ORDER BY id LIMIT 10;

-- 假设第一页最后一条记录的 id = 10
-- 第二页（传统方式：LIMIT 10, 10）
-- 第二页（游标方式：记住上一页最后的 id）
SELECT * FROM orders WHERE id > 10 ORDER BY id LIMIT 10;

-- 第 N 页：假设上一页最后的 id = 1000000
SELECT * FROM orders WHERE id > 1000000 ORDER BY id LIMIT 10;
```

上图对比了传统分页和游标分页的性能差异。关键优势在于：

* **稳定性能** ：无论翻到第几页，每次都只扫描 `size` 条记录，性能恒定
* **索引定位** ： `WHERE id > last_id` 可以直接利用主键索引定位到起始位置
* **无丢弃浪费** ：不存在"扫描后丢弃"的问题

**游标分页的局限性** ：

* **不支持跳页** ：用户只能"上一页/下一页"，不能直接跳到第 N 页
* **需要连续 ID** ：如果 ID 不连续或有删除，可能导致某些记录被跳过或重复
* **前端需要记住游标** ：需要保存上一页最后的 ID 值

### 四、方案三：BETWEEN 范围查询

如果 ID 连续且业务允许，可以用 ID 范围替代 `LIMIT offset` ：

```
-- 假设每页 10 条，要查第 100001 页
-- 起始 ID = (100001 - 1) * 10 + 1 = 1000001
-- 结束 ID = 1000001 + 9 = 1000010

SELECT * FROM orders
WHERE id BETWEEN 1000001 AND 1000010;
```

**适用条件** ：

* ID 必须连续（没有断层）
* 需要知道 ID 的分布规律

### 五、方案四：业务层面限制 —— 最实用的方案

很多大厂的做法： **直接限制用户只能翻到前 N 页** 。

**实现方式** ：

```
// 后端校验
public PageResult<Order> listOrders(int pageNum, int pageSize) {
    // 限制最大页数
    int maxPage = 100;
    if (pageNum > maxPage) {
        throw new BusinessException("最多只能查看前 " + maxPage + " 页");
    }
    // 正常查询
    return orderMapper.selectPage(pageNum, pageSize);
}
```

### 六、实际性能对比（100 万条数据测试）

| 查询方式 | SQL | 执行时间 |
| --- | --- | --- |
| 原始查询 | `SELECT * FROM orders LIMIT 1000000, 10` | ~5s |
| 子查询优化 | `SELECT * FROM orders o INNER JOIN (SELECT id FROM orders LIMIT 1000000, 10) t ON o.id = t.id` | ~0.1s |
| 游标分页 | `SELECT * FROM orders WHERE id > 1000000 LIMIT 10` | ~0.01s |

## 面试高频追问

1. **追问一** ：游标分页有什么缺点？什么场景不适合用？

   * 答：不支持跳页、需要前端保存游标状态、ID 不连续时可能漏数据。电商搜索结果页适合，但后台管理系统需要跳页就不适合。
2. **追问二** ：如果排序字段不是主键 ID，而是 `create_time` ，怎么优化？

   * 答：可以用联合索引 `(create_time, id)` ，子查询改为 `SELECT id FROM orders ORDER BY create_time, id LIMIT offset, size` ，游标分页改为 `WHERE (create_time, id) > (last_time, last_id)` 。
3. **追问三** ：为什么子查询只查 `id` 就能提升性能？

   * 答：因为只查主键/索引列时，MySQL 可以使用"覆盖索引"，直接在索引树上获取数据，不需要回表去聚簇索引查完整记录。

## 常见面试变体

* "为什么 `LIMIT 1000000, 10` 会很慢？"
* "MySQL 分页查询怎么优化？"
* "百万级数据分页怎么处理？"
* "介绍几种分页优化方案及其适用场景"

## 记忆口诀

**深度分页优化三句话** ：

1. **子查询先查 id** ：覆盖索引省回表
2. **游标记住 last\_id** ：直接定位无扫描
3. **业务限制最大页** ：性价比高最实用

## 总结

深度分页的性能问题本质是 `offset` 导致的大量无效扫描。优化核心是 **"用索引直接定位，避免扫描后丢弃"** ：生产环境推荐 **子查询 + JOIN** （兼容跳页）或 **游标分页** （性能最优），同时配合 **业务层限制最大页数** ，这是最经济实用的方案。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/MySQL面试-最左前缀匹配原则/'><span class='context-label'>上一篇</span><span class='context-title'>什么是最左前缀匹配？为什么要遵守</span></a>
<a class='context-link next' href='/software-fundamentals/posts/MySQL面试-索引慢查询原因/'><span class='context-label'>下一篇</span><span class='context-title'>用了索引还是很慢，可能是什么原因？</span></a>
</div>
