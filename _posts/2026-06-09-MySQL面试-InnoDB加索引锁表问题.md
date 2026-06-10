---
title: InnoDB 加索引，这个时候会锁表�?
date: 2026-06-09 09:00:00 +0800
categories: [数据�? MySQL]
tags: [MySQL, 面试, 小哈学Java]
---

## 面试考察�?

1. **DDL 机制理解**：面试官不仅仅是想知道一�?"�? �?"�? 的答案，更是想知道你是否理解 MySQL �?DDL（数据定义语言）执行机制，以及 Online DDL 的原理�?

2. **版本差异意识**：考察你是否清�?MySQL 5.5�?.6�?.0 �?DDL 操作上的重大差异，能否根据版本给出准确回答�?

3. **生产实践能力**：是否知道在线上加索引的正确姿势，如何避免影响业务，以及遇到紧急情况如何处理�?

## 核心答案

**分情况回�?*�?

| MySQL 版本 | 加索引行�?| 是否锁表 |
|---|---|---|
| **MySQL 5.5 及以�?* | `COPY` 方式 | �?**锁表**，全表禁止读�?|
| **MySQL 5.6+** | `Online DDL`（默认） | �?**不锁�?*，支持并发读�?|
| **MySQL 8.0+** | `Instant DDL`（部分支持） | �?**秒级完成**，几乎无影响 |

**一句话总结**：MySQL 5.6 之后默认使用 Online DDL，加索引**不会阻塞读写**，但在准备和提交阶段会有短暂的元数据锁（MDL），生产环境建议使用 `ALGORITHM=INPLACE, LOCK=NONE` 明确指定�?

## 深度解析

### 一、DDL 的三种算�?

![](https://aka.doubaocdn.com/s/VMDC1wZNoz)

- **COPY 算法**：最原始的方式。需要创建一个临时表，然后把原表数据全部拷贝过去，最后删除原表并重命名。这个过程会**全程锁表**，大表可能需要几个小时，生产环境绝对要避免�?

- **INPLACE 算法**：MySQL 5.6 引入�?Online DDL。直接在原表上操作，不需要拷贝数据到临时表。在构建索引期间�?*允许并发读写**，只在开始和结束阶段需要短暂的 MDL 锁。加索引默认使用这个算法�?

- **INSTANT 算法**：MySQL 8.0 引入。只修改表的元数据（存储�?`.frm` 文件或数据字典中），不涉及数据文件，**秒级完成**。但目前只支持部�?DDL（如添加列到表末尾、修改列默认值等），**加索引不支持 INSTANT**�?

### 二、Online DDL 的执行过�?

![](https://aka.doubaocdn.com/s/V1gh1wZNoz)

- **阶段一（初始化�?*：需要获�?MDL 锁来修改表结构定义。这里有一�?"降级" 过程：先获取排他锁评估成本，然后**快速降级为共享�?*。这个阶段极短，通常毫秒级�?

- **阶段二（执行�?*：这是最耗时的阶段，可能持续几分钟到几小时。但关键是：**允许并发 DML**！InnoDB 会把执行期间的增量修改记录到 Online Log 中�?

- **阶段三（提交�?*：需要重新获�?MDL 排他锁，�?Online Log 中的增量数据应用到新索引上，然后更新元数据。这个阶段也很短�?

**潜在风险**：如果阶段三执行时，有一个长查询持有 MDL 读锁，DDL �?*卡在等待 MDL �?*上，而后续的请求也会被阻塞，形成 "锁等待链"，导致业务抖动�?

### 三、不同索引类型的加锁情况

| 索引类型 | 算法 | 是否锁表 | 备注 |
|---|---|---|---|
| 普通二级索�?| `INPLACE` | �?不锁�?| 默认支持 Online DDL |
| 主键索引（新增） | `INPLACE` | �?不锁�?| 需要重建表，但允许并发 |
| 主键索引（删除） | `INPLACE` | �?不锁�?| 同上 |
| 全文索引 | `INPLACE` | �?不锁�?| 首次创建可能较慢 |
| 空间索引 | `INPLACE` | �?不锁�?| MySQL 5.7+ |

### 四、生产环境最佳实�?

```sql
-- �?推荐写法：明确指�?Online DDL 参数
ALTER TABLE user ADD INDEX idx_create_time (create_time),
ALGORITHM=INPLACE, LOCK=NONE;

-- 参数说明�?
-- ALGORITHM=INPLACE：使用在�?DDL，不拷贝数据
-- LOCK=NONE：不允许任何锁，支持并发读写
-- 如果不支�?INPLACE，会报错而不是降级到 COPY
```

**生产环境操作建议**�?

1. **避开业务高峰�?*：虽�?Online DDL 不锁表，但会消�?CPU �?I/O 资源

2. **使用 pt-online-schema-change 工具**（Percona Toolkit）：
   - 适用于超大表或对稳定性要求极高的场景
   - 原理：创建影子表 �?分批拷贝数据 �?触发器同步增�?�?原子切换

3. **监控 MDL 锁等�?*�?
   - 执行前检查是否有长事�?
   - 使用 performance_schema.metadata_locks 监控

4. **设置超时时间**�?
   - `LOCK_WAIT_TIMEOUT`：避免长时间等待 MDL �?
   - `MAX_EXECUTION_TIME`：限�?DDL 最大执行时�?

**检查是否有长事�?*�?

```sql
-- 查看当前运行的事�?
SELECT * FROM information_schema.INNODB_TRX;

-- 查看 MDL 锁等待（MySQL 8.0+�?
SELECT * FROM performance_schema.metadata_locks
WHERE LOCK_STATUS = 'PENDING';
```

## 面试高频追问

1. **Online DDL 期间，如果写入量很大会有什么影响？**

   Online Log 会持续增长，可能导致�?
   - **内存压力**：Online Log 默认在内存中，太大可能触发刷�?
   - **阶段三时间延�?*：增量数据越多，应用时间越长
   - **建议**：在写入低谷期执行，或使�?`pt-osc` 工具

2. **为什么有时候加索引还是会卡住？**

   通常是因�?**MDL 锁等�?*�?
   - 有长查询持有 MDL 读锁
   - DDL 等待 MDL 写锁
   - 后续请求排队等待 DDL 释放
   - **解决方案**：`NOWAIT` �?`WAIT n` 语法，或�?kill 长查�?

3. **`ALGORITHM=INPLACE` �?`LOCK=NONE` 有什么区别？**

   - `ALGORITHM=INPLACE`：指�?DDL 执行算法，不拷贝整表数据
   - `LOCK=NONE`：指定加锁级别，`NONE` 表示不允许加任何�?
   - 两者配合使用，确保 DDL 完全在线执行

4. **8.0 �?Instant DDL 能用于加索引吗？**

   **不能**。Instant DDL 目前支持的场景有限：
   - �?添加列到表末�?
   - �?删除�?
   - �?修改列默认�?
   - �?添加/删除索引（仍需�?INPLACE�?

## 常见面试变体

- "MySQL 大表加索引有哪些方案�?
- "Online DDL 的原理是什么？会不会影响业务？"
- "生产环境如何安全地给千万级大表加索引�?
- "DDL 操作导致数据库抖动，可能是什么原因？"

## 记忆口诀

**版本差异**�?.5 锁表 5.6 在线�?.0 部分秒级�?

**算法演进**：Copy 拷贝锁全表，Inplace 原地不阻塞，Instant 秒改元数�?

**生产操作**：避开高峰看长事务，INPLACE + NONE 双保�?

## 总结

MySQL 5.6 之后，InnoDB 加索引默认使�?Online DDL（`INPLACE` 算法），**不会锁表**，支持并发读写。但在执行的开始和结束阶段需要获�?MDL 锁，如果有长事务可能导致阻塞。生产环境建议明确指�?`ALGORITHM=INPLACE, LOCK=NONE`，并在业务低峰期执行，超大表可考虑使用 `pt-online-schema-change` 工具�?

---
> 参考来源：[InnoDB 加索引，这个时候会锁表�?](https://www.quanxiaoha.com/java-interview/innodb-add-index-lock-table-explained)
