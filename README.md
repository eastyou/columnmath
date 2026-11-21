# columnmath

[![CI](https://github.com/eastyou/columnmath/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/columnmath/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把加、减、乘写成规范的竖式：数位右对齐、自动画分隔线、乘法展开部分积，一键生成 A4 练习纸与答案页。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道加减乘混合竖式，附答案
columnmath sheet --count 8 --seed 1 --answers -o sheet.html

# 只练两位数以内的加法
columnmath sheet --count 12 --ops + --max 99 -o add.html

# 终端查看一道竖式
columnmath show 45 27
#   45
# + 27
# ----
#   72
# 45 + 27 = 72

# 两位数乘法会自动展开部分积
columnmath show 12 13 --op '*'

# 校验答案，正确返回 0，错误返回 1
columnmath show 45 27 --answer 72
```

## 功能

- 加法、减法、乘法三种竖式
- 减法自动交换两数，保证结果非负
- 乘法两位数自动展开部分积并再次分隔
- 数位右对齐，分隔线长度随位数自适应
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页
- 输入范围校验：0–9999，乘积过大时给出提示

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
