import os
import re

def remove_emojis(text):
    # Matches most common emojis used in the project
    emoji_pattern = re.compile(
        "["
        u"\U0001F4D8" # 📘
        u"\U0001F4CA" # 📊
        u"\u270F\uFE0F" # ✏️ (with variant selector)
        u"\u270F" # ✏
        u"\U0001F4CB" # 📋
        u"\U0001F4DD" # 📝
        u"\U0001F4D1" # 📑
        u"\U0001F4C4" # 📄
        u"\U0001F514" # 🔔
        u"\U0001F464" # 👤
        u"\U0001F6AA" # 🚪
        u"\u2705" # ✅
        u"\u23F3" # ⏳
        u"\u274C" # ❌
        u"\U0001F4CC" # 📌
        u"\U0001F465" # 👥
        u"\U0001F550" # 🕐
        u"\U0001F4F8" # 📸
        u"\U0001F393" # 🎓
        u"\U0001F3C6" # 🏆
        u"\u26A1" # ⚡
        u"\U0001F3AF" # 🎯
        u"\U0001F4AC" # 💬
        u"\U0001F4BE" # 💾
        u"\U0001F4E4" # 📤
        "]+", flags=re.UNICODE)
    # Also handle combinations like ✏️ where ✏ is matched but variation selector is left behind
    text = emoji_pattern.sub(r'', text)
    # Remove any leftover variation selectors (U+FE0F)
    text = text.replace('\uFE0F', '')
    return text

def clean_html_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = remove_emojis(content)
                # Also remove the empty icon wrapper if it is now empty, or just leave it blank
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Cleaned emojis from {file}")

def clean_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace gradients with solid colors
    content = re.sub(r'background:\s*linear-gradient\([^)]+\);', 'background: var(--primary-600);', content)
    # Revert specific solid colors that should be dark
    content = content.replace('background: var(--primary-600);\n    color: var(--text-inverse);', 'background: var(--bg-sidebar);\n    color: var(--text-inverse);')
    # For sidebar brand icon
    content = content.replace('.sidebar-brand-icon {\n    width: 44px;\n    height: 44px;\n    background: var(--primary-600);', '.sidebar-brand-icon {\n    width: 44px;\n    height: 44px;\n    background: var(--primary-500);')
    
    # Remove glassmorphism
    content = re.sub(r'backdrop-filter:\s*blur\([^)]+\);', '', content)
    
    # Fix the landing page hero text which was using background clip
    content = content.replace('-webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    background-clip: text;', 'color: var(--primary-600);')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Cleaned CSS file")

if __name__ == '__main__':
    base_dir = '/Users/mac/siwes-logbook-system'
    templates_dir = os.path.join(base_dir, 'siwes_logbook/templates')
    css_path = os.path.join(base_dir, 'static/css/styles.css')
    
    clean_html_files(templates_dir)
    clean_css(css_path)
