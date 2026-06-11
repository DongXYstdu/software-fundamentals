---
layout: page
title: 分类
icon: fas fa-stream
order: 1
---

<!-- 收集所有分类（第一级分类） -->
{% assign all_categories = "" | split: "" %}
{% for post in site.posts %}
  {% if post.categories.size > 0 %}
    {% assign first_cat = post.categories | first %}
    {% unless all_categories contains first_cat %}
      {% assign all_categories = all_categories | push: first_cat %}
    {% endunless %}
  {% endif %}
{% endfor %}

<!-- 分类页可折叠区块 -->
{% for category in all_categories %}
  {% assign cat_posts = "" | split: "" %}
  {% for post in site.posts %}
    {% if post.categories contains category %}
      {% assign cat_posts = cat_posts | push: post %}
    {% endif %}
  {% endfor %}

  {% if cat_posts.size > 0 %}

<div class="category-accordion" id="cat-{{ forloop.index }}">
  <div class="category-header">
    <div class="category-title-area">
      <span class="category-icon" id="cat-icon-{{ forloop.index }}"></span>
      <h3 class="category-title">{{ category }}</h3>
      <span class="category-count">{{ cat_posts.size }} 篇</span>
    </div>
    <span class="category-chevron"><i class="fas fa-chevron-down"></i></span>
  </div>
  <div class="category-body" id="cat-body-{{ forloop.index }}">
    <div class="post-list">
      {% for post in cat_posts %}
      <a class="post-item" href="{{ post.url | relative_url }}">
        <div class="post-item-content">
          <h4 class="post-title">{{ post.title }}</h4>
          <div class="post-meta">
            <span class="meta-date"><i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
            {% if post.categories.size > 1 %}
            <span class="meta-tags">
              {% for c in post.categories offset:1 %}
              <span class="tag">{{ c }}</span>{% unless forloop.last %}{% endunless %}
              {% endfor %}
            </span>
            {% endif %}
          </div>
        </div>
      </a>
      {% endfor %}
    </div>
  </div>
</div>

  {% endif %}
{% endfor %}

<script>
document.addEventListener('DOMContentLoaded', function() {
  var headers = document.querySelectorAll('.category-header');
  headers.forEach(function(header) {
    header.addEventListener('click', function(e) {
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

  /* 分类标题栏 - 可点击 */
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

  /* 分类内容区 - 可折叠 */
  .category-body {
    max-height: 2000px;
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

  /* 文章列表 */
  .post-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .post-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 0.85rem;
    border-radius: 10px;
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
    font-size: 0.9rem;
    font-weight: 600;
    color: #2d3748;
    margin: 0 0 0.3rem 0;
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
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .meta-date {
    font-size: 0.75rem;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }

  .meta-tags {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .tag {
    font-size: 0.62rem;
    color: #6b7280;
    background: #e9ecf2;
    padding: 0.08rem 0.3rem;
    border-radius: 4px;
    font-weight: 500;
    line-height: 1.3;
  }

  .post-arrow {
    color: #c0c7d2;
    font-size: 0.7rem;
    margin-left: 0.6rem;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }

  .post-item:hover .post-arrow {
    color: #4a6cf7;
    transform: translateX(3px);
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
    .post-arrow {
      color: #4b5563;
    }
    .post-item:hover .post-arrow {
      color: #818cf8;
    }
  }
</style>
