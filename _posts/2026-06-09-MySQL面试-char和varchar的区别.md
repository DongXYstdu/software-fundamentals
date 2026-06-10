---
title: char �?varchar 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [数据�? MySQL]
tags: [MySQL, 面试, 小哈学Java]
---

## 面试考察�?

1. **基础掌握�?*：面试官不仅仅是想知道两个类型的字面区别，更是想知道你是否理�?MySQL 的存储机制，能否在实际表设计中做出正确选择�?

2. **性能意识**：考察你是否清楚定长和变长类型在存储效率、查询性能、索引构建等方面的差异，以及在不同场景下的取舍�?

3. **实践经验**：能否结合实际业务场景（如用户名、手机号、MD5 值等）给出合理的选择建议，而不是只会背概念�?

## 核心答案

`CHAR` �?`VARCHAR` �?MySQL 中两种最常用的字符串类型，核心区别如下：

| 对比维度 | `CHAR` | `VARCHAR` |
|---|---|---|
| **存储方式** | 定长存储，不足补空格 | 变长存储，按实际长度 |
| **长度范围** | 0 ~ 255 字符 | 0 ~ 65,535 字节 |
| **空间占用** | 固定占用声明长度 | 实际长度 + 1~2 字节前缀 |
| **尾部空格** | 存储时补齐，检索时移除 | 原样存储和检�?|
| **性能特点** | 更快�?CRUD（无长度计算�?| 更省空间（按需分配�?|
| **适用场景** | 长度固定的数据（手机号、MD5�?| 长度变化的数据（用户名、地址�?|

**一句话总结**：`CHAR` 是定长、空间换时间；`VARCHAR` 是变长、时间换空间�?

## 深度解析

### 一、存储机制对�?

![](https://aka.doubaocdn.com/s/yHGZ1wZNoc)

上图展示�?`CHAR` �?`VARCHAR` 的存储差异，核心要点如下�?

- **CHAR 定长机制**：无论实际存储多少字符，都占用声明长度的空间。比�?`CHAR(10)` 存储 `'abc'` 时，会自动补 7 个空格，占用 10 字节。检索时，尾部的空格会被**自动移除**（这是一个容易踩坑的点）�?

- **VARCHAR 变长机制**：只占用实际需要的空间，额外使�?1~2 字节存储长度信息。当长度 �?255 字节时用 1 字节，超�?255 字节时用 2 字节�?

- **空间计算示例**�?
    - `CHAR(10)` 存储 `'abc'` �?占用 10 字节
    - `VARCHAR(10)` 存储 `'abc'` �?占用 4 字节�? 长度 + 3 数据�?
    - `VARCHAR(1000)` 存储 `'abc'` �?占用 5 字节�? 长度 + 3 数据�?

### 二、尾部空格处理差异（高频考点�?

```sql
-- CHAR 尾部空格会被移除
CREATE TABLE test_char (
    name CHAR(10)
);
INSERT INTO test_char VALUES ('Tom   ');  -- 存入 'Tom' + 7 空格
SELECT name, LENGTH(name) FROM test_char;
-- 结果�?Tom', 3 （检索时空格被移除了！）

-- VARCHAR 尾部空格保留
CREATE TABLE test_varchar (
    name VARCHAR(10)
);
INSERT INTO test_varchar VALUES ('Tom   ');  -- 存入 'Tom' + 7 空格
SELECT name, LENGTH(name) FROM test_varchar;
-- 结果�?Tom   ', 10 （原样保留）
```

**关键差异**�?

- `CHAR`：存储时补空格，检索时**自动移除**尾部空格
- `VARCHAR`：原样存储，原样检�?

### 三、InnoDB 行溢出与页存�?

�?InnoDB 存储引擎中，`VARCHAR` 的最大长度受多个因素限制�?

![](https://aka.doubaocdn.com/s/uzxz1wZNoc)

**关键�?*�?

- `VARCHAR(N)` 中的 N �?*字符�?*，不是字节数
- �?`utf8mb4` 字符集下，`VARCHAR(255)` 最多占�?`255 × 4 + 2 = 1022` 字节
- 当数据过大时，InnoDB 会使�?行溢�?机制，将数据存储到溢出页

### 四、性能对比

| 操作类型 | `CHAR` 表现 | `VARCHAR` 表现 |
|---|---|---|
| **INSERT** | 稍快（无需计算长度�?| 稍慢（需计算实际长度�?|
| **UPDATE** | 更快（长度不变，无碎片） | 可能产生碎片（长度变化） |
| **SELECT** | 更快（固定位置计算） | 稍慢（需解析长度前缀�?|
| **索引构建** | 更快（长度固定） | 稍慢（需遍历计算�?|
| **存储空间** | 浪费（固定长度） | 节省（按需分配�?|

**性能结论**�?

- `CHAR` 在频繁更新场景下更有优势（不会产生碎片）
- `VARCHAR` 在存储空间上更有优势（尤其数据长度差异大时）
- 实际应用中，这个性能差异通常可以忽略�?*空间利用率往往是更重要的考量**

### 五、最佳实�?

```sql
-- �?推荐使用 CHAR 的场景（长度固定�?
-- 手机号（11 位）
phone CHAR(11) NOT NULL COMMENT '手机�?
-- 身份证号�?8 位）
id_card CHAR(18) NOT NULL COMMENT '身份证号'
-- MD5 值（32 位）
md5_value CHAR(32) NOT NULL COMMENT 'MD5 哈希�?
-- 状态码、枚举�?
status CHAR(1) DEFAULT '0' COMMENT '状态：0-禁用�?-启用'
-- UUID 去掉横线�?2 位）
uuid CHAR(32) NOT NULL COMMENT 'UUID'

-- �?推荐使用 VARCHAR 的场景（长度变化�?
-- 用户名（4-20 字符�?
username VARCHAR(50) NOT NULL COMMENT '用户�?
-- 邮箱（长度不定）
email VARCHAR(100) NOT NULL COMMENT '邮箱地址'
-- 文章标题
title VARCHAR(200) NOT NULL COMMENT '文章标题'
-- 详细地址
address VARCHAR(500) COMMENT '详细地址'
-- 商品描述
description VARCHAR(2000) COMMENT '商品描述'
```

### 六、常见误�?

```sql
-- �?误区一：认�?CHAR(10) 只能�?10 个英文字�?
-- 实际上：CHAR(10) 可以�?10 个字符，不管是英文还是中�?
CHAR(10)  -- 可以�?'1234567890' �?'一二三四五六七八九�?

-- �?误区二：认为 VARCHAR 查询性能远低�?CHAR
-- 实际上：现代 MySQL �?VARCHAR 优化很好，性能差异很小

-- �?误区三：混淆字符数和字节�?
-- VARCHAR(255) �?utf8mb4 下最多占�?1022 字节，不�?255 字节

-- �?误区四：忽略 CHAR 尾部空格会被移除的特�?
INSERT INTO t (name) VALUES ('Tom   ');  -- CHAR 会丢失空格！
```

## 面试高频追问

1. **VARCHAR(10) �?VARCHAR(1000) 存储 'abc' 有区别吗�?*
    - 存储空间：磁盘上没区别（都占�?4 字节�?
    - 内存占用：排序、临时表等场景下，VARCHAR(1000) 会按声明长度预分配内存，更占内存
    - 建议：在满足业务需求的前提下，尽量使用较小的长度声�?

2. **为什�?CHAR 最多只�?255 字符�?*
    - `CHAR` 的长度用 1 字节存储，最大值就�?255
    - `VARCHAR` �?1~2 字节存储长度，所以能支持更大的�?

3. **索引中使�?CHAR 还是 VARCHAR 更好�?*
    - 对于固定长度的字段（如手机号），`CHAR` 更好（索引更紧凑�?
    - 对于变长字段，必须用 `VARCHAR`
    - 无论哪种，都建议加上前缀索引以减少索引大�?

4. **TEXT 类型什么时候用�?*
    - 超过 255 字符的定长数据：不存在，改用 `VARCHAR` �?`TEXT`
    - 超过 65,535 字节的大文本：使�?`TEXT` 系列（TINYTEXT、TEXT、MEDIUMTEXT、LONGTEXT�?

## 常见面试变体

- "数据库中定长字段和变长字段有什么区别？"
- "设计用户表时，手机号和用户名分别用什么类型？为什么？"
- "VARCHAR(255) �?utf8mb4 字符集下最多能存多少个汉字�?
- "CHAR �?VARCHAR 在索引构建上有什么差异？"

## 记忆口诀

**CHAR 定长补空格，检索之时去空格；VARCHAR 变长按需存，长度前缀记心间。手机身份证�?CHAR，用户邮箱用 VARCHAR�?*

## 总结

`CHAR` 是定长类型，存储时补空格、检索时去空格，适合长度固定的数据（手机号、MD5 值）；`VARCHAR` 是变长类型，按实际长度存储，额外使用 1~2 字节记录长度，适合长度变化的数据（用户名、地址）。选择原则�?*固定长度�?CHAR，变化长度用 VARCHAR**，性能差异通常可以忽略，优先考虑空间利用率和业务语义�?

---
> 参考来源：[MySQL char �?varchar 的区别是什么？](https://www.quanxiaoha.com/java-interview/what-is-the-difference-between-char-and-varchar-in-mysql)
