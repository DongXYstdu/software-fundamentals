---
title: 计算机网络 - HTTP协议演进
date: 2026-05-25 00:00:00 +0800
order: 5
categories: [计算机网络]
tags: [HTTP, HTTP2, HTTP3, QUIC]
math: true
mermaid: true
---

## 概述

HTTP（HyperText Transfer Protocol）是互联网数据通信的基石。从 1991 年的 HTTP/0.9 到如今的 HTTP/3，协议经历了从简单到复杂、从低效到高性能的持续演进。每一次迭代都深刻影响了 Web 架构和工程实践。

```mermaid
timeline
  title HTTP 协议演进时间线
  1991 : HTTP/0.9 : 仅 GET 方法，无头部
  1996 : HTTP/1.0 : 方法扩展，Header 支持
  1997 : HTTP/1.1 : 持久连接，管线化
  2015 : HTTP/2   : 多路复用，头部压缩
  2022 : HTTP/3   : QUIC 传输，0-RTT
```

---

## HTTP/0.9 — 一切的开端

HTTP/0.9 极其简单：

- 仅支持 `GET` 方法
- 没有请求头和响应头
- 响应只能是 HTML
- 一次请求-响应后立即断开连接

```text
请求：GET /index.html
响应：<html>...</html>
```

**问题**：无法传输非 HTML 资源，无状态码，无缓存机制。

---

## HTTP/1.0 — 功能扩展

HTTP/1.0 引入了关键特性：

| 特性 | 说明 |
|------|------|
| 方法扩展 | GET、HEAD、POST |
| 请求/响应头 | Content-Type、Content-Length 等 |
| 状态码 | 200 OK、404 Not Found 等 |
| 多类型支持 | 不再限于 HTML |

```http
GET /index.html HTTP/1.0
Host: www.example.com
Accept: text/html

HTTP/1.0 200 OK
Content-Type: text/html
Content-Length: 1234

<html>...</html>
```

**核心问题**：每次请求都需要新建 TCP 连接，三次握手 + 慢启动带来巨大开销。

---

## HTTP/1.1 — 持久连接与管线化

### 持久连接（Persistent Connection）

HTTP/1.1 默认启用 `Connection: keep-alive`，一个 TCP 连接可以发送多个请求：

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  C->>S: TCP 三次握手
  C->>S: 请求1
  S->>C: 响应1
  C->>S: 请求2
  S->>C: 响应2
  C->>S: 请求3
  S->>C: 响应3
  C->>S: TCP 四次挥手
```

### 管线化（Pipelining）

管线化允许在未收到前一个响应时就发送下一个请求：

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  Note over C,S: 无管线化：串行
  C->>S: 请求1
  S->>C: 响应1
  C->>S: 请求2
  S->>C: 响应2
  Note over C,S: 管线化：并行发送
  C->>S: 请求1
  C->>S: 请求2
  S->>C: 响应1
  S->>C: 响应2
```

### HTTP/1.1 关键特性

| 特性 | 说明 |
|------|------|
| 持久连接 | 默认 keep-alive，减少 TCP 握手开销 |
| 管线化 | 允许连续发送请求（FIFO 响应） |
| 分块传输 | `Transfer-Encoding: chunked` |
| 缓存控制 | Cache-Control、ETag、If-None-Match |
| Host 头 | 支持虚拟主机 |
| 范围请求 | Range 请求支持断点续传 |

### 队头阻塞（Head-of-Line Blocking）

管线化存在严重的队头阻塞问题——如果第一个请求处理慢，后续所有请求都必须等待：

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  C->>S: 请求1（慢查询）
  C->>S: 请求2（静态资源）
  C->>S: 请求3（静态资源）
  Note over S: 请求1 处理中...2s
  S->>C: 响应1
  Note over C: 请求2、3 被阻塞
  S->>C: 响应2
  S->>C: 响应3
```

**工程实践**：浏览器通常采用 6 个并行 TCP 连接来缓解队头阻塞，但引入了额外的连接管理开销。

---

## HTTP/2 — 多路复用革命

### 核心概念

HTTP/2 在应用层引入了**帧（Frame）**和**流（Stream）**的概念：

```mermaid
graph TD
  A[HTTP/2 连接] --> B[Stream 1]
  A --> C[Stream 3]
  A --> D[Stream 5]
  B --> E[HEADERS Frame]
  B --> F[DATA Frame]
  C --> G[HEADERS Frame]
  C --> H[DATA Frame]
  D --> I[HEADERS Frame]
  D --> J[DATA Frame x3]
```

### 三大核心特性

#### 1. 多路复用（Multiplexing）

一个 TCP 连接上可以并行交错发送多个流的帧：

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  C->>S: Stream1: HEADERS
  C->>S: Stream3: HEADERS
  C->>S: Stream1: DATA
  S->>C: Stream3: HEADERS
  S->>C: Stream1: HEADERS
  S->>C: Stream3: DATA
  S->>C: Stream1: DATA
```

**关键**：不同流的帧可以交错传输，解决了应用层队头阻塞。

#### 2. 头部压缩（HPACK）

HTTP/1.1 每次请求都携带完整头部，大量重复字段浪费带宽。HPACK 使用：

- **静态表**：预定义 61 个常见头部字段
- **动态表**：基于连接历史动态维护
- **哈夫曼编码**：压缩字符串值

```text
静态表示例：
  Index  2  → :method GET
  Index  4  → :path /
  Index  16 → accept-encoding
  Index  49 → content-type

压缩前：:method: GET :path: / accept-encoding: gzip (约 50 bytes)
压缩后：0x82 0x84 0x90 (约 3 bytes)
```

#### 3. 服务器推送（Server Push）

服务器可以主动推送资源到客户端缓存：

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  C->>S: GET /index.html
  S->>C: Stream1: index.html
  S->>C: Stream2: PUSH style.css
  S->>C: Stream2: PUSH style.css DATA
  S->>C: Stream3: PUSH app.js
  S->>C: Stream3: PUSH app.js DATA
```

### HTTP/1.1 vs HTTP/2 对比

| 维度 | HTTP/1.1 | HTTP/2 |
|------|----------|--------|
| 连接复用 | 6 个并行 TCP 连接 | 单连接多路复用 |
| 头部处理 | 纯文本重复传输 | HPACK 压缩 |
| 请求优先级 | 无 | 权重与依赖 |
| 服务器推送 | 不支持 | 支持 |
| 传输单位 | 文本报文 | 二进制帧 |
| 队头阻塞 | 应用层 | 仅 TCP 层 |

### TCP 层队头阻塞

HTTP/2 解决了应用层队头阻塞，但 TCP 层的队头阻塞仍然存在：

```mermaid
sequenceDiagram
  participant C as Client
  participant N as 网络
  participant S as Server
  C->>N: Stream1: Frame1 ✅
  C->>N: Stream3: Frame1 ❌ 丢失
  C->>N: Stream1: Frame2 ✅
  Note over N: TCP 重传 Stream3 Frame1
  N->>S: Stream1: Frame1 ✅
  Note over S: 等待重传完成，Frame2 被阻塞
  N->>S: Stream3: Frame1 ✅ 重传到达
  S->>S: 现在才能处理后续帧
```

**一个 TCP 包丢失会阻塞所有流**，这是 HTTP/2 在高丢包率网络下性能退化的根本原因。

---

## HTTP/3 + QUIC — 传输层革命

### QUIC 协议

QUIC（Quick UDP Internet Connections）基于 UDP 构建，在用户态实现了可靠传输：

```mermaid
graph LR
  subgraph "传统协议栈"
    A1[HTTP/2] --> B1[TCP]
    B1 --> C1[IP]
    A1 --> D1[TLS 1.2/1.3]
  end
  subgraph "QUIC 协议栈"
    A2[HTTP/3] --> B2[QUIC]
    B2 --> C2[UDP]
    B2 --> D2[内置 TLS 1.3]
    C2 --> E2[IP]
  end
```

### QUIC 核心特性

#### 1. 连接迁移

TCP 连接由四元组（源IP、源端口、目标IP、目标端口）标识。网络切换时连接断开。QUIC 使用 **Connection ID** 标识连接：

```mermaid
sequenceDiagram
  participant M as 手机(WiFi)
  participant S as Server
  M->>S: QUIC Packet (CID: 0xABC)
  Note over M: WiFi → 4G 切换
  participant L as 手机(4G)
  L->>S: QUIC Packet (CID: 0xABC)
  Note over S: CID 匹配，连接不断
  S->>L: 继续传输
```

#### 2. 0-RTT 连接建立

```mermaid
sequenceDiagram
  participant C as Client
  participant S as Server
  Note over C,S: 首次连接：1-RTT
  C->>S: ClientHello
  S->>C: ServerHello + 证书
  C->>S: Finished + HTTP 请求
  S->>C: HTTP 响应
  Note over C,S: 恢复连接：0-RTT
  C->>S: ClientHello + 0-RTT 数据
  S->>C: 响应
```

#### 3. 解决队头阻塞

QUIC 的流在传输层就是独立的，一个流的包丢失不影响其他流：

```mermaid
graph TD
  subgraph "HTTP/2 over TCP"
    A1[Stream1] --> T1[TCP 单一字节流]
    A2[Stream3] --> T1
    A3[Stream5] --> T1
    T1 --> B1[丢包阻塞所有流]
  end
  subgraph "HTTP/3 over QUIC"
    C1[Stream1] --> Q1[独立流传输]
    C2[Stream3] --> Q2[独立流传输]
    C3[Stream5] --> Q3[独立流传输]
    Q1 --> D1[丢包仅阻塞该流]
    Q2 --> D2[其他流不受影响]
    Q3 --> D3[其他流不受影响]
  end
```

### HTTP/2 vs HTTP/3 对比

| 维度 | HTTP/2 | HTTP/3 |
|------|--------|--------|
| 传输层 | TCP | QUIC(UDP) |
| 队头阻塞 | TCP 层存在 | 完全消除 |
| 连接建立 | TCP + TLS = 2-3 RTT | 1-RTT / 0-RTT |
| 连接迁移 | 不支持 | CID 支持 |
| 拥塞控制 | 内核态 | 用户态，可定制 |
| 中间件兼容 | 好 | UDP 可能被拦截 |

---

## HTTPS — 安全层

### HTTPS 架构

```mermaid
graph LR
  A[HTTP] --> B[TLS]
  B --> C[TCP]
  B --> D[加密/解密]
  D --> E[证书验证]
  D --> F[密钥协商]
```

### TLS 在 HTTP 协议栈中的位置

```
+-------------------+
|    HTTP/1.1/2/3   |  应用层
+-------------------+
|       TLS         |  安全层
+-------------------+
|   TCP / QUIC      |  传输层
+-------------------+
|       IP          |  网络层
+-------------------+
```

### HTTPS 性能优化实践

| 优化手段 | 说明 | 效果 |
|----------|------|------|
| Session 复用 | TLS Session ID / Session Ticket | 减少 1-RTT |
| OCSP Stapling | 服务器附带证书状态 | 减少客户端验证延迟 |
| HSTS | 强制 HTTPS | 消除 302 跳转 |
| 证书链优化 | 减少中间证书层级 | 减少验证时间 |
| HTTP/2 | 多路复用 | 减少连接数 |
| 0-RTT | TLS 1.3 + QUIC | 恢复连接零延迟 |

---

## 工程实践：协议选型决策

```mermaid
graph TD
  A[协议选型] --> B{是否需要加密?}
  B -->|是| C{网络环境}
  B -->|否| D[HTTP/1.1 内网场景]
  C -->|低丢包率| E[HTTP/2 over TLS]
  C -->|高丢包率/移动端| F[HTTP/3 over QUIC]
  C -->|兼容性优先| G[HTTP/1.1 + CDN]
  E --> H[Nginx 1.25+ / Cloudflare]
  F --> I[Cloudflare / Google Cloud]
  G --> J[传统部署]
```

### Nginx 配置 HTTP/2

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    # TLS 1.3
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
}
```

### Nginx 配置 HTTP/3（实验性）

```nginx
server {
    listen 443 quic reuseport;
    listen 443 ssl;
    http2 on;

    ssl_protocols TLSv1.3;

    # Alt-Svc 头声明 HTTP/3 支持
    add_header Alt-Svc 'h3=":443"; ma=86400';
}
```

---

## 全版本对比总览

| 特性 | HTTP/0.9 | HTTP/1.0 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|----------|----------|----------|--------|--------|
| 方法 | GET | GET/HEAD/POST | 全部 | 全部 | 全部 |
| 头部 | 无 | 有 | 有 | HPACK压缩 | QPACK压缩 |
| 连接 | 短连接 | 短连接 | 持久连接 | 多路复用 | 多路复用 |
| 加密 | 无 | 无 | 可选 | 可选 | 强制TLS1.3 |
| 传输层 | TCP | TCP | TCP | TCP | QUIC/UDP |
| 队头阻塞 | N/A | 严重 | 应用层 | TCP层 | 无 |
| 连接建立 | 1-RTT | 1-RTT | 1-RTT | 2-3RTT | 0-1RTT |
| 服务器推送 | 无 | 无 | 无 | 有 | 有 |

---

## 面试 Q&A

**Q1: HTTP/1.1 的管线化为什么没有被广泛使用？**

A: 管线化要求响应按序返回（FIFO），导致队头阻塞问题。如果第一个请求响应慢，后续响应全部被阻塞。此外，代理服务器和中间件对管线化支持不一致，存在兼容性问题。浏览器大多默认禁用管线化。

**Q2: HTTP/2 多路复用是否意味着不需要域名分片了？**

A: 是的。HTTP/2 单连接即可并行传输多个流，域名分片反而有害——多个连接会分散拥塞窗口，降低吞吐量，且无法共享 HPACK 动态表。最佳实践是合并到同一域名下。

**Q3: HTTP/3 为什么选择 UDP 而不是改进 TCP？**

A: TCP 协议栈在操作系统内核中实现，升级需要修改内核并广泛部署，周期极长。中间网络设备（NAT、防火墙）对 TCP 行为有固定预期，修改可能导致兼容性问题。QUIC 选择在用户态基于 UDP 实现，可以快速迭代，且 UDP 穿透性好。

**Q4: 0-RTT 有什么安全风险？**

A: 0-RTT 数据可能遭受**重放攻击**。攻击者可以捕获并重放 0-RTT 请求，导致服务器重复执行操作（如重复支付）。因此 0-RTT 仅适用于幂等请求，非幂等操作应使用 1-RTT。

**Q5: 如何判断当前网站使用的 HTTP 版本？**

A: Chrome DevTools → Network 面板 → 右键列头 → 勾选 Protocol 列。也可以通过 `curl -I --http2` 或查看响应头中的 Alt-Svc 字段判断 HTTP/3 支持。

**Q6: HTTP/2 的服务器推送在实际中为什么使用较少？**

A: 服务器推送存在几个问题：(1) 服务器难以准确判断客户端是否已缓存该资源；(2) 推送的资源占用客户端缓存空间；(3) 中间代理可能不支持推送；(4) Chrome 已在 2023 年宣布移除 HTTP/2 Server Push 支持。替代方案是使用 `<link rel="preload">` 让客户端主动预加载。

<div class='context-nav'>
<a class='context-link prev' href='/software-fundamentals/posts/计算机网络-HTTPS优化/'><span class='context-label'>上一篇</span><span class='context-title'>HTTPS 如何优化</span></a>
<a class='context-link next' href='/software-fundamentals/posts/计算机网络-HTTP常见面试题/'><span class='context-label'>下一篇</span><span class='context-title'>HTTP 常见面试</span></a>
</div>
