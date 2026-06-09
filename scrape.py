import os
import re
import html
import subprocess
import sys

articles = [
    ("https://xiaolincoding.com/mysql/base/how_select.html", "执行一条 SQL 查询语句，期间发生了什么？", "SQL查询执行过程"),
    ("https://xiaolincoding.com/mysql/base/row_format.html", "MySQL 一行记录是怎么存储的？", "行记录存储"),
    ("https://xiaolincoding.com/mysql/index/index_interview.html", "索引常见面试题", "索引面试题"),
    ("https://xiaolincoding.com/mysql/index/page.html", "从数据页的角度看 B+ 树", "数据页B+树"),
    ("https://xiaolincoding.com/mysql/index/why_index_chose_bpuls_tree.html", "为什么 MySQL 采用 B+ 树作为索引？", "B+树索引"),
    ("https://xiaolincoding.com/mysql/index/2000w.html", "MySQL 单表不要超过 2000W 行，靠谱吗？", "单表2000W"),
    ("https://xiaolincoding.com/mysql/index/index_lose.html", "索引失效有哪些？", "索引失效"),
    ("https://xiaolincoding.com/mysql/index/count.html", "count(*) 和 count(1) 有什么区别？哪个性能最好？", "count性能"),
    ("https://xiaolincoding.com/mysql/index/limit.html", "MySQL 分页有什么性能问题？怎么优化？", "分页优化"),
    ("https://xiaolincoding.com/mysql/transaction/mvcc.html", "事务隔离级别是怎么实现的？", "事务隔离级别"),
    ("https://xiaolincoding.com/mysql/transaction/phantom.html", "MySQL 可重复读隔离级别，完全解决幻读了吗？", "幻读"),
    ("https://xiaolincoding.com/mysql/lock/mysql_lock.html", "MySQL 有哪些锁？", "MySQL锁"),
    ("https://xiaolincoding.com/mysql/lock/how_to_lock.html", "MySQL 是怎么加锁的？", "加锁机制"),
    ("https://xiaolincoding.com/mysql/lock/update_index.html", "update 没加索引会锁全表吗？", "update无索引"),
    ("https://xiaolincoding.com/mysql/lock/lock_phantom.html", "MySQL 记录锁+间隙锁可以防止删除操作而导致的幻读吗？", "间隙锁幻读"),
    ("https://xiaolincoding.com/mysql/lock/deadlock.html", "MySQL 死锁了，怎么办？", "死锁"),
    ("https://xiaolincoding.com/mysql/lock/show_lock.html", "加了什么锁，导致死锁的？", "死锁分析"),
    ("https://xiaolincoding.com/mysql/log/how_update.html", "undo log、redo log、binlog 有什么用？", "日志机制"),
    ("https://xiaolincoding.com/mysql/buffer_pool/buffer_pool.html", "揭开 Buffer_Pool 的面纱", "BufferPool"),
    ("https://xiaolincoding.com/mysql/architecture/mysql_architecture.html", "MySQL的架构是怎样的？", "MySQL架构"),
]

def html_to_text(element_html):
    text = element_html
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<noscript[\s\S]*?</noscript>', '', text, flags=re.IGNORECASE)
    
    def replace_img(m):
        src = m.group(1) or m.group(2) or ''
        if src.startswith('//'):
            src = 'https:' + src
        return f'\n![]({src})\n'
    text = re.sub(r'<img[^>]+(?:data-src|src)="([^"]+)"[^>]*>', replace_img, text, flags=re.IGNORECASE)
    
    def replace_link(m):
        href = m.group(1) or ''
        link_text = m.group(2) or ''
        link_text = re.sub(r'<[^>]+>', '', link_text)
        link_text = html.unescape(link_text).strip()
        if href.startswith('//'):
            href = 'https:' + href
        if not link_text:
            return ''
        return f'[{link_text}]({href})'
    text = re.sub(r'<a[^>]+href="([^"]*)"[^>]*>([\s\S]*?)</a>', replace_link, text, flags=re.IGNORECASE)
    
    def replace_pre(m):
        code = m.group(1) or ''
        code = re.sub(r'<[^>]+>', '', code)
        code = html.unescape(code)
        return f'\n```\n{code}\n```\n'
    text = re.sub(r'<pre[^>]*>([\s\S]*?)</pre>', replace_pre, text, flags=re.IGNORECASE)
    text = re.sub(r'<code[^>]*>([\s\S]*?)</code>', lambda m: f'`{html.unescape(re.sub(r"<[^>]+>", "", m.group(1) or ""))}`', text, flags=re.IGNORECASE)
    
    def replace_table(m):
        table_html = m.group(0)
        rows = re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', table_html, flags=re.IGNORECASE)
        if not rows:
            return ''
        md_rows = []
        for i, row in enumerate(rows):
            cells = re.findall(r'<t[hd][^>]*>([\s\S]*?)</t[hd]>', row, flags=re.IGNORECASE)
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            cells = [html.unescape(c).replace('|', '\\|') for c in cells]
            md_rows.append('| ' + ' | '.join(cells) + ' |')
        if len(md_rows) > 1:
            header_cells = len(re.findall(r'<t[hd][^>]*>[\s\S]*?</t[hd]>', rows[0], flags=re.IGNORECASE))
            separator = '| ' + ' | '.join(['---'] * header_cells) + ' |'
            md_rows.insert(1, separator)
        return '\n' + '\n'.join(md_rows) + '\n'
    text = re.sub(r'<table[^>]*>[\s\S]*?</table>', replace_table, text, flags=re.IGNORECASE)
    
    for level in range(6, 0, -1):
        pattern = f'<h{level}[^>]*>([\\s\\S]*?)</h{level}>'
        def replace_header(m, lvl=level):
            content = re.sub(r'<[^>]+>', '', m.group(1) or '')
            content = html.unescape(content).strip()
            if not content:
                return ''
            return f'\n{"#" * lvl} {content}\n'
        text = re.sub(pattern, replace_header, text, flags=re.IGNORECASE)
    
    text = re.sub(r'<li[^>]*>', '\n- ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_main_content(html_content):
    patterns = [
        r'<div[^>]*class="[^"]*theme-default-content[^"]*"[^>]*>([\s\S]*?)</div>\s*<footer',
        r'<div[^>]*class="[^"]*theme-default-content[^"]*"[^>]*>([\s\S]*?)</div>\s*<div[^>]*class="[^"]*page-nav[^"]*"',
        r'<main[^>]*>([\s\S]*?)</main>',
        r'<article[^>]*>([\s\S]*?)</article>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    
    body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', html_content, flags=re.IGNORECASE)
    if body_match:
        return body_match.group(1)
    
    return html_content

def clean_content(markdown_content, title):
    lines = markdown_content.split('\n')
    cleaned_lines = []
    found_main_title = False
    
    for line in lines:
        stripped = line.strip()
        
        if not found_main_title:
            if stripped.startswith('#') and any(kw in stripped for kw in [title[:3], 'MySQL', 'SQL', '索引', '事务', '锁', '日志', 'Buffer', '架构']):
                found_main_title = True
                cleaned_lines.append(line)
                continue
            continue
        
        ad_keywords = ['牛面AI', '牛面', '公众号', '微信搜索', '扫码关注', '上一篇', '下一篇', '←', '→', '评论', '上次更新', '扫描二维码', '推荐阅读']
        if any(kw in stripped for kw in ad_keywords) and len(stripped) < 80:
            continue
        
        if re.match(r'^[\s\-\[\]]*https?://', stripped) and 'xiaolincoding.com' in stripped:
            continue
        
        cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n\n[←→\s]*\[.*?\]\(.*?xiaolincoding\.com.*?\)[\s\S]*$', '\n', result)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result.strip()

def main():
    output_dir = r'd:\work\docs\software-fundamentals\_posts'
    tmp_dir = r'd:\work\docs\software-fundamentals\_tmp_html'
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    
    file_date = '2026-06-11'
    
    for i, (url, title, short_title) in enumerate(articles):
        safe_title = re.sub(r'[\\/:*?"<>|]', '', short_title)
        html_file = os.path.join(tmp_dir, f'{i+1:02d}_{safe_title}.html')
        md_file = os.path.join(output_dir, f'{file_date}-MySQL-{safe_title}.md')
        
        print(f'[{i+1}/{len(articles)}] {title}')
        
        if os.path.exists(html_file) and os.path.getsize(html_file) > 5000:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            print(f'  使用缓存 ({os.path.getsize(html_file)} bytes)')
        else:
            print(f'  正在下载...')
            try:
                result = subprocess.run(
                    ['curl.exe', '-s', '--max-time', '60', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0', url],
                    capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=90
                )
                html_content = result.stdout
                if len(html_content) < 5000:
                    print(f'  警告: 下载内容较少 ({len(html_content)} bytes)')
                    continue
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f'  下载完成 ({len(html_content)} bytes)')
            except Exception as e:
                print(f'  下载失败: {e}')
                continue
        
        main_html = extract_main_content(html_content)
        md_content = html_to_text(main_html)
        md_content = clean_content(md_content, title)
        
        if len(md_content) < 300:
            body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', html_content, flags=re.IGNORECASE)
            if body_match:
                md_content = html_to_text(body_match.group(1))
                md_content = clean_content(md_content, title)
        
        front_matter = f'''---
title: {title}
date: {file_date} 09:00:00 +0800
categories: [数据库, MySQL]
tags: [数据库, MySQL, 小林coding, 图解]
---

'''
        
        footer = f'''\n\n---
> 参考来源：[{title}]({url})
'''
        
        full_content = front_matter + md_content + footer
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f'  -> {os.path.basename(md_file)} ({len(full_content)} chars)')

if __name__ == '__main__':
    main()
    print('\n=== 所有文章处理完成 ===')
