---
title: 为什么不能用 BigDecimal equals 方法做等值比较？
date: 2026-06-09 09:00:00 +0800
order: 2
categories: [Java, Java基础]
tags: [Java, 基础, 面试, 小哈学Java]
---
一则或许对你有用的小广告

欢迎 [**加入小哈的星球**](https://www.quanxiaoha.com/column/) ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书

* **《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》** 已完结，基于 `Spring AI + Spring Boot 3.x + JDK 21...`， [**查看介绍**](https://www.quanxiaoha.com/column/10508.html)
* **《从零手撸：仿小红书（微服务架构）》** 已完结，基于 `Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...`， [**查看介绍**](https://www.quanxiaoha.com/column/10247.html) ；演示链接： [**http://116.62.199.48:7070/**](http://116.62.199.48:7070/)
* **《从零手撸：前后端分离博客项目（全栈开发）》** 2 期已完结，演示链接： [**http://116.62.199.48/**](http://116.62.199.48/)
* 新开坑项目： **《从零手撸：秒杀系统高并发优化实战》** 正在更新中...， [**查看介绍**](https://www.quanxiaoha.com/column/10659.html)

截止目前， [星球](https://www.quanxiaoha.com/column/) 内专栏 **累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习** ，欢迎 [**点击围观**](https://www.quanxiaoha.com/column/)

## 面试考察点

1. **API 理解深度** ：面试官不仅仅是想知道 "不能用"，更是想考察你是否读过 `BigDecimal` 的源码，理解 `equals()` 和 `compareTo()` 的实现差异。
2. **精度意识** ： `BigDecimal` 的核心特性是精度可控，这个问题考察你是否理解 `scale` （标度）的概念及其对比较的影响。
3. **实战经验** ：金额比较是金融场景的高频操作，用错方法会导致严重的业务 bug，这反映你的工程经验。

## 核心答案

**`BigDecimal` 的 `equals()` 方法不仅比较数值，还比较精度，导致 `1.0` 和 `1.00` 被判定为不相等。比较 `BigDecimal` 的数值应该使用 `compareTo()` 方法。**

| 比较方法 | 比较内容 | `1.0` vs `1.00` 结果 | 推荐场景 |
| --- | --- | --- | --- |
| `equals()` | 数值 + 精度 | `false` （不相等） | ❌ 不推荐用于数值比较 |
| `compareTo()` | 仅数值 | `0` （相等） | ✅ **数值比较首选** |
| `compareTo() == 0` | 仅数值 | `true` （相等） | ✅ 推荐写法 |

**一句话总结** ： `equals()` 看精度， `compareTo()` 看数值，金额比较用 `compareTo()` 。

## 深度解析

### 一、翻车现场：equals 的 "坑"

```
import java.math.BigDecimal;

public class BigDecimalEqualsDemo {
    public static void main(String[] args) {
        BigDecimal a = new BigDecimal("1.0");
        BigDecimal b = new BigDecimal("1.00");

        // ❌ 用 equals 比较：返回 false！
        System.out.println(a.equals(b));  // 输出: false

        // ✅ 用 compareTo 比较：返回 0，表示相等
        System.out.println(a.compareTo(b));  // 输出: 0
        System.out.println(a.compareTo(b) == 0);  // 输出: true

        // 查看精度差异
        System.out.println("a.scale = " + a.scale());  // 输出: 1
        System.out.println("b.scale = " + b.scale());  // 输出: 2
    }
}
```

看到了吗？ `1.0` 和 `1.00` 在数学上明明相等，但 `equals()` 返回 `false` ！这在金额比较场景中是致命的 bug。

### 二、为什么会这样？scale 的概念

上图展示了 `BigDecimal` 的内部结构和 `equals()` 的比较逻辑。关键要点：

* **`scale` （标度）** ：小数点后的位数， `1.0` 的 scale 是 1， `1.00` 的 scale 是 2
* **`equals()` 严格比较** ：不仅要数值相等， `scale` 也必须相等
* **`compareTo()` 宽松比较** ：只比较数学值，忽略 `scale` 差异

### 三、源码分析

```
// BigDecimal.equals() 源码（简化版）
public boolean equals(Object x) {
    if (!(x instanceof BigDecimal))
        return false;
    BigDecimal xDec = (BigDecimal) x;

    // ⚠️ 关键：scale 必须相等
    if (scale != xDec.scale)
        return false;

    // 再比较数值
    return (this.inflated() == xDec.inflated());
}

// BigDecimal.compareTo() 源码（简化版）
public int compareTo(BigDecimal val) {
    // ✅ 只比较数值大小，不考虑 scale
    // 通过数学运算统一 scale 后再比较
    if (this.scale == val.scale) {
        // scale 相同，直接比较整数部分
        return compare(this.intVal, val.intVal);
    }
    // scale 不同，调整后比较
    // ... 省略调整逻辑
}
```

### 四、实际场景对比

```
import java.math.BigDecimal;

public class BigDecimalCompareDemo {
    public static void main(String[] args) {
        // 场景一：金额比较（数据库查询结果）
        BigDecimal priceFromDb = new BigDecimal("99.00");  // 数据库返回
        BigDecimal userPrice = new BigDecimal("99.0");     // 用户输入

        // ❌ 错误：equals 比较
        if (priceFromDb.equals(userPrice)) {
            System.out.println("价格相等");  // 不会执行！
        }

        // ✅ 正确：compareTo 比较
        if (priceFromDb.compareTo(userPrice) == 0) {
            System.out.println("价格相等");  // 会执行
        }

        // 场景二：金额比较的完整写法
        BigDecimal amount1 = new BigDecimal("100.50");
        BigDecimal amount2 = new BigDecimal("100.500");

        // ✅ 推荐写法
        boolean isEqual = amount1.compareTo(amount2) == 0;
        boolean isGreater = amount1.compareTo(amount2) > 0;
        boolean isLess = amount1.compareTo(amount2) < 0;

        System.out.println("相等: " + isEqual);      // true
        System.out.println("大于: " + isGreater);    // false
        System.out.println("小于: " + isLess);       // false
    }
}
```

### 五、最佳实践总结

| 场景 | 推荐方法 | 示例 |
| --- | --- | --- |
| 判断相等 | `compareTo() == 0` | `a.compareTo(b) == 0` |
| 判断大于 | `compareTo() > 0` | `a.compareTo(b) > 0` |
| 判断小于 | `compareTo() < 0` | `a.compareTo(b) < 0` |
| 判断大于等于 | `compareTo() >= 0` | `a.compareTo(b) >= 0` |
| 判断小于等于 | `compareTo() <= 0` | `a.compareTo(b) <= 0` |
| 排序/TreeSet | `compareTo()` | 自动使用 |

## 面试高频追问

1. **`BigDecimal` 有哪些构造方式？推荐哪种？**

   | 构造方式 | 示例 | 精度问题 | 推荐 |
   | --- | --- | --- | --- |
   | 字符串构造 | `new BigDecimal("0.1")` | ✅ 精确 | ⭐ **推荐** |
   | double 构造 | `new BigDecimal(0.1)` | ❌ 精度丢失 | ❌ 禁止 |
   | valueOf | `BigDecimal.valueOf(0.1)` | ✅ 精确 | ⭐ 推荐 |
2. **`TreeSet` 中放 `BigDecimal` 会有问题吗？**

   不会有问题。 `TreeSet` 使用 `compareTo()` 排序， `1.0` 和 `1.00` 会被视为相同元素（只能存一个）。但如果用 `HashSet` ，由于 `equals()` 不同，两个都会存进去。
3. **如何统一 `BigDecimal` 的精度？**

   ```
   BigDecimal a = new BigDecimal("1.0");
   BigDecimal normalized = a.setScale(2, RoundingMode.HALF_UP);  // 变成 1.00
   ```

## 常见面试变体

* 变体一：" `BigDecimal` 的 `compareTo()` 和 `equals()` 有什么区别？"
* 变体二："为什么 `new BigDecimal(0.1)` 得到的不是精确的 0.1？"
* 变体三：" `BigDecimal` 如何比较大小？"

## 记忆口诀

**equals 比精度，1.0 不等 1.00；** **compareTo 比数值，金额比较它靠谱；** **构造用字符串，double 构造坑死人。**

## 总结

`BigDecimal` 的 `equals()` 方法会比较 `scale` （精度），导致 `1.0` 和 `1.00` 被判定为不相等。 **金额比较必须使用 `compareTo() == 0`** ，只比较数值大小，忽略精度差异。同时，构造 `BigDecimal` 时应使用字符串或 `valueOf()` ，避免 `double` 构造导致的精度丢失。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/Java基础-BigDecimal和Long哪个表示金额更合适/'><span class='context-label'>上一篇</span><span class='context-title'>BigDecimal Long 哪个表示金额更合适？</span></a>
<a class='context-link next' href='/software-fundamentals/posts/Java基础-String-StringBuilder-StringBuffer区别/'><span class='context-label'>下一篇</span><span class='context-title'>"String、StringBuilder StringBuffer 的区别？"</span></a>
</div>
