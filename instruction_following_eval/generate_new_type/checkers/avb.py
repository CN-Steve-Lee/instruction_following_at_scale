import re

def contains_common_punctuations(text):
    common_punctuations = r"[!\"#$%&'()*+,-./:;<=>?@[\\\]^_`{|}~，。、《》？：；•［］〖〗（）…—～]"
    return bool(re.search(common_punctuations, text))

# 示例用法
text = "你好，这是一个测试字符串。"
print(contains_common_punctuations(text))  # 输出：True