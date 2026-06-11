---
layout: page
title: 分类
icon: fas fa-stream
order: 1
---

{% assign category_hierarchy = {
  "入门": ["数据库入门", "数据结构入门"],
  "数据库": ["MySQL", "Redis"],
  "Java": ["Java基础", "Java集合"],
  "操作系统": [],
  "计算机网络": [],
  "数据结构": [],
  "算法": [],
  "软件工程": [],
  "DevOps": [],
  "安全": [],
  "并发编程": [],
  "系统设计": [],
  "分布式系统": [],
  "编程语言": [],
  "编译原理": [],
  "软件设计": [],
  "面试题汇总": [],
  "核心总结": [],
  "基础教程": [],
  "前端开发": []
} %}

{% assign top_level_cats = "入门,数据库,Java,操作系统,计算机网络,数据结构,算法,软件工程,DevOps,安全,并发编程,系统设计,分布式系统,编程语言,编译原理,软件设计,面试题汇总,核心总结,基础教程,前端开发" | split: "," %}

{% for top_cat in top_level_cats %}
  {% assign sub_cats = category_hierarchy[top_cat] %}
  {% assign has_subcats = false %}
  {% if sub_cats.size > 0 %}
    {% assign has_subcats = true %}
  {% endif %}

  {% assign direct_posts = "" | split: "" %}
  {% for post in site.posts %}
    {% if post.categories contains top_cat %}
      {% assign has_subcat = false %}
      {% for sub_cat in sub_cats %}
        {% if post.categories contains sub_cat %}
          {% assign has_subcat = true %}
          {% break %}
        {% endif %}
      {% endfor %}
      {% unless has_subcat %}
        {% assign direct_posts = direct_posts | push: post %}
      {% endunless %}
    {% endif %}
  {% endfor %}

  {% assign total_posts = direct_posts.size %}
  {% for sub_cat in sub_cats %}
    {% for post in site.posts %}
      {% if post.categories contains sub_cat %}
        {% assign total_posts = total_posts | plus: 1 %}
      {% endif %}
    {% endfor %}
  {% endfor %}

  {% if total_posts > 0 %}
<div class="category-accordion" id="cat-{{ forloop.index }}">
  <div class="category-header" data-level="1">
    <div class="category-title-area">
      <span class="category-icon" id="cat-icon-{{ forloop.index }}"></span>
      <h3 class="category-title">{{ top_cat }}</h3>
      <span class="category-count">{{ total_posts }} 篇</span>
    </div>
    {% if has_subcats or direct_posts.size > 0 %}
    <span class="category-chevron"><i class="fas fa-chevron-down"></i></span>
    {% endif %}
  </div>
  
  {% if has_subcats or direct_posts.size > 0 %}
  <div class="category-body" id="cat-body-{{ forloop.index }}">
    {% if has_subcats %}
    <div class="sub-category-list">
      {% for sub_cat in sub_cats %}
        {% assign sub_posts = "" | split: "" %}
        {% for post in site.posts %}
          {% if post.categories contains sub_cat %}
            {% assign sub_posts = sub_posts | push: post %}
          {% endif %}
        {% endfor %}
        
        {% if sub_posts.size > 0 %}
        <div class="sub-category-block" id="sub-cat-{{ forloop.parentloop.index }}-{{ forloop.index }}">
          <div class="sub-category-header" data-level="2">
            <div class="sub-category-title-area">
              <span class="sub-category-icon"></span>
              <h4 class="sub-category-title">{{ sub_cat }}</h4>
              <span class="sub-category-count">{{ sub_posts.size }} 篇</span>
            </div>
            <span class="sub-category-chevron"><i class="fas fa-chevron-right"></i></span>
          </div>
          <div class="sub-category-body" id="sub-cat-body-{{ forloop.parentloop.index }}-{{ forloop.index }}">
            <div class="post-list">
              {% for post in sub_posts %}
              <a class="post-item" href="{{ post.url | relative_url }}">
                <div class="post-item-content">
                  <h5 class="post-title">{{ post.title }}</h5>
                  <div class="post-meta">
                    <span class="meta-date"><i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
                  </div>
                </div>
              </a>
              {% endfor %}
            </div>
          </div>
        </div>
        {% endif %}
      {% endfor %}
    </div>
    {% endif %}

    {% if direct_posts.size > 0 %}
    <div class="direct-posts">
      <div class="section-header">
        <span class="section-title">{{ top_cat }}（{{ direct_posts.size }} 篇）</span>
      </div>
      <div class="post-list">
        {% for post in direct_posts %}
        <a class="post-item" href="{{ post.url | relative_url }}">
          <div class="post-item-content">
            <h5 class="post-title">{{ post.title }}</h5>
            <div class="post-meta">
              <span class="meta-date"><i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
            </div>
          </div>
        </a>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>
  {% endif %}
</div>
  {% endif %}
{% endfor %}

<script>
document.addEventListener('DOMContentLoaded', function() {
  var categoryHeaders = document.querySelectorAll('.category-header');
  categoryHeaders.forEach(function(header) {
    header.addEventListener('click', function(e) {
      if (!e.target.closest('.sub-category-header')) {
        var accordion = this.parentElement;
        var body = accordion.querySelector('.category-body');
        var chevron = accordion.querySelector('.category-chevron i');

        if (body.classList.contains('collapsed')) {
          body.classList.remove('collapsed');
          chevron.style.transform = 'rotate(0deg)';
        } else {
          body.classList.add('collapsed');
          chevron.style.transform = 'rotate(-90deg)';
        }
      }
    });
  });

  var subCategoryHeaders = document.querySelectorAll('.sub-category-header');
  subCategoryHeaders.forEach(function(header) {
    header.addEventListener('click', function(e) {
      e.stopPropagation();
      var subBlock = this.parentElement;
      var body = subBlock.querySelector('.sub-category-body');
      var chevron = subBlock.querySelector('.sub-category-chevron i');

      if (body.classList.contains('collapsed')) {
        body.classList.remove('collapsed');
        chevron.style.transform = 'rotate(90deg)';
      } else {
        body.classList.add('collapsed');
        chevron.style.transform = 'rotate(0deg)';
      }
    });
  });
});
</script>

<style>
  /* ===== 分类页样式 ===== */

  /* 分类区块 - 圆角方框 */
  .category-accordion {
    background: #ffffff;
    border: 1px solid #e8eaed;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    overflow: hidden;
    transition: box-shadow 0.25s ease;
  }

  .category-accordion:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
  }

  /* 一级分类标题栏 - 可点击 */
  .category-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s ease;
    border-bottom: 1px solid #f0f0f0;
  }

  .category-header:hover {
    background: #f5f6f8;
  }

  .category-title-area {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex: 1;
    min-width: 0;
  }

  .category-icon {
    font-size: 1rem;
    color: #4a6cf7;
    font-weight: bold;
    width: 24px;
    text-align: center;
    transition: transform 0.3s ease;
  }

  .category-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0;
    white-space: nowrap;
  }

  .category-count {
    font-size: 0.78rem;
    color: #94a3b8;
    background: #f0f2f7;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-weight: 500;
    white-space: nowrap;
  }

  .category-chevron {
    color: #c0c7d2;
    font-size: 0.8rem;
    transition: transform 0.3s ease;
    flex-shrink: 0;
    margin-left: 0.75rem;
  }

  /* 一级分类内容区 - 可折叠 */
  .category-body {
    max-height: 2000px;
    overflow: hidden;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.3s ease,
                padding 0.3s ease;
    opacity: 1;
    padding: 0.5rem 0.75rem 0.75rem;
  }

  .category-body.collapsed {
    max-height: 0;
    opacity: 0;
    padding-top: 0;
    padding-bottom: 0;
  }

  /* 子分类列表 */
  .sub-category-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  /* 子分类区块 */
  .sub-category-block {
    background: #f8f9fb;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e8eaed;
  }

  /* 子分类标题栏 */
  .sub-category-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s ease;
  }

  .sub-category-header:hover {
    background: #f0f1f4;
  }

  .sub-category-title-area {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    min-width: 0;
  }

  .sub-category-icon {
    font-size: 0.85rem;
    color: #6366f1;
    font-weight: bold;
    width: 20px;
    text-align: center;
  }

  .sub-category-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #334155;
    margin: 0;
    white-space: nowrap;
  }

  .sub-category-count {
    font-size: 0.72rem;
    color: #94a3b8;
    background: #e9ecf2;
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-weight: 500;
    white-space: nowrap;
  }

  .sub-category-chevron {
    color: #94a3b8;
    font-size: 0.7rem;
    transition: transform 0.3s ease;
    flex-shrink: 0;
    margin-left: 0.5rem;
  }

  /* 子分类内容区 - 可折叠 */
  .sub-category-body {
    max-height: 1500px;
    overflow: hidden;
    transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.25s ease,
                padding 0.25s ease;
    opacity: 1;
    padding: 0.5rem 0.75rem;
    border-top: 1px solid #e8eaed;
    background: #ffffff;
  }

  .sub-category-body.collapsed {
    max-height: 0;
    opacity: 0;
    padding-top: 0;
    padding-bottom: 0;
    border-top: none;
  }

  /* 直接文章区域 */
  .direct-posts {
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px dashed #e8eaed;
  }

  .direct-posts .section-header {
    margin-bottom: 0.5rem;
  }

  .direct-posts .section-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #64748b;
  }

  /* 文章列表 */
  .post-list {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .post-item {
    display: flex;
    align-items: center;
    padding: 0.65rem 0.75rem;
    border-radius: 8px;
    background: #f8f9fb;
    border: 1px solid transparent;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s ease;
  }

  .post-item:hover {
    background: #eef1f7;
    border-color: #d0d7e2;
    transform: translateX(4px);
  }

  .post-item-content {
    flex: 1;
    min-width: 0;
  }

  .post-title {
    font-size: 0.86rem;
    font-weight: 600;
    color: #2d3748;
    margin: 0 0 0.25rem 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .post-item:hover .post-title {
    color: #4a6cf7;
  }

  .post-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex-wrap: wrap;
  }

  .meta-date {
    font-size: 0.7rem;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .meta-tags {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
  }

  .tag {
    font-size: 0.6rem;
    color: #6b7280;
    background: #e9ecf2;
    padding: 0.06rem 0.28rem;
    border-radius: 4px;
    font-weight: 500;
    line-height: 1.3;
  }

  /* 暗色模式 */
  @media (prefers-color-scheme: dark) {
    .category-accordion {
      background: #1e2333;
      border-color: #2d3348;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.15);
    }
    .category-accordion:hover {
      box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 8px 24px rgba(0,0,0,0.2);
    }
    .category-header {
      border-bottom-color: #2d3348;
    }
    .category-header:hover {
      background: #252b3d;
    }
    .category-title {
      color: #e2e8f0;
    }
    .category-count {
      color: #94a3b8;
      background: #2d3348;
    }
    .category-icon {
      color: #818cf8;
    }
    .category-chevron {
      color: #4b5563;
    }

    .sub-category-block {
      background: #252b3d;
      border-color: #2d3348;
    }
    .sub-category-header:hover {
      background: #2d3550;
    }
    .sub-category-title {
      color: #cbd5e1;
    }
    .sub-category-count {
      color: #94a3b8;
      background: #2d3348;
    }
    .sub-category-icon {
      color: #a5b4fc;
    }
    .sub-category-chevron {
      color: #6b7280;
    }
    .sub-category-body {
      background: #1e2333;
      border-top-color: #2d3348;
    }

    .direct-posts {
      border-top-color: #2d3348;
    }
    .direct-posts .section-title {
      color: #94a3b8;
    }

    .post-item {
      background: #252b3d;
    }
    .post-item:hover {
      background: #2d3550;
      border-color: #3d4663;
    }
    .post-title {
      color: #cbd5e1;
    }
    .post-item:hover .post-title {
      color: #818cf8;
    }
    .meta-date {
      color: #6b7280;
    }
    .tag {
      color: #9ca3af;
      background: #2d3348;
    }
  }
</style>
