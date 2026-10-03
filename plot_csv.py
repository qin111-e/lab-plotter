#!/usr/bin/env python3
"""把实验数据 CSV 画成图。

用法示例：
    python plot_csv.py 示例数据/示例光谱.csv --x 波长 --y 反射率 \
        --title "样品 A 漫反射光谱" --xlabel "波长 (nm)" --ylabel "反射率 (%)"
"""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 不需要图形界面也能出图，必须在 pyplot 之前设置
import matplotlib.pyplot as plt  # noqa: E402

# macOS 上让中文标签正常显示
plt.rcParams["font.sans-serif"] = [
    "PingFang HK",
    "Arial Unicode MS",
    "Heiti TC",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


def detect_delimiter(line):
    """看第一行里出现哪个分隔符，就按哪个切。"""
    for d in (",", "\t", ";"):
        if d in line:
            return d
    return ","


def read_csv(path, skip=0):
    """读入 CSV，返回表头和数据行。空行和 # 开头的注释行会被丢掉。

    skip 用来跳过文件开头的若干行，仪器导出的文件前面常有说明文字。
    """
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        raw = f.readlines()
    lines = [
        ln for ln in raw[skip:] if ln.strip() and not ln.lstrip().startswith("#")
    ]
    if not lines:
        raise SystemExit(f"{path} 里没有有效数据")
    reader = csv.reader(lines, delimiter=detect_delimiter(lines[0]))
    rows = [r for r in reader if r]
    return rows[0], rows[1:]


def pick_column(header, key):
    """key 可以是列名，也可以是列序号（从 0 开始）。"""
    if key in header:
        return header.index(key)
    try:
        idx = int(key)
    except ValueError:
        raise SystemExit(f"找不到列 {key!r}，现有列是：{', '.join(header)}")
    if not 0 <= idx < len(header):
        raise SystemExit(f"列序号 {idx} 超出范围，这个文件一共有 {len(header)} 列")
    return idx


def to_pairs(rows, xi, yi):
    """取出两列数值，跳过空行和不能转成数字的行。"""
    xs, ys, skipped = [], [], 0
    for r in rows:
        if xi >= len(r) or yi >= len(r):
            skipped += 1
            continue
        try:
            xs.append(float(r[xi]))
            ys.append(float(r[yi]))
        except ValueError:
            skipped += 1
    return xs, ys, skipped


def linear_fit(xs, ys):
    """最小二乘直线拟合，返回 (斜率, 截距, R²)。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my, 0.0
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return slope, intercept, r2


def main():
    ap = argparse.ArgumentParser(description="把 CSV 数据画成图")
    ap.add_argument("csv", type=Path, help="CSV 文件路径")
    ap.add_argument("--x", default="0", help="横轴列名或序号，默认第 0 列")
    ap.add_argument("--y", default="1", help="纵轴列名或序号，默认第 1 列")
    ap.add_argument("--title", default=None, help="图标题")
    ap.add_argument("--xlabel", default=None, help="横轴名称")
    ap.add_argument("--ylabel", default=None, help="纵轴名称")
    ap.add_argument("--out", type=Path, default=None, help="输出图片路径")
    ap.add_argument(
        "--skip",
        type=int,
        default=0,
        help="跳过文件开头的 N 行，用于仪器导出文件前的说明文字",
    )
    ap.add_argument(
        "--fit",
        choices=["none", "linear"],
        default="none",
        help="是否做线性拟合",
    )
    ap.add_argument("--dpi", type=int, default=200, help="输出图片清晰度")
    args = ap.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"找不到文件：{args.csv}")

    header, rows = read_csv(args.csv, skip=args.skip)
    xi = pick_column(header, args.x)
    yi = pick_column(header, args.y)
    xs, ys, skipped = to_pairs(rows, xi, yi)
    if not xs:
        raise SystemExit("没有取到任何有效数值，检查一下列名或分隔符")

    xlabel = args.xlabel or header[xi]
    ylabel = args.ylabel or header[yi]
    title = args.title or args.csv.stem
    out = args.out or Path("输出") / f"{args.csv.stem}.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=args.dpi)
    ax.plot(xs, ys, linewidth=1.6, color="#2f6fb3", label=ylabel)

    if args.fit == "linear":
        slope, intercept, r2 = linear_fit(xs, ys)
        fx = [min(xs), max(xs)]
        fy = [slope * x + intercept for x in fx]
        ax.plot(fx, fy, linestyle="--", linewidth=1.2, color="#d1495b", label="线性拟合")
        print(f"线性拟合：斜率 = {slope:.6g}，截距 = {intercept:.6g}，R² = {r2:.6f}")

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)

    print(f"数据点：{len(xs)} 个" + (f"（跳过 {skipped} 行）" if skipped else ""))
    print(f"横轴范围：{min(xs):.6g} ~ {max(xs):.6g}")
    print(f"纵轴范围：{min(ys):.6g} ~ {max(ys):.6g}")
    print(f"已保存：{out}")


if __name__ == "__main__":
    main()
