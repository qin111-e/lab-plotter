#!/usr/bin/env python3
"""生成一份模拟的漫反射光谱，用来演示 plot_csv.py。

曲线形状参考了带隙吸收边的样子：520 nm 附近反射率快速上升，
620 nm 附近有一个小的吸收谷，再加一点随机噪声。
"""

import csv
import math
import random
from pathlib import Path

random.seed(7)

rows = []
for i in range(251):
    wl = 300 + i * 2  # 300 ~ 800 nm
    edge = 8 + 85 / (1 + math.exp(-(wl - 520) / 18))  # 吸收边
    dip = 18 * math.exp(-(((wl - 620) / 25) ** 2))  # 吸收谷
    value = edge - dip + random.uniform(-1.5, 1.5)
    rows.append((wl, round(value, 2)))

out = Path(__file__).with_name("示例光谱.csv")
with out.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["波长", "反射率"])
    writer.writerows(rows)

print(f"已生成 {out}，共 {len(rows)} 行")
