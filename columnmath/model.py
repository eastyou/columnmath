"""竖式计算的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

OPS = ("+", "-", "*")
SYMBOLS = {"+": "+", "-": "−", "*": "×"}
MAX_VALUE = 9999


class ColumnMathError(ValueError):
    """竖式计算相关的输入错误。"""


def check_operand(value: int, name: str = "数字") -> int:
    """校验参与运算的数字。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ColumnMathError("%s必须是整数" % name)
    if value < 0 or value > MAX_VALUE:
        raise ColumnMathError("%s必须在 0–%d 之间" % (name, MAX_VALUE))
    return value


def check_op(op: str) -> str:
    """校验运算符号。"""
    if op not in OPS:
        raise ColumnMathError("运算符只能是 +、- 或 *")
    return op


def compute(a: int, b: int, op: str) -> int:
    """计算 a op b。"""
    check_operand(a, "被操作数")
    check_operand(b, "操作数")
    check_op(op)
    if op == "-" and a < b:
        raise ColumnMathError("减法不允许出现负数")
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    return a * b


@dataclass(frozen=True)
class ColumnProblem:
    """一道竖式计算题。"""

    a: int
    b: int
    op: str

    def __post_init__(self) -> None:
        check_operand(self.a, "第一个数")
        check_operand(self.b, "第二个数")
        check_op(self.op)
        if self.op == "-" and self.a < self.b:
            raise ColumnMathError("减法不允许出现负数")
        if self.op == "*" and self.a * self.b > 999999:
            raise ColumnMathError("乘积过大，请缩小数字")

    @property
    def result(self) -> int:
        """计算结果。"""
        return compute(self.a, self.b, self.op)

    @property
    def symbol(self) -> str:
        """竖式中的运算符号。"""
        return SYMBOLS[self.op]

    @property
    def width(self) -> int:
        """竖式所需的字符宽度。"""
        candidates = [len(str(self.a)), len(str(self.b)) + 1, len(str(self.result))]
        for partial in self.partials():
            candidates.append(len(str(partial)))
        return max(candidates)

    @property
    def prompt(self) -> str:
        """横式题干。"""
        return "%d %s %d" % (self.a, self.symbol, self.b)

    def _pad(self, text: str) -> str:
        return text.rjust(self.width)

    def partials(self) -> List[int]:
        """乘法竖式的部分积。"""
        if self.op != "*" or self.b < 10:
            return []
        parts: List[int] = []
        for index, char in enumerate(reversed(str(self.b))):
            digit = int(char)
            if digit == 0:
                continue
            parts.append(self.a * digit * (10 ** index))
        return parts

    def operator_lines(self) -> List[str]:
        """被操作数与操作数两行。"""
        return [self._pad(str(self.a)), self.op_second_line()]

    def op_second_line(self) -> str:
        """带运算符的第二行。"""
        return (self.symbol + str(self.b)).rjust(self.width)

    @property
    def separator(self) -> str:
        """分隔线。"""
        return "-" * self.width

    def lines(self, with_result: bool = True) -> List[str]:
        """完整竖式文本行。"""
        rows = self.operator_lines()
        rows.append(self.separator)
        for partial in self.partials():
            rows.append(self._pad(str(partial)))
        if self.partials():
            rows.append(self.separator)
        if with_result:
            rows.append(self._pad(str(self.result)))
        return rows

    def text(self) -> str:
        """多行竖式，便于终端查看。"""
        return "\n".join(self.lines(True))


def generate_problems(
    count: int = 8,
    ops: Sequence[str] = OPS,
    max_value: int = 99,
    seed: Optional[int] = None,
) -> List[ColumnProblem]:
    """随机生成不重复的竖式题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise ColumnMathError("题目数量必须是整数")
    if count < 1:
        raise ColumnMathError("题目数量至少为 1")
    chosen_ops = list(ops)
    if not chosen_ops:
        raise ColumnMathError("至少需要一种运算")
    for op in chosen_ops:
        check_op(op)
    check_operand(max_value, "最大值")
    if max_value < 1:
        raise ColumnMathError("最大值至少为 1")

    rng = random.Random(seed)
    pool: List[Tuple[int, int, str]] = []
    for op in chosen_ops:
        for _ in range(count * 6):
            a = rng.randint(1, max_value)
            b = rng.randint(1, max_value)
            if op == "-" and a < b:
                a, b = b, a
            pool.append((a, b, op))
    rng.shuffle(pool)

    problems: List[ColumnProblem] = []
    seen = set()
    for a, b, op in pool:
        key = (a, b, op)
        if key in seen:
            continue
        seen.add(key)
        problems.append(ColumnProblem(a, b, op))
        if len(problems) >= count:
            break
    if len(problems) < count:
        raise ColumnMathError("可用题目不足，请减小题量或放宽范围")
    return problems


def check_answer(problem: ColumnProblem, answer: int) -> bool:
    """判断竖式作答是否正确。"""
    if not isinstance(problem, ColumnProblem):
        raise ColumnMathError("题目必须是 ColumnProblem")
    if isinstance(answer, bool) or not isinstance(answer, int):
        raise ColumnMathError("答案必须是整数")
    return problem.result == answer
