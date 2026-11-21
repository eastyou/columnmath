"""竖式 SVG / HTML 渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import ColumnMathError, ColumnProblem


def _pre(lines: Sequence[str]) -> str:
    return '<pre class="vertical">%s</pre>' % html.escape("\n".join(lines))


_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 4mm; page-break-inside: avoid; }
.no { margin: 0 0 2mm; font-size: 13px; color: #616e7c; }
.vertical { margin: 0; font-family: "SFMono-Regular", Consolas, "Courier New", monospace;
            font-size: 24px; line-height: 1.35; letter-spacing: 2px; white-space: pre; }
.space { height: 34px; border-bottom: 1px dashed #9aa5b1; margin-top: 2mm; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2f855a; padding-left: 3mm; }
.answer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.answer-grid .vertical { font-size: 16px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def render_problem(problem: ColumnProblem, show_answer: bool = False) -> str:
    """渲染单道竖式。"""
    if not isinstance(problem, ColumnProblem):
        raise ColumnMathError("题目必须是 ColumnProblem")
    return _pre(problem.lines(show_answer))


def render_worksheet(
    problems: Sequence[ColumnProblem],
    title: str = "竖式计算练习",
    answers: bool = False,
) -> str:
    """生成可打印的竖式练习纸。"""
    items = list(problems)
    if not items:
        raise ColumnMathError("至少需要一道题")
    for item in items:
        if not isinstance(item, ColumnProblem):
            raise ColumnMathError("题目必须是 ColumnProblem")

    cards = []
    for index, item in enumerate(items, 1):
        cards.append(
            '<div class="card"><p class="no">%d. %s</p>%s'
            '<div class="space"></div></div>'
            % (index, html.escape(item.prompt), render_problem(item, False))
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="cards">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        answer_cards = [
            '<div class="card"><p class="no">%d. %s = %d</p>%s</div>'
            % (index, html.escape(item.prompt), item.result, render_problem(item, True))
            for index, item in enumerate(items, 1)
        ]
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            '<section class="answer-grid">%s</section></section>'
            % "\n".join(answer_cards)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)
