---
title: 什么是 SPI，和 API 有啥区别
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
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

1. **设计模式理解** ：面试官不仅仅是想知道 "SPI 是服务发现机制" 这种定义，更是想考察你是否理解 SPI 背后的设计思想——开闭原则、解耦、可扩展性，以及它与工厂模式、策略模式的关系。
2. **框架扩展能力** ：考察你是否清楚 SPI 在主流框架（Spring、Dubbo、JDBC、SLF4J）中的应用，能否利用 SPI 机制实现框架的灵活扩展。
3. **实践踩坑经验** ：看你是否在实际项目中使用过 SPI，是否了解 SPI 的类加载机制、配置规范、性能问题，以及如何避免 ServiceLoader 的陷阱。

## 核心答案

SPI（Service Provider Interface）是 Java 提供的一种 **服务发现机制** ，允许程序在运行时动态加载接口的实现类，实现接口与实现的解耦。

| 对比维度 | API | SPI |
| --- | --- | --- |
| **全称** | Application Programming Interface | Service Provider Interface |
| **定位** | 面向开发者提供的接口 | 面向扩展者提供的扩展点 |
| **调用方向** | 开发者调用框架 | 框架调用开发者 |
| **控制权** | 框架定义，开发者调用 | 框架定义接口，开发者实现 |
| **核心目的** | 提供功能 | 提供扩展能力 |
| **典型示例** | `List.add()` 、 `Thread.start()` | JDBC Driver、SLF4J、Spring Boot Starter |
| **发现方式** | 直接调用 | 配置文件 + `ServiceLoader` 动态加载 |

**一句话概括** ： **API 是 "我调你"，SPI 是 "你实现，我调你"** ——API 是框架暴露给开发者的接口，SPI 是框架留给开发者的扩展点。

## 深度解析

### 一、SPI 的本质理解

SPI 的核心思想是 **"接口定义在调用方，实现在扩展方"** ，实现模块间的解耦。

上图展示了 SPI 的工作原理，关键点：

* **接口定义在框架中** ：框架定义好接口（SPI），但不提供具体实现
* **实现在第三方/开发者** ：开发者或第三方库实现接口
* **框架通过 ServiceLoader 发现实现** ：运行时动态加载，无需修改框架代码
* **符合开闭原则** ：对扩展开放，对修改关闭

### 二、Java SPI 的使用方式

Java SPI 的使用分为 **3 个步骤** ：

上图展示了 Java SPI 的完整使用流程，下面是详细的代码示例：

```
// ========== Step 1：定义接口（框架方）==========
package com.example.spi;

public interface HelloService {
    String sayHello(String name);
}

// ========== Step 2：提供实现（扩展方）==========
// 实现一：中文问候
package com.example.spi.impl;

public class ChineseHelloService implements HelloService {
    @Override
    public String sayHello(String name) {
        return "你好，" + name;
    }
}

// 实现二：英文问候
package com.example.spi.impl;

public class EnglishHelloService implements HelloService {
    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }
}

// ========== Step 3：配置 SPI 文件 ==========
// 文件路径：resources/META-INF/services/com.example.spi.HelloService
// 文件内容（每行一个实现类全限定名）：
// com.example.spi.impl.ChineseHelloService
// com.example.spi.impl.EnglishHelloService

// ========== Step 4：使用 ServiceLoader 加载（调用方）==========
package com.example.spi;

import java.util.ServiceLoader;

public class SpiDemo {
    public static void main(String[] args) {
        // 加载所有 HelloService 的实现
        ServiceLoader<HelloService> loader = ServiceLoader.load(HelloService.class);

        // 遍历并调用
        for (HelloService service : loader) {
            System.out.println(service.sayHello("张三"));
        }
        // 输出：
        // 你好，张三
        // Hello, 张三
    }
}
```

### 三、SPI 的经典应用场景

SPI 在 Java 生态中有大量应用，是框架设计的核心机制：

| 框架/场景 | SPI 接口 | 作用 |
| --- | --- | --- |
| **JDBC** | `java.sql.Driver` | 不同数据库厂商实现自己的驱动 |
| **SLF4J** | `ILoggerFactory` | 不同日志框架（Logback、Log4j）实现 |
| **Spring** | `BeanPostProcessor` | 开发者扩展 Bean 生命周期 |
| **Dubbo** | 各种 `@SPI` 接口 | 协议、序列化、负载均衡扩展 |
| **Spring Boot** | `EnableAutoConfiguration` | 自动配置、Starter 扩展 |

**JDBC 的 SPI 示例** ：

```
// JDK 只定义接口，不提供实现
// java.sql.Driver 是 SPI 接口

// MySQL 驱动实现（在 mysql-connector-java.jar 中）
package com.mysql.cj.jdbc;

public class Driver implements java.sql.Driver {
    static {
        try {
            DriverManager.registerDriver(new Driver());
        } catch (SQLException e) {
            throw new RuntimeException("Can't register driver!");
        }
    }
}

// 配置文件：META-INF/services/java.sql.Driver
// 内容：com.mysql.cj.jdbc.Driver

// 使用时，只需引入 MySQL 驱动 JAR，无需修改代码
Connection conn = DriverManager.getConnection(url, user, password);
```

### 四、API vs SPI 深度对比

上图从控制流角度对比了 API 和 SPI 的本质区别：

* **API** ：开发者主动调用，控制权在开发者手中。框架提供功能，开发者使用功能。
* **SPI** ：框架主动调用，控制权在框架手中。框架定义规范，开发者提供实现。

**对比总结表** ：

| 对比维度 | API | SPI |
| --- | --- | --- |
| **调用方向** | 开发者 → 框架 | 框架 → 开发者 |
| **谁定义接口** | 框架 | 框架 |
| **谁实现接口** | 框架 | 开发者/第三方 |
| **谁调用** | 开发者 | 框架（通过 ServiceLoader） |
| **耦合程度** | 编译时确定 | 运行时动态发现 |
| **扩展方式** | 继承/组合 | 实现接口 + 配置文件 |
| **设计原则** | 封装、抽象 | 开闭原则、解耦 |

### 五、SPI 的注意事项和陷阱

```
// ========== 陷阱 1：ServiceLoader 不是线程安全的 ==========
// 每次调用 ServiceLoader.load() 都会创建新实例
// 解决方案：缓存加载结果

private static volatile List<HelloService> cachedServices;

public static List<HelloService> getServices() {
    if (cachedServices == null) {
        synchronized (SpiDemo.class) {
            if (cachedServices == null) {
                ServiceLoader<HelloService> loader = ServiceLoader.load(HelloService.class);
                cachedServices = new ArrayList<>();
                for (HelloService service : loader) {
                    cachedServices.add(service);
                }
            }
        }
    }
    return cachedServices;
}

// ========== 陷阱 2：ServiceLoader 会延迟加载 ==========
// 只有遍历时才会真正实例化实现类
// 如果实现类初始化耗时，第一次遍历会慢

// ========== 陷阱 3：无法获取单个实现 ==========
// ServiceLoader 返回所有实现，需要自己筛选
ServiceLoader<HelloService> loader = ServiceLoader.load(HelloService.class);
HelloService first = loader.iterator().next();  // 获取第一个

// ========== 陷阱 4：实现类必须有无参构造函数 ==========
// 否则 ServiceLoader 无法实例化
```

## 面试高频追问

1. **Dubbo 的 SPI 和 Java 的 SPI 有什么区别？** Dubbo 自己实现了 SPI 机制，支持按名称获取实现（ `@SPI("dubbo")` ）、依赖注入、AOP 增强、自动包装等，比 Java 原生 SPI 更强大。
2. **Spring 的 `@Autowired` 和 SPI 有什么关系？** 两者都是依赖注入的实现方式。SPI 是 Java 标准的服务发现机制，Spring 的依赖注入是 Spring 容器管理的。Spring Boot 的自动配置用到了 SPI（ `spring.factories` ）。
3. **SPI 配置文件为什么要放在 `META-INF/services/` 目录下？** 这是 `ServiceLoader` 的约定，它会在类路径下查找这个目录。这是一种约定优于配置的设计。
4. **如何实现一个类似 SPI 的机制？** 可以使用自定义注解 + 反射扫描，或者使用 Spring 的 `@Import` + `ImportSelector` ，或者使用 `ClassPathScanningCandidateComponentProvider` 扫描。

## 常见面试变体

* "SPI 和 API 有什么区别？"
* "Java 的 `ServiceLoader` 是怎么实现的？"
* "Dubbo 的 SPI 扩展机制是怎么设计的？"
* "Spring Boot 的自动配置是怎么实现的？"

## 记忆口诀

**SPI 三要素** ：接口定义好，实现配置好，ServiceLoader 来找

**API vs SPI** ：API 我调你，SPI 你实现我调你

**核心优势** ：解耦扩展两不误，开闭原则好帮手

## 总结

SPI 是 Java 提供的服务发现机制，核心思想是 **"接口在调用方，实现在扩展方"** ，通过 `META-INF/services/` 配置文件和 `ServiceLoader` 实现运行时动态加载。与 API 相比，SPI 实现了控制反转，框架定义接口规范，开发者提供实现，框架在运行时发现并调用。SPI 广泛应用于 JDBC、SLF4J、Dubbo、Spring Boot 等框架，是实现可扩展架构的核心机制。
