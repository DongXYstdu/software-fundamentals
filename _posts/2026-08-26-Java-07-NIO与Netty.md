---
title: NIO 与 Netty：从 BIO 到多路复用
date: 2026-08-26 09:00:00 +0800
categories: [Java]
tags: [NIO, Netty, Reactor]
---

# NIO 与 Netty：Reactor 模式与事件循环
---

## 第 1 段：BIO 的三个致命问题

![07-04 BIO 三个致命问题]({{ site.baseurl }}/assets/svg/07-04-BIO三个致命问题.svg)

| 问题 | 说明 |
|---|---|
| 线程与连接 1:1 绑定 | 1000 台设备 = 1000 个线程；默认栈 1MB/线程，光栈内存约 1GB |
| read() 阻塞 = 线程冻结 | 数据没到线程挂起，期间不能服务任何其他连接；设备上报稀疏时线程利用率极低 |
| 上下文切换吃掉 CPU | "连接多但 CPU 不高"——时间花在调度与等待，而非干活 |

**结论**：BIO 的瓶颈不是 CPU 算力，而是**线程数量**。突破方向 = 让少量线程同时照看大量连接。

## 第 2 段：NIO 三件套与多路复用

![07-05 NIO 三件套与多路复用]({{ site.baseurl }}/assets/svg/07-05-NIO三件套与多路复用.svg)

| 组件 | 类比 | 关键点 |
|---|---|---|
| Channel | 双向车道 | 可读可写；ServerSocketChannel 管新连接，SocketChannel 管已建立连接 |
| Buffer | 货车车厢 | 数据进出必过 Buffer；flip() 是读写模式开关 |
| Selector | 值班员 | N 个 Channel 注册进来，只报告"谁有事件" |

- **阻塞点转移**：BIO 阻塞在每个连接的 read()（阻塞点=连接数）→ NIO 只阻塞在一次 select()（阻塞点=1）
- select() 返回**就绪清单**（SelectionKey 集合），线程只遍历清单，永远碰不到没数据的连接
- 底层委托操作系统：Linux = epoll（内核主动推就绪事件），Windows = select
- 网关场景：500 台设备，BIO 要 500 线程干等；NIO 只需 1~2 线程跑 select() 循环

## 第 3 段：Reactor 三形态演进

![07-06 Reactor 三形态演进]({{ site.baseurl }}/assets/svg/07-06-Reactor三形态演进.svg)

| 形态 | 结构 | 瓶颈 |
|---|---|---|
| ① 单线程 Reactor | 一个线程包办 accept+read+业务+write | 业务处理时新连接进不来、其他连接读不到（Redis 即此模型） |
| ② 单 Reactor + Worker 池 | Reactor 只管 IO，业务扔线程池 | 单个 Reactor 扛所有连接的 accept+读写，连接上万先撑不住 |
| ③ 主从 Reactor | Main 专职 accept，Sub 组专职 IO，Worker 池专职业务 | 职责彻底分离，Netty 的选择 |

- accept 低频 → 1 线程足够；读写高频 → 一组 Sub 分摊
- **关键细节**：一条连接固定绑定在一个 SubReactor 上，所有读写同一线程处理 → 天然免锁

## 第 4 段：Netty 落地

![07-07 Netty 主从 Reactor 落地]({{ site.baseurl }}/assets/svg/07-07-Netty主从Reactor落地.svg)

### 4.1 骨架（主从 Reactor = 两个 EventLoopGroup）

```java
EventLoopGroup bossGroup = new NioEventLoopGroup(1);   // Main：只 accept，1 线程足够
EventLoopGroup workerGroup = new NioEventLoopGroup();  // Sub 组：默认 2×CPU 核数

ServerBootstrap b = new ServerBootstrap();
b.group(bossGroup, workerGroup)
 .channel(NioServerSocketChannel.class)
 .childHandler(new ChannelInitializer<SocketChannel>() {
     protected void initChannel(SocketChannel ch) { /* 每条新连接装配专属 Pipeline */ }
 });
b.bind(502).sync();   // Modbus TCP 默认端口
```

三个必记结论：
1. **EventLoop = 1 线程 + 1 Selector + 1 任务队列**，最小调度单元
2. **Channel 与 EventLoop 终身绑定** → Handler 里不用加锁（与 BIO 多线程模型最大思维差异）
3. 代价：慢 Handler 拖垮该 EventLoop 上所有连接 → 业务逻辑必须提交独立线程池

### 4.2 Pipeline 与 Handler

```java
ChannelPipeline p = ch.pipeline();
// ① 解码器（Inbound）：MBAP 头长度字段在偏移4、占2字节，adjustment=0
p.addLast(new LengthFieldBasedFrameDecoder(1024, 4, 2, 0, 0));
// ② 业务 Handler（Inbound）
p.addLast(new ModbusFrameHandler());
// ③ 编码器（Outbound）
p.addLast(new ModbusResponseEncoder());
```

```java
public class ModbusFrameHandler extends SimpleChannelInboundHandler<ByteBuf> {
    protected void channelRead0(ChannelHandlerContext ctx, ByteBuf frame) {
        // 运行在 EventLoop 线程 —— 禁止任何阻塞操作！
        int funcCode = frame.getUnsignedByte(7);
        if (funcCode == 0x03) {
            ctx.writeAndFlush(buildReadResponse(frame));  // 沿 Pipeline 反向走到编码器
        }
    }
}
```

- 流向：**入站按 addLast 顺序，出站逆 addLast 顺序**
- 耗时任务正确姿势：`bizExecutor.submit(() -> { ...; ctx.writeAndFlush(resp); })`（writeAndFlush 线程安全）

## 第 5 段：与 Vert.x 对照

![07-08 Vert.x 对照映射]({{ site.baseurl }}/assets/svg/07-08-Vertx对照映射.svg)

| Netty | Vert.x（网关） |
|---|---|
| EventLoopGroup | Vertx 实例（默认都是 2×CPU 核数） |
| EventLoop | Event Loop（底层就是 Netty 的） |
| Channel + Pipeline | NetServer + connectHandler/bodyHandler 回调链 |
| 提交业务线程池 | executeBlocking / Worker Verticle |

- Netty 要自己管线程池与线程安全；Vert.x 用 executeBlocking 封装，回调自动切回事件循环
- "绝不阻塞事件循环"的根源 = Channel 与 EventLoop 终身绑定；Vert.x 阻塞超 2 秒打 Thread blocked 警告就是防这个

## 第 6 段：小结

![07-09 全课主线小结]({{ site.baseurl }}/assets/svg/07-09-全课主线小结.svg)

一条主线：BIO 线程爆炸 → NIO Selector（1 线程盯 N 连接）→ Reactor 逐级拆职责 → Netty EventLoop/Pipeline 落地 → Vert.x 印证同源。

三个核心结论：
1. **瓶颈转移**：从"线程数量"转移到"事件循环不能被阻塞"
2. **终身绑定**：免锁的便利与"一阻塞全冻结"的代价是同一枚硬币两面
3. **职责分离**：accept 单线程 / IO 多线程分摊 / 业务独立线程池

---

## 深挖 A：零拷贝与 ByteBuf

![07-10 ByteBuf 与零拷贝]({{ site.baseurl }}/assets/svg/07-10-ByteBuf与零拷贝.svg)

ByteBuf 对 JDK ByteBuffer 的三个改进：
1. **读写指针分离**（readerIndex / writerIndex）→ 永远不用 flip()
2. **自动扩容**
3. **丰富 API**（readInt / getUnsignedByte，支持大小端）

内存布局：`[0, readerIndex)` 已读废弃区 | `[readerIndex, writerIndex)` 有效数据 | `[writerIndex, capacity)` 可写区

零拷贝五件套（Netty 级 = 减少 JVM 内复制次数，与 OS 级 sendfile 是两层优化）：

| 手段 | 原理 | 网关场景 |
|---|---|---|
| slice() | 建视图共享内存，零复制 | 最常用：从完整帧切 MBAP 头 / PDU |
| CompositeByteBuf | 逻辑组合多个 Buffer | 免去"先合并再处理"的复制 |
| wrap | 包装已有 byte[] | 包装即用 |
| FileRegion | 封装 sendfile | 文件磁盘直达网卡 |
| DirectByteBuf | 堆外内存 | 写网卡省去"堆→内核"一次复制（呼应 03-03） |

```java
ByteBuf mbap = frame.slice(0, 7);   // 视图零复制；不增加引用计数
// 跨线程持有必须 retainedSlice()，否则原 Buffer 释放后视图失效
```

## 深挖 B：粘包拆包手写解码器

![07-11 粘包拆包与手写解码器]({{ site.baseurl }}/assets/svg/07-11-粘包拆包与手写解码器.svg)

- 成因：TCP 是字节流，帧边界进入内核缓冲区后消失。粘包 = Nagle 合并/缓冲区堆积；拆包 = MSS 分片/分批到达
- `ByteToMessageDecoder` 契约：数据不够 → 直接 return（cumulation buffer 保留现场）；够了 → 消费一帧加进 out；框架反复调用直到 in 不再变化（解粘包）

```java
public class ModbusFrameDecoder extends ByteToMessageDecoder {
    private static final int MBAP_FIXED = 6;   // 事务号2+协议号2+长度2
    protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) {
        if (in.readableBytes() < MBAP_FIXED) return;          // ① 长度字段未到齐：等
        int length = in.getUnsignedShort(4);                  // ② get 偷看不移动指针
        int frameLength = MBAP_FIXED + length;                // ③ 长度字段只含单元号+PDU
        if (in.readableBytes() < frameLength) return;         // ④ 半包：等下次 read
        out.add(in.readRetainedSlice(frameLength));           // ⑤ 零拷贝切片+引用计数
    }
}
```

- 手写版价值：可在 ② 之后加协议校验（协议号必须为 0、长度超 253 判脏数据关连接）
- 勘误：第 4 段骨架中 `LengthFieldBasedFrameDecoder` 的 lengthAdjustment 应为 **0** 而非 1

## 加餐：EventLoop 任务队列

![07-12 EventLoop 任务队列]({{ site.baseurl }}/assets/svg/07-12-EventLoop任务队列.svg)

- 定位：**跨线程协作的唯一入口**——其他线程不直接碰 Channel，只投递任务，由 EventLoop 统一执行，保住单线程免锁
- **MPSC 队列**：多生产者（业务线程，CAS 无锁入队）单消费者（EventLoop 独占出队）
- `for(;;)` 三步：select() → 处理 IO 事件 → runAllTasks()，同一线程串行执行
- **ioRatio（默认 50）**：IO 与任务时间各占一半；调高 → 任务跑更久但拖慢 IO；堆积排查用 `pendingTasks()`

```java
channel.eventLoop().execute(() -> channel.writeAndFlush(resp));        // 立即
channel.eventLoop().schedule(() -> channel.writeAndFlush(hb), 5, SECONDS); // 延迟
// writeAndFlush 线程安全的真相：非加锁，而是把操作投递回 EventLoop 线程执行
```

| Netty | Vert.x |
|---|---|
| eventLoop.execute(task) | context.runOnContext(v -> ...) |
| eventLoop.schedule(...) | vertx.setTimer / setPeriodic |

---

## 自检清单

- [ ] BIO 网关"连接多但 CPU 不高"的原因？（线程阻塞挂起 + 上下文切换）
- [ ] NIO 线程阻塞点在哪？（只在 select()，一处）
- [ ] Reactor 三形态各拆掉了什么瓶颈？
- [ ] bossGroup / workerGroup 对应哪个角色？NioEventLoopGroup() 默认线程数？（2×CPU）
- [ ] 为什么 Handler 不用加锁？为什么不能在 channelRead0 阻塞？
- [ ] Inbound / Outbound 流向差异？（入站顺序、出站逆序）
- [ ] ByteBuf 三改进？slice 与 retainedSlice 区别？
- [ ] decode() 数据不够时为什么直接 return 不丢数据？
- [ ] writeAndFlush 线程安全的真正机制？（投递回 EventLoop，非加锁）

## 跨课连接

- **03-03 直接内存与 Netty 池化 → 本课 DirectByteBuf/ByteBuf**：JVM 课伏笔在网络课落地
- **04-01 JMM → 本课线程封闭**：可见性问题靠"终身绑定"的架构决策消除，而非加锁
- **06-03 网关并发模型 → 本课任务队列**：每设备 FIFO+单调度线程 与 EventLoop+MPSC 同构
- **下一站**：L2 Spring 原理（IoC/三级缓存/事务传播），衔接点 = 08-03 条件装配决策流的地基
