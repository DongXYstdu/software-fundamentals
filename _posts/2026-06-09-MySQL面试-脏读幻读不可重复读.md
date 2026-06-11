---
title: 脏读、幻读、不可重复读是什么？
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

1. **基础掌握度** ：面试官不仅仅是想知道三个概念的定义，更是想知道你是否理解它们产生的根本原因 —— 并发事务之间的数据干扰，以及它们之间的本质区别。
2. **隔离级别理解** ：考察你是否清楚 MySQL 的四种事务隔离级别，以及每种隔离级别能解决哪些并发问题。
3. **实践应用能力** ：能否根据业务场景选择合适的隔离级别，是否了解 MVCC（多版本并发控制）如何解决这些问题。

## 核心答案

脏读、不可重复读、幻读是 **数据库并发事务** 中三种典型的数据不一致问题：

| 问题 | 定义 | 关注点 | 严重程度 |
| --- | --- | --- | --- |
| **脏读** | 读到其他事务 **未提交** 的数据 | 数据被回滚 | ⭐⭐⭐ 最严重 |
| **不可重复读** | 同一事务内，两次读取 **同一行** 数据结果不同 | 数据被修改/删除 | ⭐⭐ 中等 |
| **幻读** | 同一事务内，两次查询 **结果行数** 不同 | 数据被新增 | ⭐ 较轻 |

**一句话总结** ：脏读是读了未提交的数据；不可重复读是同一条数据变了；幻读是结果集行数变了。

## 深度解析

### 一、三种问题详解

上图展示了脏读的发生过程：

* **时间点 T3** ：事务 B 将 `id=1` 的 `age` 从 20 改为 25，但尚未提交
* **时间点 T4** ：事务 A 读取该行数据，得到 `age=25`
* **时间点 T5** ：事务 B 回滚了，数据恢复为 20
* **问题** ：事务 A 读到的 `age=25` 是 "脏数据"，因为事务 B 根本没提交

**脏读危害** ：基于未提交数据做业务判断，可能导致严重的逻辑错误。

上图展示了不可重复读的发生过程：

* **时间点 T2** ：事务 A 第一次读取， `age=20`
* **时间点 T4~T5** ：事务 B 修改了这条数据并提交
* **时间点 T6** ：事务 A 再次读取同一行， `age=25`
* **问题** ：同一事务内，两次读取同一数据，结果不一致

**与脏读的区别** ：不可重复读读到的是 **已提交** 的数据，不是脏数据。

上图展示了幻读的发生过程：

* **时间点 T2** ：事务 A 查询 `age > 20` 的记录，返回 2 条
* **时间点 T4~T5** ：事务 B 新增了一条 `age=30` 的记录并提交
* **时间点 T6** ：事务 A 再次用相同条件查询，返回 3 条
* **问题** ：同一事务内，两次相同查询，结果行数不同，仿佛出现了 "幻影"

**与不可重复读的区别** ：

* 不可重复读强调 **同一条数据被修改** （UPDATE/DELETE）
* 幻读强调 **结果集行数变化** （INSERT/DELETE）

### 二、四种隔离级别

**隔离级别详解** ：

1. **READ UNCOMMITTED（读未提交）**

   * 最低隔离级别
   * 可能发生脏读、不可重复读、幻读
   * 几乎不使用
2. **READ COMMITTED（读已提交，RC）**

   * 只能读取已提交的数据
   * 解决了脏读，但可能发生不可重复读、幻读
   * Oracle、SQL Server 默认级别
3. **REPEATABLE READ（可重复读，RR）**

   * **MySQL InnoDB 默认隔离级别**
   * 保证同一事务内多次读取同一数据结果一致
   * 解决了脏读、不可重复读
   * InnoDB 通过 **MVCC + Next-Key Lock** 也解决了幻读
4. **SERIALIZABLE（串行化）**

   * 最高隔离级别
   * 强制事务串行执行
   * 解决所有问题，但性能最差

### 三、MySQL 如何解决这些问题

**MVCC 解决不可重复读** ：

```
-- RR 级别下，MVCC 保证可重复读
-- 事务 A
BEGIN;
SELECT * FROM users WHERE id = 1;  -- age=20，生成 Read View

-- 此时事务 B 修改并提交
-- UPDATE users SET age=25 WHERE id=1; COMMIT;

SELECT * FROM users WHERE id = 1;  -- 仍然读到 age=20
-- 因为 MVCC 根据事务 A 的 Read View，只能看到历史版本
COMMIT;
```

**Next-Key Lock 解决幻读** ：

```
-- RR 级别下，当前读使用 Next-Key Lock
-- 事务 A
BEGIN;
SELECT * FROM users WHERE age > 20 FOR UPDATE;
-- 锁定 age > 20 的所有行，以及 (20, +∞) 的间隙

-- 此时事务 B 尝试插入
-- INSERT INTO users(age) VALUES(30);  -- 被阻塞！

COMMIT;  -- 事务 A 提交后，事务 B 才能插入
```

### 四、对比总结

## 面试高频追问

1. **MySQL 默认隔离级别是什么？如何解决幻读？**

   * 默认是 `REPEATABLE READ` （可重复读）
   * 通过 **MVCC** 解决快照读的幻读
   * 通过 **Next-Key Lock** （行锁 + 间隙锁）解决当前读的幻读
2. **RC 和 RR 的区别？**

   * `RC` ：每次 `SELECT` 生成新的 `Read View` ，能看到其他事务已提交的修改
   * `RR` ：第一次 `SELECT` 生成 `Read View` ，后续复用，保证可重复读
3. **什么是 MVCC？**

   * 多版本并发控制，每行数据保存版本链（通过 `undo log` ）
   * 读操作根据 `Read View` 判断哪个版本对自己可见
   * 实现 "读不阻塞写，写不阻塞读"
4. **什么时候用 SERIALIZABLE？**

   * 需要严格数据一致性的场景（如金融交易）
   * 一般不推荐使用，性能太差

## 常见面试变体

* "MySQL 有哪些事务隔离级别？"
* "RR 级别能完全解决幻读吗？"
* "MVCC 是怎么实现的？"
* "什么是 Next-Key Lock？"

## 记忆口诀

**脏读未提交，数据不可信；** **不可重复读，同条数据变；** **幻读多或少，结果行数变。** **RC 解脏读，RR 解后俩，串行全解决。**

## 总结

脏读是读到未提交的数据（最严重）；不可重复读是同一事务内同一行数据变了（UPDATE/DELETE）；幻读是同一事务内查询结果行数变了（INSERT/DELETE）。MySQL 默认使用 `REPEATABLE READ` 隔离级别，通过 **MVCC** 解决不可重复读，通过 **MVCC + Next-Key Lock** 解决幻读。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/MySQL面试-索引设计原则/'><span class='context-label'>上一篇</span><span class='context-title'>设计索引时应遵循哪些原则</span></a>
<a class='context-link next' href='/software-fundamentals/posts/MySQL面试-自增主键用完了怎么办/'><span class='context-label'>下一篇</span><span class='context-title'>自增主键用完了怎么办？</span></a>
</div>
