---
title: 设计索引时应遵循哪些原则
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

1. **实战经验** ：面试官不仅仅想知道你会不会写 `CREATE INDEX` ，更想考察你是否具备在生产环境中设计合理索引的能力，能否平衡查询性能与写入成本。
2. **原理理解** ：是否理解 B+ 树结构、最左前缀原则、索引下推等底层原理，而非只会死记硬背几条规则。
3. **权衡意识** ：索引不是越多越好，考察你是否懂得在查询性能、存储空间、写入性能之间做取舍。

## 核心答案

设计索引应遵循以下 **7 大核心原则** ：

| 原则 | 核心要点 | 关键词 |
| --- | --- | --- |
| 选择合适的列 | WHERE、JOIN、ORDER BY、GROUP BY 列优先 | 高频查询列 |
| 区分度高优先 | 选择性 = 唯一值/总行数，越高越好 | 基数大、离散度高 |
| 最左前缀原则 | 联合索引按顺序匹配，从左到右连续使用 | 范围查询断后 |
| 覆盖索引 | 索引包含查询所需全部字段，避免回表 | `SELECT` 列也在索引中 |
| 控制索引数量 | 单表索引不超过 5 个，单个索引字段不超过 5 个 | 写入成本、空间占用 |
| 前缀索引 | 长字符串只索引前 N 个字符，节省空间 | 牺牲部分选择性 |
| 索引下推 | MySQL 5.6+ 特性，在索引层过滤减少回表 | `Using index condition` |

**一句话总结** ：索引设计要 "选对列、区分度高、遵循最左前缀、善用覆盖索引、控制数量"。

## 深度解析

### 一、选择合适的列建立索引

上图总结了适合与不适合建立索引的列。具体说明如下：

**✅ 适合建索引的场景** ：

* **WHERE 条件列** ：查询条件中频繁出现的列，能大幅减少扫描行数。
* **JOIN 关联列** ：外键关联列，能加速多表关联查询。
* **ORDER BY / GROUP BY 列** ：排序和分组操作非常消耗性能，索引可以利用 B+ 树的有序性直接获取结果。
* **高基数列** ：唯一值越多，索引的过滤效果越好。

**❌ 不适合建索引的场景** ：

* **区分度低的列** ：如性别（只有 "男/女"）、状态（只有 "启用/禁用"），索引过滤效果差，优化器可能直接选择全表扫描。
* **频繁更新的列** ：每次更新都会导致索引重建，增加写入成本。
* **小表** ：数据量小于 1000 行时，全表扫描可能比走索引更快。

### 二、区分度（选择性）原则

**区分度 = 唯一值数量 / 总行数** ，值越接近 1 越好。

```
-- 查看列的区分度
SELECT
    COUNT(DISTINCT user_id) / COUNT(*) AS user_id_selectivity,
    COUNT(DISTINCT status) / COUNT(*) AS status_selectivity
FROM orders;

-- 结果示例：
-- user_id_selectivity: 0.85  ✅ 区分度高，适合建索引
-- status_selectivity: 0.01   ❌ 区分度低，不适合单独建索引
```

**联合索引的列顺序** ：区分度高的列放前面。

```
-- 假设 status 只有 3 个值，user_id 有 10 万个值
-- ❌ 错误：区分度低的列在前
CREATE INDEX idx_wrong ON orders(status, user_id);

-- ✅ 正确：区分度高的列在前
CREATE INDEX idx_right ON orders(user_id, status);
```

### 三、最左前缀原则

联合索引按照定义顺序构建 B+ 树，查询时必须从最左列开始连续匹配。

上图展示了最左前缀原则的应用场景。关键点说明：

* **从左到右连续匹配** ：必须从索引的第一列开始，中间不能跳过任何一列。
* **范围查询会"断后"** ：一旦出现范围查询（ `>` 、 `<` 、 `BETWEEN` 、 `LIKE` 前缀模糊），该列之后的索引列无法被使用。
* **优化建议** ：把范围查询列放在联合索引的最后。

```
-- 场景：经常查询某用户的已支付订单
-- ✅ 推荐：等值条件在前，范围条件在后
CREATE INDEX idx_user_status_time ON orders(user_id, status, create_time);

-- 查询能完整利用索引
SELECT * FROM orders
WHERE user_id = 100 AND status = 'PAID' AND create_time > '2024-01-01';
```

### 四、覆盖索引

如果索引包含了查询所需的所有字段，MySQL 可以直接从索引中获取数据， **无需回表** 查询聚簇索引。

```
-- 假设有索引：INDEX(user_id, status)

-- ❌ 需要回表：SELECT 中有索引不包含的字段
SELECT user_id, status, amount FROM orders WHERE user_id = 100;

-- ✅ 覆盖索引：SELECT 字段都在索引中
SELECT user_id, status FROM orders WHERE user_id = 100;

-- ✅ 更好的方案：创建包含 amount 的联合索引
CREATE INDEX idx_covering ON orders(user_id, status, amount);
```

**EXPLAIN 中显示 `Using index` 表示使用了覆盖索引** 。

### 五、控制索引数量

索引不是越多越好，每个索引都有成本：

上图分析了索引带来的各项成本。具体说明：

* **空间成本** ：每个索引都是一棵独立的 B+ 树，会占用额外的磁盘空间。联合索引字段越多，空间占用越大。
* **时间成本（写入时）** ：

  + `INSERT` 操作需要同时更新所有索引
  + `UPDATE` 操作如果修改了索引列，需要先删除旧的索引项，再插入新的索引项
  + `DELETE` 操作需要从所有索引中删除对应的数据
* **优化器成本** ：索引越多，MySQL 优化器在生成执行计划时需要考虑的选项越多，可能导致选择时间变长，甚至选错索引。

**经验法则** ：

* 单表索引数量： **不超过 5 个**
* 单个索引字段数： **不超过 5 个**
* 定期审查：删除 unused 索引

```
-- 查看索引使用情况（MySQL 5.7+）
SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'your_database';
```

### 六、前缀索引

对于 `VARCHAR` 、 `TEXT` 等长字符串列，可以使用前缀索引只索引前 N 个字符，节省空间。

```
-- 创建前缀索引，只索引 email 前 10 个字符
CREATE INDEX idx_email_prefix ON users(email(10));

-- 查询时正常使用
SELECT * FROM users WHERE email = 'test@example.com';
```

**权衡** ：

* ✅ 节省索引空间
* ❌ 可能降低区分度（前 N 个字符相同的情况）
* ❌ 无法用于覆盖索引（必须回表验证完整值）

**如何确定前缀长度** ：

```
-- 计算不同前缀长度的区分度
SELECT
    COUNT(DISTINCT LEFT(email, 5)) / COUNT(*) AS prefix_5,
    COUNT(DISTINCT LEFT(email, 10)) / COUNT(*) AS prefix_10,
    COUNT(DISTINCT LEFT(email, 15)) / COUNT(*) AS prefix_15,
    COUNT(DISTINCT email) / COUNT(*) AS full_column
FROM users;

-- 选择区分度接近完整列的最短前缀
```

### 七、索引下推（Index Condition Pushdown，ICP）

MySQL 5.6+ 引入的优化特性，将部分 WHERE 条件的过滤下推到存储引擎层，减少回表次数。

```
-- 假设有索引：INDEX(name, age)

-- 无 ICP：存储引擎返回所有 name 匹配的记录，Server 层再过滤 age
-- 有 ICP：存储引擎直接过滤 name AND age，只返回符合条件的记录
SELECT * FROM users WHERE name LIKE '张%' AND age = 25;
```

**EXPLAIN 中显示 `Using index condition` 表示使用了索引下推** 。

## 面试高频追问

1. **联合索引的列顺序如何确定？**

   * 区分度高的列放前面、等值条件列放前面、范围查询列放后面、考虑排序分组需求。
2. **什么情况下索引会失效？**

   * 对索引列使用函数或计算、隐式类型转换、 `LIKE` 以 `%` 开头、 `OR` 条件中有列无索引、联合索引不满足最左前缀、否定条件（`!=` 、 `NOT IN` ）等。
3. **主键为什么建议使用自增 ID？**

   * 自增 ID 保证新数据顺序插入 B+ 树末尾，避免页分裂，减少碎片，提高写入性能和空间利用率。

## 常见面试变体

* "联合索引 (a, b, c)，WHERE b = 1 AND c = 2 能走索引吗？"
* "什么情况下应该使用前缀索引？"
* "索引越多越好吗？为什么？"
* "覆盖索引是什么？有什么优势？"

## 记忆口诀

**索引设计七原则** ：选对列、区分高、最左前、覆盖好、控数量、前缀省、下推快

**联合索引顺序** ：区分度高放前头，等值条件优先走，范围查询放最后

## 总结

索引设计需要在查询性能和写入成本之间做权衡。核心原则是：选择高频查询且区分度高的列建立索引；联合索引遵循最左前缀原则，区分度高的列放前面；善用覆盖索引避免回表；控制索引数量避免过度索引；长字符串可使用前缀索引节省空间。记住，索引不是越多越好，要根据实际业务场景和查询模式进行设计。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/MySQL面试-索引慢查询原因/'><span class='context-label'>上一篇</span><span class='context-title'>用了索引还是很慢，可能是什么原因？</span></a>
<a class='context-link next' href='/software-fundamentals/posts/MySQL面试-脏读幻读不可重复读/'><span class='context-label'>下一篇</span><span class='context-title'>脏读、幻读、不可重复读是什么？</span></a>
</div>
