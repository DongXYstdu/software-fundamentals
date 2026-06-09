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
### 📌 置顶 · {{ category }}（{{ cat_posts.size }} 篇）
    {% else %}
### {{ category }}（{{ cat_posts.size }} 篇）
    {% endif %}

<ul class="custom-post-list">
  {% for post in cat_posts %}
  <li>
    <a class="custom-post-link" href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span class="custom-post-meta">
      <i class="far fa-calendar"></i> {{ post.date | date: "%Y-%m-%d" }}
      {% if post.categories.size > 1 %}
        · <i class="far fa-folder"></i>
        {% for c in post.categories %}
          {{ c }}{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      {% endif %}
    </span>
  </li>
  {% endfor %}
</ul>

  {% endif %}
{% endfor %}

<style>
  .custom-post-list {
    list-style: none;
    padding: 0;
    margin: 0 0 2rem 0;
  }
  .custom-post-list li {
    padding: 0.5rem 0;
    border-bottom: 1px dashed var(--border-color, #eee);
  }
  .custom-post-list li:last-child {
    border-bottom: none;
  }
  .custom-post-link {
    font-size: 1rem;
    font-weight: 600;
    color: var(--link-color, #4a90d9);
    text-decoration: none;
  }
  .custom-post-link:hover {
    text-decoration: underline;
  }
  .custom-post-meta {
    display: block;
    font-size: 0.8rem;
    color: var(--text-muted, #888);
    margin-top: 0.15rem;
  }
  @media (prefers-color-scheme: dark) {
    .custom-post-list li { border-bottom-color: #2a2a2a; }
  }
</style>
