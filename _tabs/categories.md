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
      {% assign all_categories =