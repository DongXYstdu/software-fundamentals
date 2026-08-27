---
title: 并发之 synchronized 与 AQS
date: 2026-08-26 09:00:00 +0800
categories: [Java]
tags: [并发, AQS, 锁]
---

# 并发编程（二）：synchronized 与 AQS
## 1. synchronized 锁升级链

![05-01 synchronized 锁升级链]({{ site.baseurl }}/assets/svg/05-01-synchronized锁升级链.svg)

```
无锁 ──首访──> 偏向锁 ──第二线程──> 轻量级锁 ──自旋失败──> 重量级锁
对象头正常      单线程·存 ThreadID      CAS 自旋         OS 互斥量·阻塞
```

| 状态 | 触发条件 | 实现 | 成本 |
|---|---|---|---|
| 无锁 | 初始状态 | 对象头正常 | 零 |
| 偏向锁 | 单线程首次访问 | 对象头存 ThreadID | 几乎零 |
| 轻量级锁 | 第二个线程来 | CAS 自旋 | 自旋耗 CPU |
| 重量级锁 | 自旋失败/竞争激烈 | OS 互斥量 | 线程阻塞·上下文切换 |

要点：
- **升级不可逆**——一旦升到重量级锁，即使无竞争也是重量级（直到对象被 GC 重建对象头）。"先一窝蜂抢再冷却"的写法持续付出代价
- **JDK 15+ 偏向锁默认关闭**——`-XX:+UseBiasedLocking` 才开；多核高并发下维护偏向锁开销超过它省的
- 实战：低竞争 synchronized 比 ReentrantLock 还轻（JIT 自动选档+无对象创建）；高竞争才换 JUC 锁

## 2. AQS：所有 JUC 锁的通用骨架

![05-02 AQS 同步器框架]({{ site.baseurl }}/assets/svg/05-02-AQS同步器框架.svg)

```
┌──── state（volatile int）────┐
│  同步状态 · CAS 修改           │
│  0=空闲 · >0=占用              │
└──tryAcquire 失败 → 入队阻塞──┘
         │
head → Node → Node → tail   ← FIFO 双向链表
（哨兵）（线程引用+状态）        前驱唤醒后继

┌─ 独占模式 ──┐  ┌─ 共享模式 ───┐
│ReentrantLock│  │Semaphore      │
│写锁          │  │读锁 · 闭锁   │
└─────────────┘  └──────────────┘
```

### AQS 设计精髓
- **模板方法模式**：子类只写 `tryAcquire/tryRelease`（独占）或 `tryAcquireShared/tryReleaseShared`（共享），AQS 管通用的入队、阻塞、唤醒
- **state 复用**：同一个 int 在不同子类里解释不同
- **FIFO 公平唤醒**：前驱节点 release 后唤醒后继，避免线程饥饿（除非非公平锁插队）

### 各锁 state 的含义

| 锁 | state 含义 |
|---|---|
| ReentrantLock | 重入次数（重入 +1，释放 -1） |
| Semaphore | 剩余许可数 |
| CountDownLatch | 倒数计数（减到 0 才放行） |
| ReentrantReadWriteLock | 高 16 位=共享读 / 低 16 位=独占写 |

### 网关 FIFO 的真相
`LinkedBlockingQueue` 的 `put/take` 基于 AQS 的 `ConditionObject`：put 满了挂到 notFull 队列、take 空了挂到 notEmpty 队列——两层条件变量是 `ArrayBlockingQueue` 没有的，高并发下 LBQ 表现更好。

## 3. synchronized vs ReentrantLock 选型

![05-03 synchronized 与 ReentrantLock 选型]({{ site.baseurl }}/assets/svg/05-03-synchronized与ReentrantLock选型.svg)

| 维度 | synchronized | ReentrantLock |
|---|---|---|
| 使用方式 | 关键字·自动释放 | API·必须 finally unlock |
| 公平性 | 非公平（不可选） | 可选公平/非公平 |
| 可中断 | ✗ 不可 | ✓ lockInterruptibly |
| 超时获取 | ✗ 不可 | ✓ tryLock(timeout) |
| 条件变量 | 单 wait/notify | 多个 Condition |
| 异常时释放 | ✓ 自动 | ✗ 漏 unlock 就死锁 |

**选型口诀**：能用 synchronized 就用；要可中断/超时/多条件/公平才换 ReentrantLock。

### 场景对照

| 场景 | 选型 |
|---|---|
| 空压机多步安全控制序列 | ReentrantLock.tryLock(timeout)——避免抢不到锁卡死 |
| 网关 FIFO 队列 | LinkedBlockingQueue（内部 AQS + 双 Condition） |
| 计数器累加 | 都不是——AtomicInteger（CAS） |
| 简单互斥保护 | synchronized 即可，自动释放不会漏 |

**最大坑**：ReentrantLock 用错就是死锁源。`lock()` 后任何路径漏 `finally unlock()`，整个锁永久持有。所以"能用 synchronized 就用"，**确需可中断/超时/多条件/公平才换 ReentrantLock**，且必须 `try-finally`。

## 4. 下一步

- 并发第三课：线程池——ThreadPoolExecutor 七参数、拒绝策略、执行流程、与网关 FIFO 对照
- 讲完 L1 收官
