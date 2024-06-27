#!/bin/bash

# ディレクトリを指定
dir="articles"

# 最大の数字を取得
max_num=$(find "$dir" -type f -name "hello*.md" | sed -E 's/.*hello([0-9]+)\.md/\1/' | sort -n | tail -1)

# 新しいファイルのナンバーを決定
if [ -z "$max_num" ]; then
  new_num=1
else
  new_num=$((max_num + 1))
fi

# 新しいファイルのパスを決定
new_file="$dir/hello$new_num.md"

# 新しいファイルを作成し内容を記述
cat <<EOL > "$new_file"
<!--
title: hello$new_num
tags: a, b, c
publishStatus: draft
license: cc-40-by-nd
notifyFollowers: true
-->

# heloo

hay.
EOL

echo "Created $new_file"
