import re


def merge_lines(text):
    """
    将不以标点符号结尾的行与下一行合并，保留段落结构

    参数:
        text (str): 输入的文本字符串

    返回:
        str: 处理后的文本
    """
    # 定义中英文标点符号集合
    punctuation = r'[。！？.?!…」*”)）]'

    # 将文本按行分割
    lines = text.splitlines()
    merged_lines = []
    i = 0
    n = len(lines)

    print(n)
    while i < n:


        current_line = lines[i].rstrip()  # 移除行尾空白字符


        if len(merged_lines) == 0:
            merged_lines.append(current_line)

        previous_line = merged_lines[- 1].rstrip()
        previous_ends_with_punctuation = re.search(punctuation + r'\s*$', previous_line) is not None
        if not previous_ends_with_punctuation:
            if current_line and len(current_line)>1:
                merged_lines[-1] += current_line.replace('\n', '')
            i += 1
            print(i)
            continue


        # 如果是空行，直接保留
        if not current_line and previous_ends_with_punctuation:
            merged_lines.append(current_line)
            i += 1
            print(i)
            continue
        else:
            merged_lines.append(current_line)
            i+=1
    # 重新构建文本，保留原有段落结构
    return '\n'.join(merged_lines)


# 测试用例
test_text = """
　　萧玉霜听后面色一暗，「是了，要不是我把他的名字叫出就不会有这事了，
都怨我，呜呜呜……」
"""

# 处理文本
processed_text = merge_lines(test_text)

# 打印原始文本和处理后的文本对比
print("原始文本:")
print(test_text)
print("\n" + "=" * 50 + "\n")
print("处理后的文本:")
print(processed_text)
