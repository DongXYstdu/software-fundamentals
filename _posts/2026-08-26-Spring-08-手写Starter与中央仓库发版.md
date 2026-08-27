---
title: 手写 Spring Boot Starter 并发布到中央仓库
date: 2026-08-26 09:00:00 +0800
categories: [Java, Spring]
tags: [SpringBoot, Starter, Maven, 发版]
---

# 手写 Spring Boot Starter 与 Maven 中央仓库发版
## 1. 发版全景图

![08-01 发版流程全景]({{ site.baseurl }}/assets/svg/08-01-发版流程全景.svg)

### 1.1 生态里的五个角色

| 角色 | 是什么 | 打交道点 |
|---|---|---|
| Maven 中央仓库 | repo1.maven.org/maven2，全球公共仓库 | 发版最终目的地 |
| Sonatype Central Portal | portal.sonatype.com，唯一发布入口（替代已停用的 OSSRH） | 注册、验证命名空间、审核发布 |
| 命名空间 Namespace | 被允许使用的 groupId | 发版前必须验证所有权 |
| GPG | 非对称签名，证明包是你发的、未被篡改 | 生成密钥、上传公钥、配置签名 |
| 镜像（aliyun 等） | 中央仓库的同步副本 | 项目 settings.xml 配的就是它 |

### 1.2 发布流转

```
本地 Starter 工程
    │  mvn deploy
    │  ① central-publishing-maven-plugin 打包
    │  ② GPG 对每个构件签名（.jar/.pom → .asc）
    ▼
Central Portal 校验队列（Staging）
    │  自动校验：元信息·license·sources·javadoc·签名·命名空间
    │  校验失败 → 打回；通过 →
    ▼
Release（手动点按钮 / 配置自动发布）
    │  发布后不可撤回（只能升版本）
    ▼
中央仓库 repo1.maven.org ──同步──► aliyun 等镜像 ──► 全世界项目引入
```

**关键点：发布不可撤回**。版本号一旦 Release 就永久存在，发错了只能发新版本覆盖使用、旧版仍在。

### 1.3 Portal 校验清单（硬性自动化检查）

1. POM 元信息完整：`name`、`description`、`url`、`licenses`、`developers`、`scm` 缺一不可
2. 附带 `-sources.jar`（源码包）
3. 附带 `-javadoc.jar`（文档包，可为空壳但必须存在）
4. 所有构件带 GPG 签名（`.asc` 文件）
5. groupId 属于已验证命名空间，且不能发 `SNAPSHOT`

### 1.4 命名空间怎么选

| 方式 | groupId 示例 | 验证方式 | 适合 |
|---|---|---|---|
| 自有域名 | `com.yourcompany` | DNS 加 TXT 记录 | 公司/有域名者 |
| GitHub 账号 | `io.github.<用户名>` | Portal 跳转 GitHub 授权 | 个人开发者（推荐） |

groupId 只要求是"已验证命名空间"，不要求与 Java 包名一致（但惯例保持一致）。

### 1.5 两个过时警告（老教程的坑）

- OSSRH（oss.sonatype.org）已于 2025-06-30 彻底停用，`nexus-staging-maven-plugin` 作废，现在统一用 `central-publishing-maven-plugin`
- `spring.factories` 注册自动装配在 Boot 2.7+ 已改为 `AutoConfiguration.imports`，Boot 3.x 只认新文件

### 1.6 对应生产场景

- yudao 的所有依赖最终都来自中央仓库（经 aliyun 镜像加速）
- Starter 发到中央仓库后，任何项目加三行坐标就能用，不用再 `mvn install` 手动塞本地仓库
- 私服（Nexus）vs 中央仓库：公司内部组件发私服即可；发中央仓库的意义是公开可复用 + 走业界标准流程

## 2. 环境准备

![08-02 环境准备五步]({{ site.baseurl }}/assets/svg/08-02-环境准备五步.svg)

发版前必备齐四样：**Portal 账号+Token、已验证命名空间、GPG 密钥、settings.xml 凭证**。

### 2.1 注册 Central Portal 并生成 User Token

1. 打开 `https://central.sonatype.com`，右上角 Sign in，推荐用 GitHub 账号登录
2. 头像 → View Account → **Generate User Token**，生成一对随机 username/password

> 这对 Token 才是 `mvn deploy` 的凭证，**不是网站登录密码**。生成后立即保存。

### 2.2 验证命名空间（GitHub 路线）

1. 左侧菜单 Namespaces → Register Namespace
2. 输入 `io.github.<GitHub用户名>`（全小写）
3. 按页面要求在该 GitHub 账号下创建指定名称的公开仓库（形如 `OSSRH-xxxxx`）
4. 回 Portal 点 Verify，状态变 **VERIFIED** 即通过

### 2.3 安装 GPG 并生成密钥对（Windows）

1. 下载安装 Gpg4win（https://www.gpg4win.org），自带 gpg 命令行 + Kleopatra
2. 验证：`gpg --version`
3. 生成密钥：`gpg --full-gen-key`，交互选项：

| 提示 | 选择 | 说明 |
|---|---|---|
| Key type | 1（RSA and RSA） | 默认 |
| Key size | 3072（或 4096） | 3072 够用 |
| Expiration | 0 | 永不过期 |
| Real name / Email | 与 GitHub 一致 | 写进密钥供核对身份 |
| Passphrase | 自定义口令 | 签名时用，务必记住 |

4. 取 Key ID：`gpg --list-keys --keyid-format=long`，输出 `pub rsa3072/3AA5C34371567BD2` 中 `/` 后的即 Key ID

### 2.4 上传公钥到 keyserver

```powershell
gpg --keyserver keyserver.ubuntu.com --send-keys <KeyID>
```

别人下载 jar 后校验工具要去 keyserver 拉公钥验签；公钥不上传，签名再对也过不了。
备选：`keys.openpgp.org`（需邮箱验证）；`pgp.mit.edu` 已不稳定，别用。

### 2.5 配置 settings.xml（`C:\Users\hw\.m2\settings.xml`）

```xml
<servers>
  <!-- Central Portal 发布凭证：id 必须是 central，与插件 serverId 对应 -->
  <server>
    <id>central</id>
    <username>第2.1步的Token用户名</username>
    <password>第2.1步的Token密码</password>
  </server>
  <!-- GPG 签名口令：maven-gpg-plugin 约定读 gpg.passphrase -->
  <server>
    <id>gpg.passphrase</id>
    <passphrase>第2.3步设置的口令</passphrase>
  </server>
</servers>
```

要点：
- `<id>central</id>` 必须与 `central-publishing-maven-plugin` 的 serverId 一致（默认 central），否则 401
- 填 Token，不是网站登录密码
- settings.xml 含密钥口令，绝不提交 git
- 现有 aliyun `<mirror>` 不受影响：mirror 管下载，server 管发布认证，共存不冲突

### 2.6 自检清单

| # | 检查项 | 验证方式 | 通过标志 |
|---|---|---|---|
| 1 | Token 已生成并保存 | 第 2.1 步 | 有一对随机 username/password |
| 2 | 命名空间已验证 | Portal → Namespaces | 显示 VERIFIED |
| 3 | GPG 可用 | `gpg --version` | 正常输出版本号 |
| 4 | 私钥已生成 | `gpg --list-secret-keys --keyid-format=long` | 见 `sec rsa3072/<KeyID>` |
| 5 | 公钥已上传 | keyserver 网页搜 KeyID | 能检索到公钥 |
| 6 | settings.xml 两段 server 就位 | 文件检查 | central + gpg.passphrase 都在 |

### 2.7 两个坑

- GPG 2.1+ 签名可能卡在弹窗输口令：第 4 节配插件时加 `--pinentry-mode loopback`，让它从 settings.xml 读口令
- 公钥同步有延迟：`--send-keys` 后各 keyserver 互相同步要几分钟到几小时，报"找不到公钥"稍等再试

## 3. 手写 Starter（分 5 步：3.1 骨架 → 3.2 属性绑定 → 3.3 核心组件 → 3.4 自动装配 → 3.5 注册与验证）

版本基线（2026-08 查证）：
- Spring Boot 用 **3.5.16**（3.x 最后一版，与 yudao 生态一致；自动装配机制与 4.x 相同）
- 发布插件 `org.sonatype.central:central-publishing-maven-plugin` 最新 **0.11.0**

### 3.1 工程骨架与 pom

#### 3.1.1 Starter 命名与结构规范

| 构件 | 命名 | 职责 |
|---|---|---|
| autoconfigure | `xxx-spring-boot-autoconfigure` | 自动装配代码（@AutoConfiguration、@ConditionalOnXxx） |
| starter | `xxx-spring-boot-starter` | 聚合构件：只放依赖 + 引入 autoconfigure，不含业务代码 |

- 成熟框架拆两个模块；本课单模块聚焦装配机制 + 发版
- **命名红线**：第三方不能以 `spring-boot-starter-` 开头（官方保留前缀），必须用 `xxx-spring-boot-starter`

#### 3.1.2 目录结构

```
modbus-spring-boot-starter/
├── pom.xml
└── src/main/
    ├── java/io/github/yourname/modbus/
    │   ├── ModbusProperties.java          # 3.2 配置属性绑定
    │   ├── ModbusTcpClient.java           # 3.3 核心组件
    │   └── ModbusAutoConfiguration.java   # 3.4 自动装配
    └── resources/META-INF/spring/
        └── org.springframework.boot.autoconfigure.AutoConfiguration.imports   # 3.5 注册文件
```

`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 是 Boot 2.7+ 硬约定，路径/文件名写错一个字符装配就不生效。

#### 3.1.3 pom.xml（可编译版，发版插件第 4 节再加）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 坐标：groupId 必须是你已验证的命名空间 -->
    <groupId>io.github.yourname</groupId>
    <artifactId>modbus-spring-boot-starter</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <!-- 项目身份元信息：中央仓库校验硬性要求（对应 1.3 清单第 1 条） -->
    <name>modbus-spring-boot-starter</name>
    <description>Spring Boot Starter for Modbus TCP client</description>
    <url>https://github.com/yourname/modbus-spring-boot-starter</url>
    <licenses>
        <license>
            <name>The Apache License, Version 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
        </license>
    </licenses>
    <developers>
        <developer>
            <name>Your Name</name>
            <email>you@example.com</email>
        </developer>
    </developers>
    <scm>
        <connection>scm:git:git://github.com/yourname/modbus-spring-boot-starter.git</connection>
        <developerConnection>scm:git:ssh://github.com/yourname/modbus-spring-boot-starter.git</developerConnection>
        <url>https://github.com/yourname/modbus-spring-boot-starter</url>
    </scm>

    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <spring-boot.version>3.5.16</spring-boot.version>
    </properties>

    <!-- 库构件不继承 spring-boot-starter-parent，改用 BOM 统一版本 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- 提供 @AutoConfiguration / @ConditionalOnXxx / @ConfigurationProperties -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-autoconfigure</artifactId>
        </dependency>
        <!-- 生成 spring-configuration-metadata.json，让 IDE 对 application.yml 有补全提示 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
                <configuration>
                    <release>17</release>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

#### 3.1.4 三个关键决策点

1. **为什么用 BOM 而不继承 `spring-boot-starter-parent`？**
   parent 是给"应用"用的，带入应用级默认配置（资源过滤、插件版本锁定）。库构件用 `spring-boot-dependencies` BOM 只拿版本管理、不带应用包袱，不强制下游用户的构建行为。
2. **为什么元信息现在就写？**
   name/description/url/licenses/developers/scm 是校验清单第 1 条硬性要求，缺一个 Portal 就打回。它们属于"项目身份"，建骨架时就写好；第 4 节只补"发版动作"相关的插件。
3. **为什么 `configuration-processor` 标 `optional`？**
   只在编译期生成元数据 JSON，运行时不需要，`optional=true` 保证不传递给下游、不污染依赖树。

#### 3.1.5 本步自检

| 检查项 | 通过标志 |
|---|---|
| groupId 与已验证命名空间一致 | `io.github.<GitHub用户名>` |
| 六项元信息齐全 | name/description/url/licenses/developers/scm 都有 |
| 依赖能解析 | `mvn dependency:resolve` 无报错 |
| 能编译 | `mvn compile` BUILD SUCCESS |

### 3.2 ModbusProperties 配置属性绑定

#### 3.2.1 配置契约（Starter 的对外 API，先于代码设计）

```yaml
modbus:
  enabled: true              # 总开关
  host: 192.168.1.100        # PLC/网关地址
  port: 502                  # Modbus TCP 标准端口
  unit-id: 1                 # 从站地址（单播 1~247，广播 0）
  connect-timeout: 3s        # 连接超时
  response-timeout: 5s       # 响应超时
  retry-times: 3             # 失败重试次数
```

`modbus` 是前缀，每个键绑定到 `ModbusProperties` 同名字段；松散绑定自动处理 `unit-id` → `unitId`。

#### 3.2.2 ModbusProperties 代码

```java
package io.github.yourname.modbus;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

/**
 * Modbus TCP 客户端配置属性。
 * 前缀 modbus，绑定 application.yml 中 modbus.* 的所有键。
 */
@ConfigurationProperties(prefix = "modbus")
public class ModbusProperties {

    /** 总开关，默认开启 */
    private boolean enabled = true;

    /** Modbus 服务端地址（PLC / 网关） */
    private String host = "127.0.0.1";

    /** Modbus TCP 端口，标准值 502 */
    private int port = 502;

    /** 从站地址（Unit ID），1~247 */
    private int unitId = 1;

    /** 连接超时 */
    private Duration connectTimeout = Duration.ofSeconds(3);

    /** 响应超时 */
    private Duration responseTimeout = Duration.ofSeconds(5);

    /** 失败重试次数 */
    private int retryTimes = 3;

    // getter / setter 全部生成（绑定靠 setter 注入）
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }

    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }

    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }

    public int getUnitId() { return unitId; }
    public void setUnitId(int unitId) { this.unitId = unitId; }

    public Duration getConnectTimeout() { return connectTimeout; }
    public void setConnectTimeout(Duration connectTimeout) { this.connectTimeout = connectTimeout; }

    public Duration getResponseTimeout() { return responseTimeout; }
    public void setResponseTimeout(Duration responseTimeout) { this.responseTimeout = responseTimeout; }

    public int getRetryTimes() { return retryTimes; }
    public void setRetryTimes(int retryTimes) { this.retryTimes = retryTimes; }
}
```

#### 3.2.3 三个关键机制

1. **`@ConfigurationProperties` 只做绑定，不注册 Bean**——需配合 3.4 节 `@EnableConfigurationProperties(ModbusProperties.class)` 才生效。职责分离：属性类是纯 POJO，装配类决定要不要启用。
2. **超时用 `Duration` 而非 `long` 毫秒**——Boot 属性绑定的一等公民，支持 `3s`/`500ms`/`PT3S` 写法，官方 Starter 通行做法。
3. **默认值写在字段初始化上**——用户不配置时兜底；`host` 给 `127.0.0.1` 而非 `null`，宁可连失败也不留 NPE。更严格做法是 3.4 节用 `@ConditionalOnProperty` 控制。

#### 3.2.4 松散绑定规则速查

| yml 写法 | Java 字段 | 说明 |
|---|---|---|
| `unit-id` | `unitId` | kebab-case（推荐，官方规范） |
| `unitId` | `unitId` | camelCase（可用） |
| `unit_id` | `unitId` | 下划线（环境变量场景） |
| `UNIT_ID` | `unitId` | 全大写（仅环境变量） |

#### 3.2.5 本步自检

| 检查项 | 通过标志 |
|---|---|
| 类上有 `@ConfigurationProperties(prefix = "modbus")` | 前缀与 yml 契约一致 |
| 所有字段有 getter/setter | JavaBean 规范 |
| 超时字段是 `Duration` 类型 | 支持 `3s`/`500ms` 写法 |
| `mvn compile` 通过 | BUILD SUCCESS |

### 3.3 ModbusTcpClient 核心组件

#### 3.3.1 报文结构（MBAP 头 7B + PDU）

```
MBAP 头（7B）                    PDU（请求示例：功能码 03）
┌──────────┬──────────┬────────┬─────────┬──────────┬──────────┬──────────┐
│事务标识 2B│协议标识 2B│长度 2B │单元标识1B│功能码 1B │起始地址2B│寄存器数2B│
│ 自增     │ 固定 0   │后续字节数│ unitId  │ 0x03     │ 0x0000   │ 0x000A   │
└──────────┴──────────┴────────┴─────────┴──────────┴──────────┴──────────┘
```

三个校验点：事务标识回显校验（防串包）、异常响应识别（功能码 | 0x80）、按长度字段定界读 PDU。

#### 3.3.2 ModbusTcpClient 代码

```java
package io.github.yourname.modbus;

import java.io.Closeable;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 最小 Modbus TCP 客户端。
 * 单连接、请求串行化（synchronized），实现 Closeable 交由 Spring 管理生命周期。
 */
public class ModbusTcpClient implements Closeable {

    private static final int FUNCTION_READ_HOLDING_REGISTERS = 0x03;
    private static final int EXCEPTION_FLAG = 0x80;

    private final ModbusProperties properties;
    private final AtomicInteger transactionId = new AtomicInteger(0);

    private Socket socket;
    private DataOutputStream out;
    private DataInputStream in;

    public ModbusTcpClient(ModbusProperties properties) {
        this.properties = properties;
    }

    /** 建立 TCP 连接（connectTimeout 内连不上即失败） */
    public synchronized void connect() throws IOException {
        if (socket != null && socket.isConnected()) {
            return;
        }
        Socket s = new Socket();
        s.connect(new InetSocketAddress(properties.getHost(), properties.getPort()),
                (int) properties.getConnectTimeout().toMillis());
        // 响应超时：读等待上限，超时抛 SocketTimeoutException
        s.setSoTimeout((int) properties.getResponseTimeout().toMillis());
        this.socket = s;
        this.out = new DataOutputStream(s.getOutputStream());
        this.in = new DataInputStream(s.getInputStream());
    }

    /**
     * 读保持寄存器（功能码 03）。
     * @param address  起始寄存器地址（0 基址）
     * @param quantity 寄存器数量（1~125）
     * @return 每个寄存器的无符号值（0~65535）
     */
    public synchronized int[] readHoldingRegisters(int address, int quantity) throws IOException {
        if (quantity < 1 || quantity > 125) {
            throw new IllegalArgumentException("quantity 必须在 1~125 之间");
        }
        connect(); // 惰性连接：首次调用才建连

        IOException lastError = null;
        // 重试次数来自配置（含首次共 retryTimes+1 次尝试）
        for (int attempt = 0; attempt <= properties.getRetryTimes(); attempt++) {
            try {
                return doReadHoldingRegisters(address, quantity);
            } catch (IOException e) {
                lastError = e;
                closeQuietly(); // 连接可能已脏，断开下轮重连
            }
        }
        throw lastError;
    }

    private int[] doReadHoldingRegisters(int address, int quantity) throws IOException {
        int txId = transactionId.incrementAndGet() & 0xFFFF;

        // ---- 组包：MBAP(7B) + PDU(5B) ----
        byte[] frame = new byte[12];
        frame[0] = (byte) (txId >> 8);          // 事务标识 高
        frame[1] = (byte) txId;                 // 事务标识 低
        frame[2] = 0;                           // 协议标识 = 0（Modbus）
        frame[3] = 0;
        frame[4] = 0;                           // 长度 = 6（unitId + PDU 5B）
        frame[5] = 6;
        frame[6] = (byte) properties.getUnitId();
        frame[7] = FUNCTION_READ_HOLDING_REGISTERS;
        frame[8] = (byte) (address >> 8);
        frame[9] = (byte) address;
        frame[10] = (byte) (quantity >> 8);
        frame[11] = (byte) quantity;
        out.write(frame);
        out.flush();

        // ---- 解包：先读 MBAP 头 7 字节 ----
        byte[] mbap = new byte[7];
        in.readFully(mbap);
        int respTxId = ((mbap[0] & 0xFF) << 8) | (mbap[1] & 0xFF);
        int pduLength = ((mbap[4] & 0xFF) << 8) | (mbap[5] & 0xFF); // unitId + PDU
        if (respTxId != txId) {
            throw new IOException("事务标识不匹配：期望 " + txId + "，实际 " + respTxId);
        }

        // ---- 再读 PDU（长度字段定界，pduLength 含 1 字节 unitId）----
        byte[] pdu = new byte[pduLength - 1];
        in.readFully(pdu);

        int functionCode = pdu[0] & 0xFF;
        if (functionCode == (FUNCTION_READ_HOLDING_REGISTERS | EXCEPTION_FLAG)) {
            throw new ModbusException(pdu[1] & 0xFF); // 异常响应：功能码|0x80
        }

        int byteCount = pdu[1] & 0xFF;
        int[] registers = new int[quantity];
        for (int i = 0; i < quantity; i++) {
            registers[i] = ((pdu[2 + i * 2] & 0xFF) << 8) | (pdu[3 + i * 2] & 0xFF);
        }
        return registers;
    }

    private void closeQuietly() {
        try {
            close();
        } catch (IOException ignored) {
        }
    }

    @Override
    public synchronized void close() throws IOException {
        if (socket != null) {
            socket.close();
            socket = null;
            out = null;
            in = null;
        }
    }
}
```

配套异常类：

```java
package io.github.yourname.modbus;

/** Modbus 异常响应（功能码 | 0x80），exceptionCode 即协议异常码 1~11 */
public class ModbusException extends RuntimeException {

    private final int exceptionCode;

    public ModbusException(int exceptionCode) {
        super("Modbus exception response, code = " + exceptionCode);
        this.exceptionCode = exceptionCode;
    }

    public int getExceptionCode() {
        return exceptionCode;
    }
}
```

#### 3.3.3 四个 Spring 集成层设计决策

1. **实现 `Closeable`**——Spring 容器关闭时自动推断调用单例 Bean 的 `close()`（inferred destroy method），应用停机自动释放 TCP 连接，用户零清理代码。
2. **所有方法 `synchronized`**——单 Socket 请求必须串行，与网关 FIFO 串行下行模型一致；要并发走连接池而非去锁。
3. **`connect()` 惰性**——Bean 创建在启动期，此时 PLC 可能未上电；启动期连失败会让整个应用起不来。惰性连接 + 重试把失败推迟到使用时，启动永远成功（Hikari 同款思路）。
4. **重试失败后 `closeQuietly()`**——超时/断连后 Socket 可能残留半截报文，复用会永久串包，断开重建是唯一安全选择。

#### 3.3.4 本步自检

| 检查项 | 通过标志 |
|---|---|
| 实现 `Closeable` | 容器关闭自动释放连接 |
| 事务标识回显校验 | `respTxId != txId` 抛异常 |
| 异常响应识别 | 功能码 `| 0x80` 转 `ModbusException` |
| 按 MBAP 长度字段定界读 PDU | 不靠固定长度硬读 |
| `mvn compile` 通过 | BUILD SUCCESS |

### 3.4 ModbusAutoConfiguration 自动装配（Starter 的灵魂）

![08-03 条件装配决策流]({{ site.baseurl }}/assets/svg/08-03-条件装配决策流.svg)

#### 3.4.1 装配类要回答的三个问题

| 问题 | 答案 | 对应注解 |
|---|---|---|
| 什么时候装配？ | 用户没显式关闭就装配 | `@ConditionalOnProperty(matchIfMissing = true)` |
| 装配什么？ | `ModbusProperties` + `ModbusTcpClient` | `@EnableConfigurationProperties` + `@Bean` |
| 用户想定制怎么办？ | 用户自己定义了就不覆盖 | `@ConditionalOnMissingBean` |

#### 3.4.2 代码

```java
package io.github.yourname.modbus;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;

/**
 * Modbus Starter 自动装配类。
 * 由 META-INF/spring/...AutoConfiguration.imports 注册（3.5 节）。
 */
@AutoConfiguration
@EnableConfigurationProperties(ModbusProperties.class)
@ConditionalOnProperty(prefix = "modbus", name = "enabled", havingValue = "true", matchIfMissing = true)
public class ModbusAutoConfiguration {

    /**
     * 仅当容器中没有 ModbusTcpClient 时才创建。
     * 用户自定义的 Bean 优先——这是 Starter 的"礼貌"。
     */
    @Bean
    @ConditionalOnMissingBean
    public ModbusTcpClient modbusTcpClient(ModbusProperties properties) {
        return new ModbusTcpClient(properties);
    }
}
```

#### 3.4.3 逐注解审查（五个检查点）

1. **`@AutoConfiguration` vs `@Configuration`**——Boot 2.7+ 专用注解，语义是"自动配置类，由 imports 文件驱动加载"。内部组合 `@Configuration(proxyBeanMethods = false)`（Lite 模式），`@Bean` 方法间互调不走代理，强制自动配置类互不依赖，省 CGLIB 开销。
2. **`@EnableConfigurationProperties(ModbusProperties.class)`**——补上 3.2 节"只绑定不注册"的缺口，负责注册 + 绑定，保证注入时属性已完成绑定校验。
3. **`@ConditionalOnProperty` 的 `matchIfMissing = true`**——不配置就默认启用，零配置体验；`false` 则必须显式开启（适合重资源组件）。`modbus.enabled=false` 时整个装配类被跳过，一个 Bean 都不创建。
4. **`@ConditionalOnMissingBean`**——Starter 黄金法则：永远给用户留后门。用户自己声明同类型 Bean，默认装配自动退让；没有此注解的 Starter 会逼用户用 `@Primary` 硬抢。
5. **构造器注入 `ModbusProperties`**——`@Bean` 方法参数由容器注入，此时已完成绑定。**绝不能在装配类里 `new ModbusProperties()`**，那样拿到未绑定空对象，yml 配置全部失效（新手最常犯错误）。

#### 3.4.4 条件装配排查手段：条件评估报告

启动参数加 `--debug`（或 yml `debug: true`），打印 Condition Evaluation Report：

```
Positive matches:（条件满足，装配了）
   ModbusAutoConfiguration matched:
      - @ConditionalOnProperty (modbus.enabled=true) matched
Negative matches:（条件不满足，没装配）
Exclusions:（被排除）
```

排查"Starter 怎么没生效"，第一反应看这份报告，每个条件的匹配/不匹配原因逐条列出。

#### 3.4.5 本步自检

| 检查项 | 通过标志 |
|---|---|
| 用 `@AutoConfiguration` 而非 `@Configuration` | Boot 2.7+ 规范 |
| `@EnableConfigurationProperties` 注册了属性类 | 属性可注入且已绑定 |
| `matchIfMissing = true` | 零配置默认启用 |
| `@Bean` 上有 `@ConditionalOnMissingBean` | 用户自定义可覆盖 |
| `mvn compile` 通过 | BUILD SUCCESS |

### 3.5 注册文件与本地验证

#### 3.5.1 注册文件：自动装配的"开关接线"

Spring Boot 不会自动发现装配类，必须显式登记。路径（固定，一字不能错）：

```
src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

内容（每行一个装配类全限定名）：

```
io.github.yourname.modbus.ModbusAutoConfiguration
```

工作原理：启动时扫描 classpath 所有 jar 的该文件 → 读到装配类全限定名作为候选 → 逐个评估 @ConditionalOnXxx → 通过则装配。

历史对照：

| 时代 | 注册位置 | 现状 |
|---|---|---|
| Boot 1.x ~ 2.6 | `META-INF/spring.factories` 的 `EnableAutoConfiguration` 键 | Boot 3.x 不再读取此键 |
| Boot 2.7+ | `AutoConfiguration.imports` 文件 | 唯一方式 |

换掉 spring.factories 的原因：大杂烩（初始化器/监听器/自动配置混塞），无法精细排序去重；新文件职责单一、一行一类，支持 `@AutoConfiguration(before/after)` 排序。

#### 3.5.2 打包并安装到本地仓库

```powershell
mvn clean package   # 基本打包
mvn install         # 安装到本地仓库 ~/.m2/repository
```

install 后，本地任何工程都能像引用中央仓库依赖一样引用它——发版前的最后演习。

#### 3.5.3 验证工程：三个场景

新建 `modbus-demo` 工程，引入依赖：

```xml
<dependency>
    <groupId>io.github.yourname</groupId>
    <artifactId>modbus-spring-boot-starter</artifactId>
    <version>1.0.0</version>
</dependency>
```

验证组件：

```java
package com.example.demo;

import io.github.yourname.modbus.ModbusTcpClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DemoConfig {

    private static final Logger log = LoggerFactory.getLogger(DemoConfig.class);

    @Bean
    public ApplicationRunner modbusSmokeTest(ModbusTcpClient client) {
        return args -> {
            // 注入成功即证明自动装配生效；读寄存器需要真实 PLC，连不上会按重试策略报错
            log.info("ModbusTcpClient 注入成功: {}", client);
            try {
                int[] registers = client.readHoldingRegisters(0, 10);
                log.info("读到寄存器: {}", java.util.Arrays.toString(registers));
            } catch (Exception e) {
                log.warn("读取失败（无真实 PLC 属预期）: {}", e.getMessage());
            }
        };
    }
}
```

| 场景 | yml / 代码 | 预期结果 |
|---|---|---|
| 一：默认装配生效 | 只配 host/port/unit-id | 日志见 `ModbusTcpClient 注入成功` |
| 二：开关关闭 | `modbus.enabled: false` | 报找不到 Bean（报错反而是验证通过的标志） |
| 三：用户自定义覆盖 | 自己声明同类型 @Bean | 自定义日志出现且仅一次，默认装配退让 |

#### 3.5.4 用 `--debug` 看条件报告

| 场景 | 报告中位置 |
|---|---|
| 一 | `ModbusAutoConfiguration` 在 Positive matches |
| 二 | 在 Negative matches，原因 `@ConditionalOnProperty did not match` |
| 三 | 类级 Positive，`modbusTcpClient` 方法级 Negative（did not find existing bean） |

#### 3.5.5 本步自检

| 检查项 | 通过标志 |
|---|---|
| imports 文件路径与文件名完全正确 | 一字不差 |
| 文件内容是装配类全限定名 | 一行一个，无多余空格 |
| `mvn install` 成功 | 本地仓库出现该构件 |
| 场景一：注入成功 | 日志见注入成功 |
| 场景二：关闭生效 | 报找不到 Bean（预期行为） |
| 场景三：覆盖生效 | 自定义日志出现且仅一次 |

## 4. pom 发版配置

![08-04 deploy 生命周期与插件时序]({{ site.baseurl }}/assets/svg/08-04-deploy生命周期与插件时序.svg)

### 4.1 校验清单 → pom 配置映射

| 校验清单（1.3 节） | pom 兑现方式 | 小节 |
|---|---|---|
| 1. 元信息完整 | 3.1 节已写好 | ✅ |
| 2. 附 `-sources.jar` | `maven-source-plugin` | 4.2 |
| 3. 附 `-javadoc.jar` | `maven-javadoc-plugin` | 4.3 |
| 4. GPG 签名 `.asc` | `maven-gpg-plugin` | 4.4 |
| 5. 命名空间 + 上传 | `central-publishing-maven-plugin` | 4.5 |

设计原则：四个插件全部放进 `release` profile，日常 `mvn package` 不签名不打源码包（快），只有 `mvn deploy -Prelease` 走完整发版链路。

插件版本基线（2026-08 查证）：source 3.3.1 / javadoc 3.11.2 / gpg 3.2.8 / central-publishing 0.11.0。

### 4.2 maven-source-plugin（源码包）

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-source-plugin</artifactId>
    <version>3.3.1</version>
    <executions>
        <execution>
            <id>attach-sources</id>
            <goals>
                <goal>jar-no-fork</goal>  <!-- 不用 jar goal：它会 fork 新生命周期，有递归触发构建风险 -->
            </goals>
        </execution>
    </executions>
</plugin>
```

审查点：用 `jar-no-fork` 而非 `jar`，直接复用当前构建产物，官方推荐。

### 4.3 maven-javadoc-plugin（文档包）

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-javadoc-plugin</artifactId>
    <version>3.11.2</version>
    <executions>
        <execution>
            <id>attach-javadocs</id>
            <goals>
                <goal>jar</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <!-- doclint 严格校验会把中文注释/不规范标签当错误，发版场景关掉 -->
        <doclint>none</doclint>
        <charset>UTF-8</charset>
        <encoding>UTF-8</encoding>
    </configuration>
</plugin>
```

审查点：
- `doclint=none` 实战必配——中央仓库只要求 javadoc 包存在，不审查内容质量
- `charset/encoding` 显式 UTF-8，防 Windows 默认 GBK 导致中文注释乱码

### 4.4 maven-gpg-plugin（签名）

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-gpg-plugin</artifactId>
    <version>3.2.8</version>
    <executions>
        <execution>
            <id>sign-artifacts</id>
            <phase>verify</phase>   <!-- 打包后、部署前签名，覆盖全部构件 -->
            <goals>
                <goal>sign</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <!-- 指定用哪把私钥：第 2.3 步的 Key ID -->
        <keyname>3AA5C34371567BD2</keyname>
        <!-- 口令从 settings.xml 的 server id=gpg.passphrase 读取 -->
        <passphraseServerId>gpg.passphrase</passphraseServerId>
        <gpgArguments>
            <!-- 关键：不弹交互框，口令走 loopback 通道从配置读 -->
            <arg>--pinentry-mode</arg>
            <arg>loopback</arg>
            <arg>--batch</arg>
            <arg>--yes</arg>
        </gpgArguments>
    </configuration>
</plugin>
```

审查点：
1. `--pinentry-mode loopback`——2.7 节预告的坑的解法，没有它 GPG 2.1+ 弹框卡死 CI
2. `passphraseServerId`——口令来源指向 settings.xml，口令不落 pom、不进 git
3. 绑定 `verify` 阶段——此时 sources/javadoc 已生成，一次签名覆盖全部构件

**Windows 新坑（GPG 2.5+，2026 实测）**：签名可能报 `gpg: sending fd ... to keyboxd: Input/output error`，签名实际成功但退出码 2 导致 Maven 失败。解法——发版前先杀守护进程：`gpgconf --kill keyboxd`。

### 4.5 central-publishing-maven-plugin（上传发布）

```xml
<plugin>
    <groupId>org.sonatype.central</groupId>
    <artifactId>central-publishing-maven-plugin</artifactId>
    <version>0.11.0</version>
    <extensions>true</extensions>   <!-- 关键：接管 deploy 阶段，替代默认 maven-deploy-plugin -->
    <configuration>
        <!-- 对应 settings.xml 里 id=central 的 server（Token 凭证） -->
        <publishingServerId>central</publishingServerId>
        <!-- 首次发版建议 false：上传后去 Portal 手动点 Release，留人工确认闸 -->
        <autoPublish>false</autoPublish>
    </configuration>
</plugin>
```

审查点：
1. `extensions=true` 是灵魂——替换默认 deploy 行为，把构件打成 bundle.zip 上传 Central Portal；没有这行 `mvn deploy` 还走老路
2. `autoPublish=false`——首次发版手动 Release，发布不可撤回多一道闸；跑通后可改 true 配合 CI
3. **不需要 `distributionManagement`**——OSSRH 时代产物，新插件体系下删掉

### 4.6 组装位置规则

- `central-publishing-maven-plugin` 放**主 `<build>`**（extensions 插件放 profile 里可能不生效，Maven 扩展加载机制限制）
- source / javadoc / gpg 三个插件放 **`release` profile**：

```xml
<profiles>
    <profile>
        <id>release</id>
        <build>
            <plugins>
                <!-- 4.2 / 4.3 / 4.4 三个插件完整配置放这里 -->
            </plugins>
        </build>
    </profile>
</profiles>
```

### 4.7 发版命令与生命周期对照

```powershell
# 日常开发：不签名、不生成源码/文档包
mvn clean package

# 发版：激活 release profile
gpgconf --kill keyboxd   # Windows GPG 2.5+ 先杀守护进程
mvn clean deploy -Prelease
```

触发时序：`package（主 jar）→ verify：source → javadoc → gpg 签名 → deploy：central-publishing 打 bundle.zip 上传 Portal`。

### 4.8 本步自检

| 检查项 | 通过标志 |
|---|---|
| 四个插件版本与本课一致 | source 3.3.1 / javadoc 3.11.2 / gpg 3.2.8 / central 0.11.0 |
| gpg 的 `keyname` 换成自己的 Key ID | 2.3 步取的那串 |
| central 插件在主 build 且 `extensions=true` | 不在 profile 里 |
| 其余三插件在 `release` profile | 日常构建不触发 |
| `mvn clean package` 正常 | BUILD SUCCESS 且无 .asc 生成 |

## 5. 发布与验证

### 5.1 执行发布命令与输出解读

```powershell
gpgconf --kill keyboxd          # Windows GPG 2.5+ 预防 keyboxd 报错
mvn clean deploy -Prelease
```

成功输出关键行：

```
[INFO] Using credentials from server id central in settings.xml     ← 凭证找对了
[INFO] Using Usertoken auth, with namecode: XXXXXXX                 ← Token 认证生效
[INFO] Staging 6 files                                              ← jar/pom/sources/javadoc + 各自 .asc
[INFO] Created bundle successfully .../central-publishing/central-bundle.zip
[INFO] Uploaded bundle successfully, deploymentId: 9590fb21-...
[INFO] Deployment 9590fb21-... has been validated.
       To finish publishing visit https://central.sonatype.com/publishing/deployments
[INFO] BUILD SUCCESS
```

**关键认知：`BUILD SUCCESS` ≠ 已发布**——只代表上传成功 + 校验通过，构件还在 Portal 暂存区，全世界看不到；最后 Release 要手动做（autoPublish=false）。

常见失败对照：

| 报错 | 原因 | 解法 |
|---|---|---|
| `401 Unauthorized` | Token 错或 serverId 不匹配 | 核对 settings.xml `id=central` 与 Token |
| `namespace not allowed` / `403` | groupId 未验证或拼错 | 回 Portal 看 Namespace 状态 |
| `gpg: signing failed` | 口令错 / keyboxd 问题 | 核对 `gpg.passphrase`；`gpgconf --kill keyboxd` |
| `javadoc generation failed` | 注释被 doclint 拦 | 确认 `doclint=none` 生效 |

### 5.2 Portal 页面操作：校验 → Release

1. 打开 `https://central.sonatype.com/publishing/deployments`
2. 状态流转：`Uploading → Validating → Validated →（点 Release）→ Publishing → Published`；校验失败则 Validation failed（点开看逐条原因，可 Drop 后修复重传）
3. Validated 状态两个按钮：**Publish**（正式发布，不可撤回）/ **Drop**（丢弃——发布前最后一次反悔机会，这就是人工闸的价值）
4. 点 Publish 前核对 bundle 文件清单：主 jar、pom、sources、javadoc、每个都有 .asc 和校验和
5. 校验失败时 Portal 给出精确到文件的失败原因，按 4.1 映射表修，重新 deploy 即可——**未发布前可反复重传同一版本**

### 5.3 中央仓库检索验证（三个层面）

① 搜索入口 `https://central.sonatype.com` 搜构件名（索引有几分钟延迟）

② 仓库直连（最硬核证据）：

```
https://repo1.maven.org/maven2/io/github/yourname/modbus-spring-boot-starter/1.0.0/
```

需看到 8 类文件：主 jar（+.asc）、pom（+.asc）、sources（+.asc）、javadoc（+.asc）、maven-metadata.xml

③ 签名验证（可选）：

```powershell
gpg --verify modbus-spring-boot-starter-1.0.0.jar.asc modbus-spring-boot-starter-1.0.0.jar
# Good signature from "Your Name <you@example.com>" 即签名链完整
```

### 5.4 镜像同步延迟（aliyun）

- 中央仓库有了 ≠ 镜像立刻有，aliyun 同步通常数分钟到数小时
- 等不了可临时直连验证：`mvn dependency:get -Dartifact=io.github.yourname:modbus-spring-boot-starter:1.0.0`
- **本地缓存陷阱**：拉取失败会留下 `*.lastUpdated` 失败标记，镜像同步好后仍可能报找不到。清掉再试：

```powershell
Remove-Item "$env:USERPROFILE\.m2\repository\io\github\yourname" -Recurse -Force
```

### 5.5 终极验证：全新工程引入

全新工程只加三行依赖坐标，跑 3.5.3 三场景（默认装配 / enabled=false / 自定义覆盖）。全部通过 = 发版闭环完成——此时你的 Starter 与 spring-boot-starter-web 使用体验无差别。

### 5.6 本步自检

| 检查项 | 通过标志 |
|---|---|
| `mvn deploy -Prelease` 输出 `Uploaded bundle successfully` | 上传成功 |
| Portal 状态到 Validated | 五条校验全过 |
| 点 Publish 后状态 Published | 正式发布 |
| repo1 直连 URL 能看到 8 类文件 | 中央仓库确有其物 |
| `gpg --verify` 输出 Good signature | 签名链完整（可选） |
| 全新工程三场景验证通过 | 发版闭环完成 |

## 6. 总结与进阶方向

![08-05 全课主线闭环]({{ site.baseurl }}/assets/svg/08-05-全课主线闭环.svg)

### 6.1 全课主线

```
第1节 全景图        第2节 环境          第3节 Starter 本体
五角色·五校验  →   Token·命名空间·GPG →  属性绑定 → 核心组件 → 条件装配 → imports 注册
不可撤回            四样凭证              （自动装配是灵魂）
                                              │
第6节 进阶  ←   第5节 发布验证   ←   第4节 pom 发版配置
演进路线        deploy→Validated      五校验逐一兑现：
                →手动Release→Published  sources·javadoc·gpg·central插件
```

三个最重要的认知：
1. **自动装配 = 发现 + 条件 + 注册**：imports 文件负责发现，`@ConditionalOnXxx` 负责条件，`@EnableConfigurationProperties` + `@Bean` 负责注册。任何官方 Starter 拆开都是这个骨架。
2. **发版 = 五校验的兑现**：元信息、sources、javadoc、签名、命名空间——pom 里每个插件对应一条校验，没有多余配置。
3. **发布不可撤回 + 人工闸**：`autoPublish=false` 留 Drop 机会，是对待"永久公开"的正确姿态。

### 6.2 发版后的日常运维

**① 版本升级策略（语义化版本）**

| 变更类型 | 版本号动作 | 例子 |
|---|---|---|
| 修 bug，API 不变 | 补丁位 +1 | 1.0.0 → 1.0.1 |
| 加功能，向后兼容 | 次版本 +1 | 1.0.0 → 1.1.0 |
| 破坏性变更 | 主版本 +1 | 1.0.0 → 2.0.0 |

改 `<version>` 重新 `mvn deploy -Prelease`。永远不要复用已发布的版本号。

**② GPG 密钥续期与备份**

- 到期前续期：`gpg --edit-key <KeyID>` → `expire` → 重新 `--send-keys`
- 私钥务必备份：`gpg --armor --export-secret-keys > private-key.asc` 存安全位置——没有私钥就无法再发新版本

**③ Token 泄露处理**

Portal → View Account → 重新 Generate User Token，旧 Token 立即失效，更新 settings.xml。

### 6.3 进阶演进路线

| 方向 | 内容 | 价值 |
|---|---|---|
| 双模块拆分 | autoconfigure + starter 分离 | 官方标准形态 |
| CI 自动发版 | GitHub Actions 打 tag 触发，密钥放 Secrets，autoPublish=true | 发版流水线化 |
| 功能完善 | 写寄存器（06/16）、连接池、多从站、actuator HealthIndicator | 教学品变生产级 |
| 测试体系 | `ApplicationContextRunner` 测条件装配 | 三场景验证脚本化 |

`ApplicationContextRunner` 示例（3.5.3 手工场景的自动化版）：

```java
new ApplicationContextRunner()
    .withConfiguration(AutoConfigurations.of(ModbusAutoConfiguration.class))
    .withPropertyValues("modbus.enabled=false")
    .run(context -> assertThat(context).doesNotHaveBean(ModbusTcpClient.class));
```

### 6.4 与生产场景的闭环

- **网关项目**：Starter 完善后可替代手写 Modbus 连接代码，配置驱动 + 自动装配
- **yudao**：其 `yudao-spring-boot-starter-*` 系列就是同样的命名规范 + 装配套路，从"会用"变"能写"
- **简历价值**：中央仓库可检索的开源构件是硬通货
