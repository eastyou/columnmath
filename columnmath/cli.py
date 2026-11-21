"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    OPS,
    ColumnMathError,
    ColumnProblem,
    generate_problems,
)
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="columnmath",
        description="竖式计算练习纸：加、减、乘的竖式排版与答案页",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 竖式练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--ops", default="+,-,*", help="运算，用逗号分隔，默认 +,-,*")
    sheet.add_argument("--max", dest="max_value", type=int, default=99, help="数字上限，默认 99")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="竖式计算练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    show = subparsers.add_parser("show", help="显示一道竖式")
    show.add_argument("a", type=int, help="第一个数")
    show.add_argument("b", type=int, help="第二个数")
    show.add_argument("--op", default="+", help="运算符：+、- 或 *")
    show.add_argument("--answer", type=int, default=None, help="校验答案")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_ops(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ColumnMathError("至少需要一种运算")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "show":
            problem = ColumnProblem(args.a, args.b, args.op)
            print(problem.text())
            print("%s = %d" % (problem.prompt, problem.result))
            if args.answer is not None:
                correct = problem.result == args.answer
                print("作答：%s" % ("正确" if correct else "错误"))
                return 0 if correct else 1
            return 0
        problems = generate_problems(
            args.count, _parse_ops(args.ops), args.max_value, args.seed
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except ColumnMathError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
