#!/usr/bin/env python3
"""Add prev/next context navigation links to all markdown posts."""

import os
import re
import glob

POSTS_DIR = r"d:\work\docs\software-fundamentals\_posts"
BASE_URL = "/software-fundamentals/posts"

# Parse all articles
articles = []
for filepath in glob.glob(os.path.join(POSTS_DIR, "*.md")):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract front matter
    fm_match = re.match(r'^---\r?\n(.*?)---\r?\n', content, re.DOTALL)
    if not fm_match:
        continue
    
    front_matter = fm_match.group(1)
    
    # Get title
    title = ''
    title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    
    # Get categories
    categories = []
    cat_match = re.search(r'^categories:\s*\[(.+?)\]', front_matter, re.MULTILINE)
    if cat_match:
        cat_str = cat_match.group(1)
        categories = [c.strip() for c in cat_str.split(',')]
    
    primary_cat = categories[0] if categories else "未分类"
    filename = os.path.basename(filepath)
    slug = filename.replace('.md', '')
    
    articles.append({
        'filepath': filepath,
        'filename': filename,
        'title': title,
        'primary_cat': primary_cat,
        'slug': slug,
        'content': content,
    })

# Group by primary category
groups = {}
for article in articles:
    cat = article['primary_cat']
    if cat not in groups:
        groups[cat] = []
    groups[cat].append(article)

# Sort each group by slug and add context links
for cat, group_articles in groups.items():
    group_articles.sort(key=lambda x: x['slug'])
    
    for i, article in enumerate(group_articles):
        # Skip if already has context links
        if "context-nav" in article['content']:
            print(f"Skip (already has context): {article['filename']}")
            continue
        
        prev_article = group_articles[i - 1] if i > 0 else None
        next_article = group_articles[i + 1] if i < len(group_articles) - 1 else None
        
        # Build context links
        prev_link = ""
        if prev_article:
            prev_link = f"<a class='context-link prev' href='{BASE_URL}/{prev_article['slug']}/'><span class='context-label'>上一篇</span><span class='context-title'>{prev_article['title']}</span></a>"
        else:
            prev_link = "<a class='context-link prev disabled'><span class='context-label'>上一篇</span><span class='context-title'>暂无</span></a>"
        
        next_link = ""
        if next_article:
            next_link = f"<a class='context-link next' href='{BASE_URL}/{next_article['slug']}/'><span class='context-label'>下一篇</span><span class='context-title'>{next_article['title']}</span></a>"
        else:
            next_link = "<a class='context-link next disabled'><span class='context-label'>下一篇</span><span class='context-title'>暂无</span></a>"
        
        context_html = f"\n<div class='context-nav'>\n{prev_link}\n{next_link}\n</div>\n"
        
        new_content = article['content'] + context_html
        
        with open(article['filepath'], 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated: {article['filename']}")

print(f"\nDone! Processed {len(articles)} articles in {len(groups)} categories.")
