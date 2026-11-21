"""竖式计算模型测试。"""

import unittest

from columnmath.model import (
    OPS,
    ColumnMathError,
    ColumnProblem,
    check_answer,
    check_operand,
    check_op,
    compute,
    generate_problems,
)


class ComputeTest(unittest.TestCase):
    """逐一验证 1–9 的加减乘竖式。"""


def _make_compute_test(a, b, op):
    def test(self):
        expected = {"+": a + b, "-": a - b, "*": a * b}[op]
        self.assertEqual(compute(a, b, op), expected)
        problem = ColumnProblem(a, b, op)
        self.assertEqual(problem.result, expected)
        lines = problem.lines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[2], "-" * problem.width)
        self.assertEqual(lines[-1], str(expected).rjust(problem.width))
        self.assertEqual(len(problem.operator_lines()), 2)
        self.assertEqual(problem.separator, lines[2])
        self.assertEqual(len(problem.prompt), len(str(a)) + len(str(b)) + 3)

    test.__doc__ = "%d %s %d 的竖式" % (a, op, b)
    return test


for _a in range(1, 10):
    for _b in range(1, 10):
        for _op in OPS:
            if _op == "-" and _a < _b:
                continue
            setattr(
                ComputeTest,
                "test_%d_%s_%d" % (_a, _op == "*" and "mul" or _op == "+" and "add" or "sub", _b),
                _make_compute_test(_a, _b, _op),
            )


class MultiDigitTest(unittest.TestCase):
    def test_two_digit_addition(self):
        problem = ColumnProblem(456, 278, "+")
        self.assertEqual(problem.result, 734)
        self.assertEqual(problem.width, 4)
        self.assertEqual(problem.op_second_line(), "+278")

    def test_three_digit_subtraction(self):
        problem = ColumnProblem(900, 128, "-")
        self.assertEqual(problem.result, 772)
        self.assertEqual(problem.lines()[1], "−128")

    def test_two_digit_multiplication(self):
        problem = ColumnProblem(12, 13, "*")
        self.assertEqual(problem.result, 156)
        self.assertEqual(problem.partials(), [36, 120])

    def test_multiplication_lines(self):
        problem = ColumnProblem(12, 13, "*")
        lines = problem.lines()
        self.assertEqual(lines[3], "36".rjust(problem.width))
        self.assertEqual(lines[4], "120".rjust(problem.width))
        self.assertEqual(lines[5], "-" * problem.width)
        self.assertEqual(lines[6], "156")

    def test_zero_partial_skipped(self):
        problem = ColumnProblem(12, 10, "*")
        self.assertEqual(problem.partials(), [120])

    def test_single_digit_multiplication_no_partial(self):
        problem = ColumnProblem(12, 3, "*")
        self.assertEqual(problem.partials(), [])
        self.assertEqual(len(problem.lines()), 4)

    def test_zero_operand(self):
        self.assertEqual(ColumnProblem(0, 5, "*").result, 0)
        self.assertEqual(ColumnProblem(5, 0, "+").result, 5)
        self.assertEqual(ColumnProblem(5, 5, "-").result, 0)

    def test_text_output(self):
        text = ColumnProblem(45, 27, "+").text()
        self.assertEqual(text.count("\n"), 3)
        self.assertTrue(text.endswith("72"))


class ValidationTest(unittest.TestCase):
    def test_operand_bounds(self):
        self.assertEqual(check_operand(0), 0)
        self.assertEqual(check_operand(9999), 9999)

    def test_operand_negative(self):
        with self.assertRaises(ColumnMathError):
            check_operand(-1)

    def test_operand_too_large(self):
        with self.assertRaises(ColumnMathError):
            check_operand(10000)

    def test_operand_bool(self):
        with self.assertRaises(ColumnMathError):
            check_operand(True)

    def test_operand_string(self):
        with self.assertRaises(ColumnMathError):
            check_operand("12")

    def test_op_valid(self):
        for op in OPS:
            self.assertEqual(check_op(op), op)

    def test_op_invalid(self):
        with self.assertRaises(ColumnMathError):
            check_op("/")

    def test_negative_subtraction(self):
        with self.assertRaises(ColumnMathError):
            ColumnProblem(3, 8, "-")

    def test_compute_negative(self):
        with self.assertRaises(ColumnMathError):
            compute(3, 8, "-")

    def test_product_too_large(self):
        with self.assertRaises(ColumnMathError):
            ColumnProblem(9999, 9999, "*")

    def test_frozen(self):
        problem = ColumnProblem(3, 8, "+")
        with self.assertRaises(AttributeError):
            problem.a = 4  # type: ignore[misc]


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(p.a, p.b, p.op) for p in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_op(self):
        items = generate_problems(8, ["+"], seed=3)
        self.assertTrue(all(p.op == "+" for p in items))

    def test_subtraction_non_negative(self):
        for problem in generate_problems(30, ["-"], 50, seed=4):
            self.assertGreaterEqual(problem.result, 0)

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=5), generate_problems(8, seed=5))

    def test_seed_differs(self):
        self.assertNotEqual(generate_problems(8, seed=5), generate_problems(8, seed=6))

    def test_zero_count(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(0)

    def test_bool_count(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(True)

    def test_empty_ops(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(3, [])

    def test_bad_op(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(3, ["/"])

    def test_bad_max(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(3, ["+"], 0)

    def test_too_many_for_range(self):
        with self.assertRaises(ColumnMathError):
            generate_problems(500, ["+"], 2)

    def test_within_max(self):
        for problem in generate_problems(20, ["+", "*"], 20, seed=7):
            self.assertLessEqual(problem.a, 20)
            self.assertLessEqual(problem.b, 20)


class AnswerTest(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(check_answer(ColumnProblem(45, 27, "+"), 72))

    def test_incorrect(self):
        self.assertFalse(check_answer(ColumnProblem(45, 27, "+"), 71))

    def test_bad_problem(self):
        with self.assertRaises(ColumnMathError):
            check_answer("45+27", 72)

    def test_bad_answer(self):
        with self.assertRaises(ColumnMathError):
            check_answer(ColumnProblem(45, 27, "+"), "72")

    def test_bool_answer(self):
        with self.assertRaises(ColumnMathError):
            check_answer(ColumnProblem(45, 27, "+"), True)


if __name__ == "__main__":
    unittest.main()
