"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from columnmath.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_show(self):
        code, out, _ = run(["show", "45", "27"])
        self.assertEqual(code, 0)
        self.assertIn("+27", out)
        self.assertIn("72", out)

    def test_show_subtraction(self):
        code, out, _ = run(["show", "90", "27", "--op", "-"])
        self.assertEqual(code, 0)
        self.assertIn("63", out)

    def test_show_multiplication(self):
        code, out, _ = run(["show", "12", "13", "--op", "*"])
        self.assertEqual(code, 0)
        self.assertIn("156", out)

    def test_show_answer_correct(self):
        code, out, _ = run(["show", "45", "27", "--answer", "72"])
        self.assertEqual(code, 0)
        self.assertIn("正确", out)

    def test_show_answer_wrong(self):
        code, out, _ = run(["show", "45", "27", "--answer", "70"])
        self.assertEqual(code, 1)
        self.assertIn("错误", out)

    def test_show_negative_subtraction(self):
        code, _, err = run(["show", "3", "8", "--op", "-"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_show_bad_op(self):
        code, _, err = run(["show", "3", "8", "--op", "/"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_single_op(self):
        code, out, _ = run(["sheet", "--count", "6", "--ops", "+", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertNotIn("−", out)
        self.assertNotIn("×", out)

    def test_sheet_empty_ops(self):
        code, _, err = run(["sheet", "--ops", " , "])
        self.assertEqual(code, 2)
        self.assertIn("运算", err)

    def test_sheet_bad_max(self):
        code, _, err = run(["sheet", "--max", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "900", "--max", "3"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
