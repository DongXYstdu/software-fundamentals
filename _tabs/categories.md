---
layout: page
title: 分类
icon: fas fa-stream
order: 1
---

<!-- 自定义分类排序：数据库和数据结构置顶 -->

{% assign pinned_cats = "数据库, 数据结构" | split: ", " %}
{% assign all_categories = "" | split: "" %}

<!-- 收集所有分类（第一级分类） -->
{% for post in site.posts %}
  {% if post.categories.size > 0 %}
    {% assign first_cat = post.categories | first %}
    {% unless all_categories contains first_cat %}
      {% assign all_categories = all_categories | push: first_cat %}
    {% endunless %}
  {% endif %}
{% endfor %}

<!-- 构建排序后的分类列表：置顶分类先 -->
{% assign sorted_categories = "" | split: "" %}
{% for pc in pinned_cats %}
  {% if all_categories contains pc %}
    {% assign sorted_categories = sorted_categories | push: pc %}
  {% endif %}
{% endfor %}
{% for c in all_categories %}
  {% unless sorted_categories contains c %}
    {% assign sorted_categories = sorted_categories | push: c %}
  {% endunless %}
{% endfor %}

<!-- 遍历每个分类 -->
{% for category in sorted_categories %}
  {% assign cat_posts = "" | split: "" %}
  {% for post in site.posts %}
    {% if post.categories contains category %}
      {% assign cat_posts = cat_posts | push: post %}
    {% endif %}
  {% endfor %}

  {% if cat_posts.size > 0 %}

    {% if pinned_cats contains category %}
<h3 class="section-title"> 置顶 · {{ category }}（{{ cat_posts.size }} 篇）</h3>
    {% else %}
<h3 class="section-title">{{ category }}（{{ cat_posts.size }} 篇）</h3>
    {% endif %}

<ul class="custom-post-list">
  {% for post in cat_posts %}
  <li class="post-card">
    <div class="post-card-content">
      <a class="post-card-link" href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <div class="post-card-meta">
        <span class="post-date"><i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
        {% if post.categories.size > 1 %}
          <span class="post-categories">
            <i class="far fa-folder"></i>
            {% for c in post.categories %}
              <a href="{{ '/categories/' | append: c | relative_url }}">{{ c }}</a>{% unless forloop.last %}, {% endunless %}
            {% endfor %}
          </span>
        {% endif %}
      </div>
    </div>
    <div class="post-card-arrow">
      <i class="fas fa-chevron-right"></i>
    </div>
  </li>
  {% endfor %}
</ul>

  {% endif %}
{% endfor %}

<style>
  .section-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--heading-color, #333);
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border-color, #e5e7eb);
  }

  .custom-post-list {
    list-style: none;
    padding: 0;
    margin: 0 0 2rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .post-card {
    display: flex;
    align-items: center;
    padding: 1rem 1.2rem;
    border-radius: 0.8rem;
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--border-color, #e5e7eb);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    cursor: pointer;
    text-decoration: none;
    color: inherit;
  }

  .post-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: var(--link-color, #4a90d9);
  }

  .post-card-content {
    flex: 1;
    min-width: 0;
  }

  .post-card-link {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--link-color, #4a90d9);
    text-decoration: none;
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .post-card-link:hover {
    text-decoration: underline;
  }

  .post-card-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: var(--text-muted, #888);
    flex-wrap: wrap;
  }

  .post-card-meta i {
    margin-right: 0.3rem;
  }

  .post-card-meta a {
    color: var(--text-muted, #888);
    text-decoration: none;
  }

  .post-card-meta a:hover {
    color: var(--link-color, #4a90d9);
    text-decoration: underline;
  }

  .post-card-arrow {
    color: var(--text-muted, #ccc);
    font-size: 0.8rem;
    margin-left: 0.8rem;
    transition: color 0.2s ease, transform 0.2s ease;
  }

  .post-card:hover .post-card-arrow {
    color: var(--link-color, #4a90d9);
    transform: translateX(4px);
  }

  @media (prefers-color-scheme: dark) {
    .post-card {
      background: #1f2937;
      border-color: #374151;
    }
    .post-card:hover {
      border-color: var(--link-color, #4a90d9);
    }
    .section-title {
      color: #e5e7eb;
      border-bottom-color: #374151;
    }
  }
</style>
