#!/bin/bash
# 交互式画图：把数据文件拖进来，回答几个问题，自动出图。
# 双击运行，或者在访达里把 CSV 文件拖到这个文件上。

cd "$(dirname "$0")" || exit 1

PY="./.venv/bin/python"
if [ ! -x "$PY" ]; then
    echo "没有找到项目的 Python 环境。"
    echo "请先在终端里执行下面三行："
    echo "  cd \"$(pwd)\""
    echo "  python3 -m venv .venv"
    echo "  .venv/bin/pip install -r requirements.txt"
    echo
    read -r -p "按回车键关闭。" _
    exit 1
fi

echo "=========================================="
echo "  实验数据画图工具"
echo "=========================================="
echo
echo "第 1 步：把你的数据文件（.csv / .txt）从访达拖到这一行，然后按回车。"
echo "        也可以直接手动输入文件路径。"
echo
read -r -p "文件： " FILE

# 处理拖拽进终端时产生的引号和反斜杠转义
FILE="${FILE%$'\r'}"
FILE="${FILE#\"}"
FILE="${FILE%\"}"
FILE="${FILE//\\/}"

if [ ! -f "$FILE" ]; then
    echo
    echo "× 找不到这个文件：$FILE"
    echo "  检查一下路径对不对，或者重新拖一次。"
    echo
    read -r -p "按回车键关闭。" _
    exit 1
fi

echo
echo "你选的文件是：$FILE"
echo "文件前几行长这样："
head -n 3 "$FILE"
echo
echo "第 2 步：告诉我画哪两列。不确定就直接按回车用默认值。"
echo
read -r -p "  横轴列名或序号（默认第 0 列）： " XCOL
read -r -p "  纵轴列名或序号（默认第 1 列）： " YCOL
read -r -p "  图标题（默认用文件名）： " TITLE
read -r -p "  坐标轴名称，写成「横轴/纵轴」（可留空）： " AXES
read -r -p "  文件开头要跳过的行数（默认 0）： " SKIP

XCOL="${XCOL:-0}"
YCOL="${YCOL:-1}"
SKIP="${SKIP:-0}"

ARGS=(plot_csv.py "$FILE" --x "$XCOL" --y "$YCOL" --skip "$SKIP")

if [ -n "$TITLE" ]; then
    ARGS+=(--title "$TITLE")
fi
if [[ "$AXES" == */* ]]; then
    ARGS+=(--xlabel "${AXES%%/*}" --ylabel "${AXES#*/}")
fi

echo
echo "第 3 步：开始画图……"
echo
MPLCONFIGDIR="${TMPDIR:-/tmp}/mplcache" "$PY" "${ARGS[@]}"

echo
echo "------------------------------------------"
echo "如果上面出现「已保存」，图就在 输出 文件夹里，文件名跟你选的文件同名。"
echo
read -r -p "按回车键关闭这个窗口。" _
