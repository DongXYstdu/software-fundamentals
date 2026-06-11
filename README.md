# software-fundamentals 项目文件结构

## 项目概述

**software-fundamentals** 是一个基于 Jekyll + Chirpy 主题构建的个人技术博客项目，主题为"软件基础——夯实根基，理解本质"。项目通过 GitHub Pages 部署，系统梳理计算机科学与软件工程的基础知识体系。

- **站点地址**：`https://DongXYstdu.github.io/software-fundamentals`
- **作者**：董向阳
- **语言**：中文（zh-CN）
- **主题**：jekyll-theme-chirpy (~> 7.5)

---

## 目录结构总览

```
software-fundamentals/
├── .devcontainer/          # 开发容器配置
├── .github/                # GitHub Actions 工作流
├── .vscode/                # VS Code 编辑器配置
├── _data/                  # Jekyll 数据文件
├── _plugins/               # Jekyll 自定义插件
├── _posts/                 # 博客文章（核心内容）
├── _tabs/                  # 导航栏页面
├── tools/                  # 构建/测试脚本
├── _config.yml             # Jekyll 站点配置
├── index.html              # 首页模板
├── Gemfile                 # Ruby 依赖
├── article-task-list.md    # 文章抓取任务清单
├── scrape.py               # 文章抓取脚本
├── download.ps1            # PowerShell 下载脚本
└── 其他配置文件
```

---

## 各目录与文件详解

### 1. `.devcontainer/` — 开发容器

| 文件 | 说明 |
|------|------|
| `devcontainer.json` | VS Code Dev Container 配置，定义开发环境 |
| `post-create.sh` | 容器创建后的初始化脚本 |

用于在容器中统一开发环境，确保 Jekyll 构建环境一致性。

### 2. `.github/workflows/` — CI/CD

| 文件 | 说明 |
|------|------|
| `pages-deploy.yml` | GitHub Actions 自动部署工作流，构建并发布到 GitHub Pages |

推送代码后自动触发构建和部署。

### 3. `.vscode/` — 编辑器配置

| 文件 | 说明 |
|------|------|
| `extensions.json` | 推荐安装的 VS Code 扩展列表 |
| `settings.json` | 工作区级别的编辑器设置 |
| `tasks.json` | 自定义任务（如本地预览、构建等） |

### 4. `_data/` — Jekyll 数据文件

| 文件 | 说明 |
|------|------|
| `contact.yml` | 侧边栏联系方式配置（GitHub、Email、RSS） |
| `share.yml` | 文章分享按钮配置 |

### 5. `_plugins/` — 自定义插件

| 文件 | 说明 |
|------|------|
| `posts-lastmod-hook.rb` | 自动更新文章 `lastmod` 时间的钩子插件 |

### 6. `_posts/` — 博客文章（核心内容）

这是项目的核心目录，存放所有技术文章。文件命名格式为 `日期-分类-标题.md`，例如：

```
2026-06-10-计算机网络-TCP-三次握手与四次挥手面试题.md
2026-06-18-MySQL-索引失效场景.md
2026-06-19-Java-Java基础面试题.md
```

每篇文章包含 YAML Front Matter：

```yaml
---
title: 文章标题
date: 2026-06-10 09:00:00 +0800
categories: [分类1, 分类2]
tags: [标签1, 标签2, 标签3]
---
```

#### 文章分类体系

| 分类 | 文章数 | 说明 |
|------|--------|------|
| **操作系统** | ~50篇 | 进程线程、内存管理、文件系统、IO模型、锁机制等 |
| **计算机网络** | ~40篇 | TCP/IP、HTTP/HTTPS、DNS、WebSocket、RPC等 |
| **MySQL** | ~40篇 | 索引原理、锁机制、事务隔离、日志系统、架构等 |
| **Redis** | ~20篇 | 数据结构、持久化、集群、分布式锁、缓存问题等 |
| **Java基础** | ~20篇 | String、泛型、反射、序列化、异常、多态等 |
| **Java集合** | ~14篇 | HashMap原理、ConcurrentHashMap、fail-fast等 |
| **MySQL面试** | ~24篇 | InnoDB、索引设计、锁、SQL调优、范式等 |
| **数据结构** | ~15篇 | 链表、栈队列、二叉树、图、堆、哈希表等 |
| **数据库入门** | ~6篇 | 基本概念、三范式、数据库设计实战等 |
| **数据库** | ~6篇 | 事务隔离、索引原理、性能优化、NoSQL等 |
| **算法** | ~4篇 | 动态规划、图算法、排序算法等 |
| **软件工程** | ~4篇 | 性能优化、API设计、测试方法论、代码重构等 |
| **DevOps** | ~2篇 | 容器化与K8s、Git工作流 |
| **安全** | ~2篇 | 认证授权、Web安全攻防 |
| **并发编程** | ~2篇 | 并发模型、锁与同步机制 |
| **系统设计** | ~3篇 | DDD、微服务、高可用架构 |
| **分布式系统** | ~3篇 | 消息队列、分布式事务、CAP理论 |
| **编程语言** | ~2篇 | 垃圾回收、类型系统 |
| **编译原理** | ~1篇 | 从源代码到机器码 |
| **软件设计** | ~1篇 | SOLID原则与设计模式 |
| **面试题汇总** | ~17篇 | 各领域面试题合集（Java/JVM/Spring/MySQL/Redis等） |
| **核心总结** | ~8篇 | 各领域核心知识总结 |
| **基础教程** | ~8篇 | Java/Python/HTML/CSS/JS/Git/Docker/Linux入门 |
| **前端开发** | ~3篇 | HTML/CSS/JavaScript基础教程 |

#### 文章来源

文章主要从以下技术博客抓取和整理：

1. **小林Coding**（xiaolincoding.com）— 图解网络、图解系统、图解MySQL、图解Redis
2. **小哈学Java** — Java基础面试题、Java集合面试题、MySQL面试题
3. **JavaGuide** — Java系列、数据库、系统设计等（计划中）
4. **菜鸟教程** — 编程语言、前端、数据库等基础教程（计划中）

### 7. `_tabs/` — 导航栏页面

| 文件 | 说明 |
|------|------|
| `about.md` | 关于页面 |
| `archives.md` | 归档页面 |
| `categories.md` | 分类页面 |
| `tags.md` | 标签页面 |

这些页面会出现在博客顶部导航栏中。

### 8. `tools/` — 构建脚本

| 文件 | 说明 |
|------|------|
| `run.sh` | 本地启动 Jekyll 服务的脚本 |
| `test.sh` | 本地构建测试脚本 |

### 9. 根目录配置文件

| 文件 | 说明 |
|------|------|
| `_config.yml` | Jekyll 站点核心配置（标题、语言、主题、评论、分页等） |
| `index.html` | 首页模板，包含 Banner 和按分类展示文章的逻辑 |
| `Gemfile` | Ruby 依赖声明（jekyll-theme-chirpy、html-proofer等） |
| `article-task-list.md` | 文章抓取任务清单，记录已完成和待抓取的文章 |
| `scrape.py` | Python 文章抓取脚本，从小林Coding下载并转换为Markdown |
| `download.ps1` | PowerShell 下载脚本 |
| `.gitmodules` | Git 子模块配置（Chirpy 主题） |
| `.gitignore` | Git 忽略规则 |
| `.gitattributes` | Git 属性配置 |
| `.editorconfig` | 编辑器代码风格统一配置 |
| `.nojekyll` | 告知 GitHub Pages 不跳过 Jekyll 处理 |
| `LICENSE` | MIT 开源许可证 |
| `README.md` | 项目说明文档 |

---

## 技术架构

```
┌─────────────────────────────────────────────┐
│              GitHub Pages                    │
│         (自动部署 + CDN)                      │
├─────────────────────────────────────────────┤
│           Jekyll 静态站点生成                  │
│         jekyll-theme-chirpy 7.5              │
├─────────────────────────────────────────────┤
│  _posts/  │  _tabs/  │  _data/  │ index.html │
│  (文章)    │  (页面)   │  (数据)   │  (首页)     │
├─────────────────────────────────────────────┤
│  GitHub Actions (CI/CD)                      │
│  .github/workflows/pages-deploy.yml          │
└─────────────────────────────────────────────┘
```

---

## 内容采集流程

项目通过自动化脚本从优质技术博客抓取文章，流程如下：

1. **定义任务**：在 `article-task-list.md` 中规划待抓取的文章列表
2. **抓取转换**：运行 `scrape.py` 脚本，下载网页 HTML 并转换为 Markdown
3. **格式规范**：自动添加 Front Matter、清理广告和无关内容、添加参考来源
4. **本地预览**：通过 `tools/run.sh` 启动本地 Jekyll 服务预览效果
5. **自动部署**：推送到 GitHub 后，Actions 自动构建并部署到 GitHub Pages

---

## 文章命名与格式规范

### 命名格式

```
YYYY-MM-DD-分类-简短标题.md
```

示例：
- `2026-06-10-计算机网络-TCP-三次握手与四次挥手面试题.md`
- `2026-06-18-MySQL-索引失效场景.md`
- `2026-06-19-Java-Java基础面试题.md`

### Front Matter 格式

```yaml
---
title: 文章标题
date: 2026-06-11 09:00:00 +0800
categories: [分类1, 分类2]
tags: [标签1, 标签2, 标签3]
math: true        # 可选，启用数学公式
mermaid: true     # 可选，启用流程图
---
```

### 文章尾部

```markdown
---
> 参考来源：[原文标题](原文URL)
```