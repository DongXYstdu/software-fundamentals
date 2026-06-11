#!/usr/bin/env python3
"""Add YYYY-MM-DD- prefix to filenames based on front matter date field."""

import os
import re
import shutil

POSTS_DIR = r"d:\work\docs\software-fundamentals\_posts"

files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')]
renamed = 0

for filename in files:
    # Skip if already has date prefix
    if re.match(r'^\d{4}-\d{2}-\d{2}-', filename):
        continue
    
    filepath = os.path.join(POSTS_DIR, filename)
    
    # Read front matter to get date
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match date field
    date_match = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
    if not date_match:
        print(f"SKIP (no date): {filename}")
        continue
    
    date_str = date_match.group(1)
    new_filename = f"{date_str}-{filename}"
    new_filepath = os.path.join(POSTS_DIR, new_filename)
    
    if os.path.exists(new_filepath):
        print(f"SKIP (exists): {new_filename}")
        continue
    
    shutil.move(filepath, new_filepath)
    renamed += 1
    print(f"Renamed: {filename} -> {new_filename}")

print(f"\nDone! Renamed: {renamed}")
