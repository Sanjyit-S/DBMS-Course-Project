#!/usr/bin/env python3
"""
Comprehensive Emoji Stripper & Sanitizer for ARFOM-DB
Removes all emojis and non-standard unicode symbols across the entire repository.
"""

import os
import re

# Specific emoji replacements for semantic clarity
REPLACEMENTS = {
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '[OK]': '[OK]',
    '[OK]': '[OK]',
    '[OK]': '[OK]',
    '[X]': '[X]',
    'X': 'X',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '->': '->',
    '->': '->',
    '->': '->',
    '->': '->',
    '|': '|',
    '‍': '',
    'Dr.': 'Dr.'
}

# Regex for any other leftover emoji ranges
EMOJI_REGEX = re.compile(
    r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\u203c-\u2049]|[\u25aa-\u25fe]|[\u00a9\u00ae]|[\u2122]|[\u2139]',
    flags=re.UNICODE
)

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        orig = content
        for emoji, repl in REPLACEMENTS.items():
            content = content.replace(emoji, repl)

        # Remove any remaining emojis
        content = EMOJI_REGEX.sub('', content)

        # Clean multiple spaces left behind if needed
        # But preserve layout
        if content != orig:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[CLEANED] {file_path}")
            return 1
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
    return 0

count = 0
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.system_generated' in root:
        continue
    for f in files:
        if f.endswith(('.md', '.html', '.js', '.py', '.css', '.txt', '.sql', '.json')):
            p = os.path.join(root, f)
            count += clean_file(p)

print(f"\nTotal files cleaned: {count}")
