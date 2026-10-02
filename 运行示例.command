#!/bin/bash
# 双击这个文件就能跑一次示例。
# 它做的事：切到本文件所在目录 -> 用项目自带的 Python 环境运行脚本。

cd "$(dirname "$0")" || exit 1

./.venv/bin/python plot_csv.py "示例数据/示例光谱.csv" \
    --x 波长 --y 反射率 \
    --title "样品 A 漫反射光谱" \
    --xlabel "波长 (nm)" \
    --ylabel "反射率 (%)"

echo ""
echo "----------------------------------------"
echo "完成。图保存在 输出/示例光谱.png"
echo "可以在访达里打开 输出 文件夹查看。"
echo ""

# 双击运行时窗口会停住，方便你看结果；在脚本里调用则不会卡住
if [ -t 0 ]; then
    echo "按回车键关闭这个窗口。"
    read -r
fi
