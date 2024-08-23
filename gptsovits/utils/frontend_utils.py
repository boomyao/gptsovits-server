import re
chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]+')

# whether contain chinese character
def contains_chinese(text):
    return bool(chinese_char_pattern.search(text))