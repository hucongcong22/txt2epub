# txt2epub.py
import argparse
import sys
from pathlib import Path

from utils.logger import setup_logger
from utils.txt_reader import read_txt, detect_encoding
from utils.epub_builder import build_epub

log = setup_logger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TXT → EPUB 转换工具（可打包为 .exe）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input', type=Path, help="输入 TXT 文件路径")
    parser.add_argument('output', type=Path, nargs='?', help="输出 EPUB 文件路径，默认同名 .epub")
    parser.add_argument('-t', '--title', help="EPUB 标题（默认文件名）")
    parser.add_argument('-a', '--author', default="作者未知", help="作者")
    parser.add_argument('-c', '--cover', type=Path, help="封面图片（JPG/PNG）")
    parser.add_argument('-e', '--encoding', help="手动指定源文件编码 (如: utf-8, gbk, gb2312, big5)")
    parser.add_argument('-d', '--debug', action='store_true', help="调试模式，输出 DEBUG 级日志")
    parser.add_argument('--no-clean', action='store_true', help="禁用文本净化功能")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.debug:
        log.setLevel('DEBUG')

    if not args.input.is_file():
        log.error("输入文件不存在: %s", args.input)
        sys.exit(1)

    # 读取文本
    if args.encoding:
        enc = args.encoding
        log.info("使用指定编码: %s", enc)
    else:
        log.info("检测文件编码……")
        enc, confidence = detect_encoding(args.input)
        log.info("检测到的文件编码: %s (置信度: %.2f)", enc, confidence)

    log.info("读取文本……")
    # 如果用户禁用了文本净化功能，则传入空列表作为clean_rules参数
    clean_rules = [] if args.no_clean else None
    lines = read_txt(args.input, enc, split_include_title=True, clean_rules=clean_rules)

    if not lines:
        log.error("文件为空或无法读取文本")
        sys.exit(1)

    # 生成 EPUB
    title = args.title or args.input.stem
    output_path = args.output or args.input.with_suffix('.epub')

    log.info("生成 EPUB…")
    build_epub(
        title=title,
        author=args.author,
        chapters=lines,
        output_path=output_path,
        cover_img=args.cover
    )

    log.info("完成: %s", output_path)


if __name__ == "__main__":
    main()
