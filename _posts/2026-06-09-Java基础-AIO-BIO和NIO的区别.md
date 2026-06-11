---
title: AIO、BIO NIO 的区别？
date: 2026-06-09 09:00:00 +0800
categories: [Java, 基础]
tags: [Java, 基础, 面试, 小哈学Java]
---
<main><div><p>一则或许对你有用的小广告</p> <p>欢迎 <a href="https://www.quanxiaoha.com/column/"><b>加入小哈的星球</b></a> ，你将获得：专属的实战项目（4个项目都能学） / 1v1 提问 / 简历修改 / Java 学习路线 / 社群讨论 / 学习打卡 / 每月赠书</p> <ul><li><p><b>《Spring AI 项目实战（问答机器人、RAG 智能客服、联网搜索）》</b> 已完结，基于 <code>Spring AI + Spring Boot 3.x + JDK 21...</code>， <a href="https://www.quanxiaoha.com/column/10508.html"><b>查看介绍</b></a></p></li> <li><p><b>《从零手撸：仿小红书（微服务架构）》</b> 已完结，基于 <code>Spring Cloud Alibaba + Spring Boot 3.x + JDK 17...</code>， <a href="https://www.quanxiaoha.com/column/10247.html"><b>查看介绍</b></a> ；演示链接： <a href="http://116.62.199.48:7070/"><b>http://116.62.199.48:7070/</b></a></p></li> <li><p><b>《从零手撸：前后端分离博客项目（全栈开发）》</b> 2 期已完结，演示链接： <a href="http://116.62.199.48/"><b>http://116.62.199.48/</b></a></p></li> <li><p>新开坑项目： <b>《从零手撸：秒杀系统高并发优化实战》</b> 正在更新中...， <a href="https://www.quanxiaoha.com/column/10659.html"><b>查看介绍</b></a></p></li></ul> <p>截止目前， <a href="https://www.quanxiaoha.com/column/">星球</a> 内专栏 <b>累计输出 150w+ 字，讲解图 5110+ 张，还在持续爆肝中.. 后续还会上新更多项目，已有 4700+ 小伙伴加入学习</b> ，欢迎 <a href="https://www.quanxiaoha.com/column/"><b>点击围观</b></a></p></div> <div><H2>面试考察点</H2> <ol> <li> <p><strong>IO 模型理解深度</strong> ：面试官不仅仅是想知道 "BIO 阻塞、NIO 非阻塞" 这种浅层答案，更是想考察你是否理解同步/异步、阻塞/非阻塞的本质区别，以及三种 IO 模型在操作系统层面的实现原理。</p> </li> <li> <p><strong>架构设计能力</strong> ：考察你是否清楚不同 IO 模型的适用场景，能否根据业务特点（连接数、数据量、实时性）选择合适的模型，理解 Netty、Tomcat 等框架为何选择 NIO。</p> </li> <li> <p><strong>实践经验</strong> ：看你是否在实际项目中使用过 NIO/AIO，是否了解 Reactor 模式、Proactor 模式，以及如何解决 IO 模型带来的性能瓶颈。</p> </li> </ol> <H2>核心答案</H2> <p>BIO、NIO、AIO 是 Java 的三种 IO 模型，核心区别在于 <strong>阻塞方式</strong> 和 <strong>线程模型</strong> ：</p> <table> <thead> <tr> <th>对比维度</th> <th>BIO</th> <th>NIO</th> <th>AIO</th> </tr> </thead> <tbody> <tr> <td><strong>全称</strong></td> <td>Blocking I/O</td> <td>Non-blocking I/O</td> <td>Asynchronous I/O</td> </tr> <tr> <td><strong>中文名</strong></td> <td>同步阻塞 IO</td> <td>同步非阻塞 IO</td> <td>异步非阻塞 IO</td> </tr> <tr> <td><strong>阻塞特性</strong></td> <td>阻塞</td> <td>非阻塞</td> <td>非阻塞</td> </tr> <tr> <td><strong>同步/异步</strong></td> <td>同步</td> <td>同步</td> <td><strong>异步</strong></td> </tr> <tr> <td><strong>线程模型</strong></td> <td>一连接一线程</td> <td>多路复用（Selector）</td> <td>回调机制</td> </tr> <tr> <td><strong>连接数限制</strong></td> <td>低（受线程数限制）</td> <td>高（单线程管理多连接）</td> <td>高</td> </tr> <tr> <td><strong>编程复杂度</strong></td> <td>简单</td> <td>复杂（需理解 Selector）</td> <td>较复杂（回调模式）</td> </tr> <tr> <td><strong>JDK 版本</strong></td> <td>JDK 1.0+</td> <td>JDK 1.4+</td> <td>JDK 1.7+</td> </tr> <tr> <td><strong>适用场景</strong></td> <td>连接数少且固定</td> <td>连接数多、连接时间短</td> <td>连接数多、连接时间长</td> </tr> <tr> <td><strong>典型应用</strong></td> <td>传统 Socket</td> <td>Netty、Tomcat NIO</td> <td>Windows 完成端口</td> </tr> </tbody> </table> <p><strong>一句话概括</strong> ：BIO 是 "一个服务员服务一桌"，NIO 是 "一个服务员服务多桌（轮询）"，AIO 是 "顾客自己点餐，做好了叫号"。</p> <H2>深度解析</H2> <H3>一、BIO：同步阻塞 IO</H3> <p>BIO 是最传统的 IO 模型， <strong>一个连接对应一个线程</strong> ，读写操作会阻塞当前线程。</p>   <p>上图展示了 BIO 的工作模型，核心特点：</p> <ul> <li><strong>一连接一线程</strong> ：每个客户端连接都会创建一个独立的线程处理</li> <li><strong>阻塞等待</strong> ：线程在执行 <code>read()</code> 、 <code>accept()</code> 时会阻塞，直到有数据可读或有新连接</li> <li><strong>资源浪费</strong> ：大量线程处于阻塞状态，白白占用内存和 CPU</li> </ul> <p><strong>BIO 的问题</strong> ：</p> <ul> <li><strong>线程资源消耗</strong> ：10000 个连接需要 10000 个线程，每个线程约 1MB 栈空间</li> <li><strong>上下文切换开销</strong> ：大量线程频繁切换，CPU 消耗严重</li> <li><strong>无法应对高并发</strong> ：线程数受操作系统限制</li> </ul> <pre><code class="language-java" data-lang="java">// BIO 服务端示例
public class BioServer {
    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = new ServerSocket(8080);
        System.out.println("服务器启动...");

        while (true) {
            // 阻塞等待客户端连接
            Socket socket = serverSocket.accept();  // 阻塞点 1
            System.out.println("客户端连接：" + socket.getRemoteSocketAddress());

            // 为每个连接创建新线程处理
            new Thread(() -&gt; {
                try {
                    InputStream is = socket.getInputStream();
                    byte[] buffer = new byte[1024];
                    while (true) {
                        // 阻塞等待读取数据
                        int len = is.read(buffer);  // 阻塞点 2
                        if (len == -1) break;
                        System.out.println("收到数据：" + new String(buffer, 0, len));
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}</code></pre> <H3>二、NIO：同步非阻塞 IO</H3> <p>NIO 引入了 <strong>多路复用器（Selector）</strong> ，一个线程可以管理多个连接，通过轮询检查哪些连接有数据可读。</p>   <p>上图展示了 NIO 的核心组件和工作流程：</p> <ul> <li><strong>Channel（通道）</strong> ：双向的，可以同时读写（BIO 的 Stream 是单向的）</li> <li><strong>Buffer（缓冲区）</strong> ：数据读写都通过缓冲区，不是直接操作流</li> <li><strong>Selector（选择器）</strong> ：多路复用器，轮询检测多个 Channel 的就绪状态</li> </ul> <p><strong>NIO 的核心流程</strong> ：</p> <ol> <li><strong>注册</strong> ：所有 Channel 注册到 Selector 上</li> <li><strong>轮询</strong> ：Selector 轮询检查哪些 Channel 有事件（连接、读、写）</li> <li><strong>处理</strong> ：有事件的 Channel 才会被处理，没有事件的 Channel 不消耗资源</li> </ol> <pre><code class="language-java" data-lang="java">// NIO 服务端示例
public class NioServer {
    public static void main(String[] args) throws IOException {
        // 创建 Selector
        Selector selector = Selector.open();

        // 创建 ServerSocketChannel
        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        serverChannel.configureBlocking(false);  // 设置为非阻塞
        serverChannel.bind(new InetSocketAddress(8080));

        // 将 ServerSocketChannel 注册到 Selector，监听 ACCEPT 事件
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);

        System.out.println("NIO 服务器启动...");

        while (true) {
            // 阻塞等待至少有一个 Channel 就绪（可设置超时）
            selector.select();

            // 获取所有就绪的 SelectionKey
            Set&lt;SelectionKey&gt; selectedKeys = selector.selectedKeys();
            Iterator&lt;SelectionKey&gt; iterator = selectedKeys.iterator();

            while (iterator.hasNext()) {
                SelectionKey key = iterator.next();
                iterator.remove();

                if (key.isAcceptable()) {
                    // 处理新连接
                    ServerSocketChannel server = (ServerSocketChannel) key.channel();
                    SocketChannel client = server.accept();
                    client.configureBlocking(false);
                    client.register(selector, SelectionKey.OP_READ);
                    System.out.println("客户端连接：" + client.getRemoteAddress());

                } else if (key.isReadable()) {
                    // 处理读事件
                    SocketChannel client = (SocketChannel) key.channel();
                    ByteBuffer buffer = ByteBuffer.allocate(1024);
                    int len = client.read(buffer);
                    if (len &gt; 0) {
                        buffer.flip();
                        System.out.println("收到数据：" + new String(buffer.array(), 0, len));
                    } else if (len == -1) {
                        client.close();
                    }
                }
            }
        }
    }
}</code></pre> <H3>三、AIO：异步非阻塞 IO</H3> <p>AIO 是真正的 <strong>异步 IO</strong> ，由操作系统完成读写操作后 <strong>回调</strong> 应用程序，应用程序不需要轮询。</p>   <p>上图展示了 AIO 的工作原理，核心特点：</p> <ul> <li><strong>真正的异步</strong> ：读写操作由操作系统内核完成，应用程序只负责发起请求和处理结果</li> <li><strong>回调机制</strong> ：操作完成后，操作系统通过回调通知应用程序</li> <li><strong>Proactor 模式</strong> ：与 NIO 的 Reactor 模式不同，AIO 是 "完成通知" 而非 "就绪通知"</li> </ul> <p><strong>AIO vs NIO 的本质区别</strong> ：</p> <ul> <li><strong>NIO</strong> ：操作系统通知 "数据准备好了，你可以来读了" → 应用程序自己读</li> <li><strong>AIO</strong> ：操作系统通知 "数据已经读好了，放在这里了" → 应用程序直接用</li> </ul> <pre><code class="language-java" data-lang="java">// AIO 服务端示例
public class AioServer {
    public static void main(String[] args) throws IOException, InterruptedException {
        AsynchronousServerSocketChannel serverChannel =
            AsynchronousServerSocketChannel.open().bind(new InetSocketAddress(8080));

        System.out.println("AIO 服务器启动...");

        // 异步接受连接
        serverChannel.accept(null, new CompletionHandler&lt;AsynchronousSocketChannel, Void&gt;() {
            @Override
            public void completed(AsynchronousSocketChannel client, Void attachment) {
                // 继续接受下一个连接
                serverChannel.accept(null, this);

                // 读取客户端数据
                ByteBuffer buffer = ByteBuffer.allocate(1024);
                client.read(buffer, buffer, new CompletionHandler&lt;Integer, ByteBuffer&gt;() {
                    @Override
                    public void completed(Integer result, ByteBuffer attachment) {
                        if (result == -1) {
                            try {
                                client.close();
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                            return;
                        }
                        attachment.flip();
                        System.out.println("收到数据：" + new String(attachment.array(), 0, result));

                        // 继续读取下一段数据
                        attachment.clear();
                        client.read(attachment, attachment, this);
                    }

                    @Override
                    public void failed(Throwable exc, ByteBuffer attachment) {
                        exc.printStackTrace();
                    }
                });
            }

            @Override
            public void failed(Throwable exc, Void attachment) {
                exc.printStackTrace();
            }
        });

        // 主线程可以继续做其他事
        Thread.sleep(Long.MAX_VALUE);
    }
}</code></pre> <H3>四、三种模型全面对比</H3> <table> <thead> <tr> <th>对比维度</th> <th>BIO</th> <th>NIO</th> <th>AIO</th> </tr> </thead> <tbody> <tr> <td><strong>IO 方式</strong></td> <td>阻塞</td> <td>非阻塞</td> <td>非阻塞</td> </tr> <tr> <td><strong>同步/异步</strong></td> <td>同步</td> <td>同步</td> <td>异步</td> </tr> <tr> <td><strong>核心组件</strong></td> <td>Socket、ServerSocket</td> <td>Channel、Buffer、Selector</td> <td>AsynchronousChannel、CompletionHandler</td> </tr> <tr> <td><strong>编程难度</strong></td> <td>⭐ 简单</td> <td>⭐⭐⭐ 复杂</td> <td>⭐⭐ 中等</td> </tr> <tr> <td><strong>连接数支持</strong></td> <td>低（受线程限制）</td> <td>高（单线程管理多连接）</td> <td>高</td> </tr> <tr> <td><strong>CPU 利用率</strong></td> <td>低（线程阻塞）</td> <td>高（轮询）</td> <td>高（回调）</td> </tr> <tr> <td><strong>操作系统依赖</strong></td> <td>无</td> <td>Linux epoll / Windows IOCP</td> <td>Windows IOCP 支持更好</td> </tr> <tr> <td><strong>生产使用</strong></td> <td>传统应用</td> <td><strong>主流</strong> （Netty、Tomcat）</td> <td>较少</td> </tr> </tbody> </table> <H3>五、为什么主流框架选择 NIO 而不是 AIO？</H3> <p>虽然 AIO 理论上更先进，但实际生产中 <strong>NIO 更受欢迎</strong> ：</p> <table> <thead> <tr> <th>原因</th> <th>说明</th> </tr> </thead> <tbody> <tr> <td><strong>Linux AIO 支持不完善</strong></td> <td>Linux 的 AIO 实现有限制，很多场景退化成 NIO</td> </tr> <tr> <td><strong>Netty 已优化 NIO</strong></td> <td>Netty 对 NIO 做了大量优化，性能已经足够好</td> </tr> <tr> <td><strong>调试难度</strong></td> <td>AIO 的回调模式调试困难，问题排查成本高</td> </tr> <tr> <td><strong>生态成熟度</strong></td> <td>NIO 生态更成熟，资料和解决方案更多</td> </tr> <tr> <td><strong>Windows vs Linux 差异</strong></td> <td>AIO 在不同操作系统表现不一致</td> </tr> </tbody> </table> <p><strong>Netty 的选择</strong> ：Netty 早期支持 AIO，但后来移除了，原因是 Linux 下 AIO 性能没有优势。</p> <H2>面试高频追问</H2> <ol> <li> <p><strong>NIO 的 Selector 是怎么实现的？</strong> Linux 下使用 epoll，Windows 下使用 IOCP，macOS 下使用 kqueue。epoll 使用事件驱动，比传统的 select/poll 效率更高。</p> </li> <li> <p><strong>为什么 Netty 使用 NIO 而不是 AIO？</strong> Linux 的 AIO 实现不完善，且 Netty 对 NIO 的优化已经足够好，AIO 的回调模式调试困难。</p> </li> <li> <p><strong>NIO 的 Buffer 有什么作用？</strong> Buffer 是 NIO 读写数据的中转站，所有数据都通过 Buffer 读写。核心属性：capacity（容量）、position（当前位置）、limit（限制）。</p> </li> <li> <p><strong>什么是 Reactor 模式？</strong> Reactor 模式是 NIO 的核心设计模式，包含单 Reactor 单线程、单 Reactor 多线程、主从 Reactor 多线程三种实现。Netty 使用的是主从 Reactor 模式。</p> </li> </ol> <H2>常见面试变体</H2> <ul> <li>"同步和异步、阻塞和非阻塞的区别是什么？"</li> <li>"Netty 为什么这么快？"</li> <li>"Tomcat 支持哪些 IO 模型？默认用哪个？"</li> <li>"NIO 的 Selector 在 Linux 下使用什么系统调用？"</li> </ul> <H2>记忆口诀</H2> <p><strong>BIO</strong> ：一连接一线程，阻塞等到天荒地老</p> <p><strong>NIO</strong> ：一个选择器管多连接，轮询检测谁就绪</p> <p><strong>AIO</strong> ：操作系统全包办，做完回调告诉你</p> <p><strong>选型</strong> ：连接少用 BIO，连接多用 NIO，AIO 理论好实战少</p> <H2>总结</H2> <p>BIO 是同步阻塞 IO，一连接一线程，适合连接数少且固定的场景；NIO 是同步非阻塞 IO，使用 Selector 多路复用，一个线程管理多个连接，是高并发场景的主流选择；AIO 是异步非阻塞 IO，操作系统完成 IO 后回调通知，理论上最先进但 Linux 支持不完善。 <strong>生产环境推荐使用 NIO</strong> （如 Netty），BIO 用于简单场景，AIO 在 Windows 环境下可以考虑。</p> </div></main>