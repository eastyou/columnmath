"""竖式渲染测试。"""

import unittest

from columnmath.model import ColumnMathError, ColumnProblem, generate_problems
from columnmath.render import render_problem, render_worksheet


class ProblemRenderTest(unittest.TestCase):
    def test_svg_free_html(self):
        page = render_problem(ColumnProblem(45, 27, "+"))
        self.assertIn("<pre", page)
        self.assertIn("45", page)
        self.assertIn("+27", page)

    def test_hide_answer(self):
        page = render_problem(ColumnProblem(45, 27, "+"), show_answer=False)
        self.assertNotIn("72", page)

    def test_show_answer(self):
        page = render_problem(ColumnProblem(45, 27, "+"), show_answer=True)
        self.assertIn("72", page)

    def test_multiplication(self):
        page = render_problem(ColumnProblem(12, 13, "*"), show_answer=True)
        self.assertIn("156", page)
        self.assertIn("36", page)
        self.assertIn("120", page)

    def test_symbols(self):
        self.assertIn("−", render_problem(ColumnProblem(45, 27, "-")))
        self.assertIn("×", render_problem(ColumnProblem(4, 2, "*")))

    def test_bad_problem(self):
        with self.assertRaises(ColumnMathError):
            render_problem("45+27")


class WorksheetRenderTest(unittest.TestCase):
    def setUp(self):
        self.problems = generate_problems(6, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 6)

    def test_no_answers_by_default(self):
        page = render_worksheet(self.problems)
        self.assertNotIn("参考答案", page)

    def test_answers_section(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count('class="card"'), 12)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="三班竖式")
        self.assertIn("三班竖式", page)

    def test_empty(self):
        with self.assertRaises(ColumnMathError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ColumnMathError):
            render_worksheet(["45+27"])

    def test_escaping(self):
        page = render_worksheet(self.problems, title="A&B")
        self.assertIn("A&amp;B", page)

    def test_answer_values_present(self):
        page = render_worksheet(self.problems, answers=True)
        for problem in self.problems:
            self.assertIn(str(problem.result), page)


if __name__ == "__main__":
    unittest.main()
