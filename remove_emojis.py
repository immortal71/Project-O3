import re
import os
from pathlib import Path

# Emoji pattern - matches most common emoji ranges
emoji_pattern = re.compile(
    r'[\U0001F600-\U0001F64F]|'  # Emoticons
    r'[\U0001F300-\U0001F5FF]|'  # Symbols & Pictographs
    r'[\U0001F680-\U0001F6FF]|'  # Transport & Map
    r'[\U0001F700-\U0001F77F]|'  # Alchemical
    r'[\U0001F780-\U0001F7FF]|'  # Geometric Shapes Extended
    r'[\U0001F800-\U0001F8FF]|'  # Supplemental Arrows-C
    r'[\U0001F900-\U0001F9FF]|'  # Supplemental Symbols and Pictographs
    r'[\U0001FA00-\U0001FA6F]|'  # Chess Symbols
    r'[\U0001FA70-\U0001FAFF]|'  # Symbols and Pictographs Extended-A
    r'[\U00002600-\U000026FF]|'  # Miscellaneous Symbols
    r'[\U00002700-\U000027BF]|'  # Dingbats
    r'[\U0000FE00-\U0000FE0F]|'  # Variation Selectors
    r'[\u2600-\u26FF]|[\u2700-\u27BF]'  # More symbols
)

md_files = list(Path('.').glob('*.md'))
count = 0

for md_file in md_files:
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_len = len(content)
        cleaned = emoji_pattern.sub('', content)
        
        if len(cleaned) != original_len:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            count += 1
            print(f'Cleaned: {md_file.name}')
    except Exception as e:
        print(f'Error processing {md_file.name}: {e}')

print(f'\nTotal files cleaned: {count}/{len(md_files)}')
