---
layout: page
title: 分类
icon: fas fa-stream
order: 1
---

{% comment %}
分类体系设计：
1. 入门专区：学习路径入口，展示系统化学习顺序
2. 技术领域分类：按技术领域组织，按 orders 字段排序
3. 面试题：各领域面试题汇总

Front Matter 规范：
- categories: [分类名]
- orders: {分类名: 排序号} （按分类定义排序，数值越小越靠前，默认9999）
- level: 入门/进阶/深入 （可选）
{% endcomment %}

{% assign category_order = "入门,Java,数据库,操作系统,计算机网络,数据结构与算法,系统设计,开发工具,软件工程" | split: "," %}

{% capture zero5 %}00000{% endcapture %}

{% for cat in category_order %}
  {% assign sorted_urls = "" | split: "" %}
  {% for post in site.posts %}
    {% if post.categories contains cat %}
      {% assign post_order = post.orders[cat] | default: 9999 %}
      {% assign padded = zero5 | append: post_order %}
      {% assign padded = padded | slice: -5, 5 %}
      {% assign entry = padded | append: "|||" | append: post.url %}
      {% assign sorted_urls = sorted_urls | push: entry %}
    {% endif %}
  {% endfor %}
  {% assign sorted_urls = sorted_urls | sort %}
  
  {% if sorted_urls.size > 0 %}
<div class="category-section" id="cat-{{ forloop.index }}">
  <div class="category-header" data-level="1">
    <div class="category-title-area">
      <span class="category-icon"></span>
      <h3 class="category-title">{{ cat }}</h3>
      <span class="category-count">{{ sorted_urls.size }} 篇</span>
    </div>
    <span class="category-chevron"><i class="fas fa-chevron-down"></i></span>
  </div>
  
  <div class="category-body" id="cat-body-{{ forloop.index }}">
    <div class="post-list">
      {% for url_entry in sorted_urls %}
        {% assign url_parts = url_entry | split: "|||" %}
        {% assign target_url = url_parts[1] %}
        {% for post in site.posts %}
          {% if post.url == target_url %}
        <a class="post-item" href="{{ post.url | relative_url }}">
          <div class="post-item-content">
            <h5 class="post-title">{{ post.title }}</h5>
            <div class="post-meta">
              <span class="meta-date"><i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
              {% if post.level %}
              <span class="level-badge level-{{ post.level }}">{{ post.level }}</span>
              {% endif %}
            </div>
          </div>
        </a>
          {% endif %}
        {% endfor %}
      {% endfor %}
    </div>
  </div>
</div>
  {% endif %}
{% endfor %}

<script>
document.addEventListener('DOMContentLoaded', function() {
  var categoryHeaders = document.querySelectorAll('.category-header');
  categoryHeaders.forEach(function(header) {
    header.addEventListener('click', function() {
      var section = this.parentElement;
      var body = section.querySelector('.category-body');
      var chevron = section.querySelector('.category-chevron i');
      
      if (body.classList.contains('collapsed')) {
        body.classList.remove('collapsed');
        chevron.style.transform = 'rotate(0deg)';
      } else {
        body.classList.add('collapsed');
        chevron.style.transform = 'rotate(-90deg)';
      }
    });
  });
  
  var firstHeader = document.querySelector('.category-header');
  if (firstHeader) {
    firstHeader.click();
  }
});
</script>

<style>
  .category-section {
    background: #ffffff;
    border: 1px solid #e8eaed;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    overflow: hidden;
    transition: box-shadow 0.25s ease;
  }
  
  .category-section:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
  }
  
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
  
  .category-body {
    max-height: 3000px;
    overflow: hidden;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.3s ease,
                padding 0.3s ease;
    opacity: 1;
    padding: 0.75rem;
  }
  
  .category-body.collapsed {
    max-height: 0;
    opacity: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
  
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
  
  .level-badge {
    font-size: 0.62rem;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-weight: 600;
    white-space: nowrap;
  }
  
  .level-badge.level-入门 {
    background: #dcfce7;
    color: #166534;
  }
  
  .level-badge.level-进阶 {
    background: #fef9c3;
    color: #854d0e;
  }
  
  .level-badge.level-深入 {
    background: #fee2e2;
    color: #991b1b;
  }
  
  @media (prefers-color-scheme: dark) {
    .category-section {
      background: #1e2333;
      border-color: #2d3348;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.15);
    }
    .category-section:hover {
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
    
    .level-badge.level-入门 {
      background: #14532d;
      color: #bbf7d0;
    }
    .level-badge.level-进阶 {
      background: #713f12;
      color: #fef08a;
    }
    .level-badge.level-深入 {
      background: #7f1d1d;
      color: #fecaca;
    }
  }
</style>
