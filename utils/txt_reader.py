# utils/txt_reader.py
import re

import charset_normalizer

from pathlib import Path
from typing import List, Tuple, Optional, Any


def detect_encoding(file_path: Path) -> tuple[Any, Any]:
    """通过读取文件前 N 字节来推断编码"""
    print(file_path)
    raw = open(file_path, 'rb').read()

    res = charset_normalizer.detect(raw)  # 返回 dict 和 list
    # res['encoding'] -> str / None
    # res['confidence'] -> float
    return res['encoding'] or 'utf-8', res['confidence']


def read_txt(
        file_path: Path,
        encoding: Optional[str] = None,
        *,
        chapter_regex: str = r"^\s*(?P<title>(?:第([零〇一二三四五六七八九十百千万]|[0-9])+[章节回卷篇]+|Chapter\s+\d+)[^\n]{0,30})",
        split_include_title: bool = False
) -> List[str] | List[Tuple[str, str]]:
    """
    读取 TXT 并以 **章节** 列表形式返回。

    1. 读取整篇文件（一次性读入内存）
    2. 根据 `chapter_regex` 识别章节标题
    3. 通过标题位置信息切分正文
    4. 返回 `List`（如果 `split_include_title=True` 还能拿到标题）

    参数
    ----
    file_path: Path        文件完整路径
    encoding:  str | None  指定字符编码；若为 None 则用 `detect_encoding`
    chapter_regex: str     章节标题正则（可覆盖为其它书写习惯）
    split_include_title:  bool
        * False   → 仅返回章节正文（`List[str]`）
        * True    → 返回 `List[(title, body)]`，每个元素包含标题和正文

    返回
    ----
    * **如果 `split_include_title==False`**: `List[str]`
      例如 `[chapter1_body, chapter2_body, …]`
    * **如果 `split_include_title==True`**: `List[Tuple[str, str]]`
      例如 `[("第1章", "正文…"), ("第2章", "正文…")]`
    """
    if encoding is None:
        encoding = detect_encoding(file_path)[0]

    # ① 一次性把整个文件读进来
    text = file_path.read_text(encoding=encoding, errors="replace")
    text = merge_lines(text)

    # ② 编译正则 - 添加多行匹配模式
    chapter_pat = re.compile(chapter_regex, re.IGNORECASE | re.VERBOSE | re.MULTILINE)

    # ③ 找到所有标题的位置信息
    matches = list(chapter_pat.finditer(text))
    if not matches:
        # 如果没有任何标题——把完整文本当作"一个章节"返回
        return [text.strip()] if not split_include_title else [("", text.strip())]

    # ④ 逐一切分正文
    result: List[str] | List[Tuple[str, str]] = []

    # 处理第一个章节之前的内容（如果有）
    first_match = matches[0]
    if first_match.start() > 0:
        preface = text[:first_match.start()].strip()
        if preface:
            if split_include_title:
                result.append(("前言", preface))
            else:
                result.append(preface)

    for i, m in enumerate(matches):
        # ① 章节标题字符串（包含"第 X 章" 或 "Chapter N"）
        title = m.group("title").strip()

        # ② 正文起始 = 标题结束
        body_start = m.end()

        # ③ 正文结束 = 下一个标题开始位置，或全文结尾
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        body = text[body_start:body_end].strip()

        if split_include_title:
            result.append((title, body))
        else:
            result.append(body)

    # ⑤ 返回最终列表
    return result

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
            continue


        # 如果是空行，直接保留
        if not current_line and previous_ends_with_punctuation:
            merged_lines.append(current_line)
            i += 1
            continue
        else:
            merged_lines.append(current_line)
            i+=1
    # 重新构建文本，保留原有段落结构
    return '\n'.join(merged_lines)

# -------------------------------------------------------------
# 用法示例
# -------------------------------------------------------------
if __name__ == "__main__":
    p = Path("C:\\Users\\hucc\\Downloads\\Telegram Desktop\\《极品家丁萧玉霜系列》.txt")
    # 只想要章节正文（List[str]）
    chapters = read_txt(p)
    print(len(chapters), "章")      # 报告章节数

    # 如果想保留标题
    chapters_with_titles = read_txt(p, split_include_title=True)
    for t, b in chapters_with_titles:
        print(f"--- {t} ---")
        print(b[:60])