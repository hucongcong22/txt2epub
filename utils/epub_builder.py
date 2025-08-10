# utils/epub_builder.py
import os
from pathlib import Path
from typing import List

from ebooklib import epub

def build_epub(
        title: str,
        author: str,
        chapters: List[str],
        output_path: Path,
        cover_img: Path | None = None,
) -> None:
    """生成简易 EPUB 文件"""

    book = epub.EpubBook()
    book.set_title(title)
    book.set_language('zh')
    book.add_author(author)

    if cover_img and cover_img.is_file():
        with cover_img.open('rb') as f:
            book.set_cover("cover.jpg", f.read())

    epub_chapters = []

    for idx, content in enumerate(chapters, start=1):

        if isinstance(content, tuple):
            body = content[1]
            title = content[0]
        else:
            body = content
            title = f"第{idx}章"
        c = epub.EpubHtml(
            title=title,
            file_name=f"chap_{idx}.xhtml",
            lang='zh',
        )
        ## 第一行是章节标题。

        # 检查content是否为元组，如果是则取第二个元素（正文内容）

            
        c.content = f"<p>{body.replace('　　','').replace(chr(10), '<p>')}</p>"
        c.add_link(rel="stylesheet", href="style/nav.css", type="text/css")
        book.add_item(c)
        epub_chapters.append(c)

    # Table of Contents & Spine
    book.toc = tuple(epub_chapters)
    book.spine = ['nav'] + epub_chapters

    # nav
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Optional CSS
    style = """
        /* ===== 基础文本样式 ===== */
body {
  font-family: "Noto Serif SC", "Source Han Serif CN", serif, "Apple Color Emoji";
  font-size: 1.05em;
  line-height: 1.7;
  color: #333;
  text-align: justify;
  padding: 0.8em;
  margin: 0 auto;
  max-width: 680px;
  hyphens: auto;
  word-break: break-word;
  text-rendering: optimizeLegibility;
}

/* ===== 标题层级系统 ===== */
h1 {
  font-size: 1.8em;
  text-align: center;
  margin: 1.5em 0 0.8em;
  padding-bottom: 0.5em;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
}

h2 {
  font-size: 1.5em;
  margin: 1.8em 0 0.8em;
  padding-left: 0.5em;
  border-left: 4px solid #8db596;
}

h3 {
  font-size: 1.25em;
  margin: 1.3em 0 0.5em;
  color: #555;
  font-weight: 500;
}

/* ===== 段落排版优化 ===== */
p {
  margin: 0 0 1.2em;
  text-indent: 2em;
  text-align: justify;
  orphans: 3;
  widows: 3;
}

.no-indent {
  text-indent: 0 !important;
}

/* ===== 列表与定义列表 ===== */
ul, ol {
  margin: 0.8em 0 1.2em 2em;
  padding-left: 1.5em;
}

li {
  margin-bottom: 0.5em;
}

dl {
  margin: 1em 0;
}

dt {
  font-weight: bold;
  margin-top: 0.8em;
}

dd {
  margin: 0.3em 0 0.8em 2em;
}

/* ===== 引用与特殊内容 ===== */
blockquote {
  margin: 1.5em 0;
  padding: 1em 1.5em;
  background-color: #f9f9f9;
  border-left: 4px solid #c8d6e5;
  font-style: italic;
  color: #555;
}

pre {
  background-color: #f5f5f5;
  padding: 1em;
  overflow-x: auto;
  border-radius: 3px;
  margin: 1.5em 0;
  font-family: "Courier New", monospace;
  font-size: 0.92em;
}

code {
  font-family: "Fira Code", Consolas, monospace;
  background-color: #f0f0f0;
  padding: 0.15em 0.4em;
  border-radius: 2px;
  font-size: 0.95em;
}

/* ===== 媒体元素 ===== */
img {
  display: block;
  max-width: 92%;
  height: auto;
  margin: 1.8em auto;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

figcaption {
  text-align: center;
  font-style: italic;
  font-size: 0.85em;
  color: #666;
  margin-top: 0.5em;
}

/* ===== 表格样式 ===== */
table {
  width: 100%;
  margin: 1.5em 0;
  border-collapse: collapse;
  border: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: 600;
  padding: 0.6em;
  text-align: left;
}

td {
  padding: 0.5em 0.8em;
  border-top: 1px solid #eee;
}

tr:nth-child(even) {
  background-color: #f8f8f8;
}

/* ===== 超链接样式 ===== */
a {
  color: #1e6b8f;
  text-decoration: none;
  border-bottom: 1px dotted #5d93b1;
  padding-bottom: 0.1em;
}

a:hover {
  color: #0d4d6d;
  border-bottom-style: solid;
}

/* ===== 响应式处理 ===== */
@media (max-width: 500px) {
  body {
    font-size: 0.95em;
    padding: 0.7em;
  }
  
  h1 { font-size: 1.65em; }
  h2 { font-size: 1.4em; }
  h3 { font-size: 1.18em; }
  
  img {
    max-width: 98%;
  }
}

/* ===== 深色模式适配 ===== */
@media (prefers-color-scheme: dark) {
  body {
    color: #e0e0e0;
    background-color: #121212;
  }
  
  blockquote {
    background-color: #1e1e1e;
    border-left-color: #3a506b;
  }
  
  pre, code {
    background-color: #2d2d2d;
  }
  
  a {
    color: #64b5f6;
    border-bottom-color: #90caf9;
  }
  
  a:hover {
    color: #bbdefb;
  }
}
    """
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    epub.write_epub(str(output_path), book, {})
