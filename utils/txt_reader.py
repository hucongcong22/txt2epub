# utils/txt_reader.py
import re

import charset_normalizer

from pathlib import Path
from typing import List, Tuple, Optional, Any


def detect_encoding(file_path: Path) -> tuple[Any, Any]:
    """通过读取文件来推断编码，优先考虑中文编码"""
    try:
        raw = open(file_path, 'rb').read()
    except Exception as e:
        # 如果无法读取文件，返回默认编码
        return 'utf-8', 0.0

    # 使用 charset_normalizer 检测编码
    try:
        res = charset_normalizer.detect(raw)
        detected_encoding = res['encoding']
        confidence = res['confidence']
    except Exception as e:
        # 如果 charset_normalizer 出错，设置默认值
        detected_encoding = 'utf-8'
        confidence = 0.0
    
    # 确保 confidence 不是 None
    if confidence is None:
        confidence = 0.0
    
    # 确保 detected_encoding 不是 None
    if detected_encoding is None:
        detected_encoding = 'utf-8'
    
    # 对于中文文本，优先考虑常见的中文编码
    # 如果检测到的编码置信度较低，尝试其他常见的中文编码
    common_chinese_encodings = ['utf-8', 'gbk', 'gb2312', 'big5']
    
    if confidence < 0.8 or detected_encoding not in common_chinese_encodings:
        # 尝试解码每种编码，看哪种更合理
        best_encoding = detected_encoding
        best_score = 0
        
        for encoding in common_chinese_encodings:
            try:
                # 尝试解码前1000个字符来评估编码的合理性
                sample = raw[:1000].decode(encoding)
                # 简单评估：检查是否有太多乱码字符
                # 中文文本应该有较多的中文字符
                chinese_chars = len([c for c in sample if '\u4e00' <= c <= '\u9fff'])
                total_chars = len(sample)
                score = chinese_chars / total_chars if total_chars > 0 else 0
                
                if score > best_score:
                    best_score = score
                    best_encoding = encoding
            except (UnicodeDecodeError, LookupError):
                # 如果解码失败，跳过此编码
                continue
        
        # 如果找到了更好的编码，使用它
        if best_encoding != detected_encoding and best_score > 0.1:
            detected_encoding = best_encoding
            # 置信度设为基于评分的估计值
            confidence = min(best_score, 1.0)
    
    return detected_encoding or 'utf-8', confidence or 0.0


def read_txt(
        file_path: Path,
        encoding: Optional[str] = None,
        *,
        chapter_regex: str = r"^\s*(?P<title>(?:第([零〇一二三四五六七八九十百千万]|[0-9])+[章节回卷篇]+|Chapter\s+\d+)[^\n]{0,30})",
        split_include_title: bool = False,
        clean_rules: list = None
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
    clean_rules: list      文本净化规则列表，默认为None使用默认规则

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
    
    # ② 文本净化
    text = clean_text(text, clean_rules)

    # ③ 编译正则 - 添加多行匹配模式
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
    但保留章节标题的独立性

    参数:
        text (str): 输入的文本字符串

    返回:
        str: 处理后的文本
    """
    # 定义中英文标点符号集合
    punctuation = r'[。！？.?!…」*”)）]'
    
    # 定义章节标题模式
    chapter_pattern =  r"^\s*(?P<title>(?:第([零〇一二三四五六七八九十百千万]|[0-9])+[章节回卷篇]+|Chapter\s+\d+)[^\n]{0,30})"
    
    # 将文本按行分割
    lines = text.splitlines()
    merged_lines = []
    i = 0
    n = len(lines)

    while i < n:
        current_line = lines[i].rstrip()  # 移除行尾空白字符
        
        # 如果当前行是章节标题，单独保留
        if re.match(chapter_pattern, current_line):
            if merged_lines and merged_lines[-1]:  # 如果前一行不为空，添加一个空行
                merged_lines.append("")
            merged_lines.append(current_line)
            merged_lines.append("")  # 章节标题后添加空行
            i += 1
            continue

        # 如果是第一行
        if len(merged_lines) == 0:
            merged_lines.append(current_line)
            i += 1
            continue
            
        # 检查前一行是否以标点符号结尾
        previous_line = merged_lines[-1].rstrip()
        previous_ends_with_punctuation = re.search(punctuation + r'\s*$', previous_line) is not None
        
        # 如果前一行不以标点符号结尾，且当前行不为空，合并两行
        if not previous_ends_with_punctuation and current_line:
            # 但不要合并章节标题
            if not re.match(chapter_pattern, current_line):
                merged_lines[-1] += current_line
                i += 1
                continue

        # 如果是空行，直接保留
        if not current_line:
            # 只有当前一行以标点结尾时才添加空行
            if previous_ends_with_punctuation or not merged_lines[-1]:
                merged_lines.append(current_line)
            i += 1
            continue
        else:
            merged_lines.append(current_line)
            i += 1
            
    # 重新构建文本，保留原有段落结构
    return '\n'.join(merged_lines)


def clean_text(text: str, clean_rules: list = None) -> str:
    """
    清理文本内容，移除不需要的字符和格式
    
    参数:
        text (str): 原始文本
        clean_rules (list): 清理规则列表，默认为None使用默认规则
        
    返回:
        str: 清理后的文本
    
    默认清理规则:
        1. 移除多余的空白字符（保留单个空格）
        2. 移除行首行尾的空白字符
        3. 移除常见的广告文本
        4. 移除乱码字符
        5. 标准化换行符
    """
    if clean_rules is None:
        # 默认清理规则
        clean_rules = [
            # 移除行首行尾空白字符
            (r'^\s+', '', '行首空白字符'),
            (r'\s+$', '', '行尾空白字符'),
            # 移除多余的空白字符（保留单个空格）
            (r'[ \t]{2,}', ' ', '多余空白字符'),
            # 移除常见的广告文本模式
            (r'本书由.*?txt小说电子书下载', '', '广告文本1'),
            (r'小说天堂.*?免费下载', '', '广告文本2'),
            (r'请记住本书首发域名.*?。第一时间更新', '', '广告文本3'),
            (r'电脑站.*?手机站.*?最新最快', '', '广告文本4'),
            (r'【推荐下，.*?追书真的好用', '', '广告文本5'),
            (r'天才一秒记住.*?，精彩小说无弹窗免费阅读！', '', '广告文本6'),
            # 移除乱码字符（常见的乱码模式）
            (r'□', '', '乱码字符1'),
            (r'', '', '乱码字符2'),
            (r'[-\uF8FF]', '', '私有区字符'),
            # 标准化换行符
            (r'\r\n', '\n', 'Windows换行符'),
            (r'\r', '\n', 'Mac换行符'),
            # 移除多余的空行（保留最多2个连续换行）
            (r'\n{3,}', '\n\n', '多余空行'),
        ]
    
    cleaned_text = text
    for pattern, replacement, description in clean_rules:
        try:
            cleaned_text = re.sub(pattern, replacement, cleaned_text)
        except re.error as e:
            # 如果正则表达式有错误，跳过该规则
            pass
    
    return cleaned_text.strip()

# -------------------------------------------------------------
# 用法示例
# -------------------------------------------------------------
if __name__ == "__main__":
    p = Path("C:\\Users\\hucc\\Downloads\\Telegram Desktop\\凡人修仙传.txt")
    # 只想要章节正文（List[str]）
    chapters = read_txt(p)
    print(len(chapters), "章")      # 报告章节数

    # 如果想保留标题
    chapters_with_titles = read_txt(p, split_include_title=True)
    for t, b in chapters_with_titles:
        print(f"--- {t} ---")
        print(b[:60])