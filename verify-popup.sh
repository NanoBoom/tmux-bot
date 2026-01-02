#!/usr/bin/env bash
# 验证 tmux-toggle-popup 是否正确安装

echo "=== tmux-toggle-popup 安装验证 ==="
echo ""

# 1. 检查插件目录
if [ -d "$HOME/.tmux/plugins/tmux-toggle-popup" ]; then
    echo "✓ 插件目录存在"
else
    echo "✗ 插件目录不存在"
    echo "  请运行: prefix + I 安装插件"
    exit 1
fi

# 2. 检查入口文件
if [ -f "$HOME/.tmux/plugins/tmux-toggle-popup/toggle-popup.tmux" ]; then
    echo "✓ 入口文件存在: toggle-popup.tmux"
elif [ -f "$HOME/.tmux/plugins/tmux-toggle-popup/popup.tmux" ]; then
    echo "✓ 入口文件存在: popup.tmux"
else
    echo "⚠ 未找到标准入口文件"
    ls "$HOME/.tmux/plugins/tmux-toggle-popup/" | head -5
fi

# 3. 检查 @popup-toggle 变量
popup_toggle=$(tmux show -gqv @popup-toggle 2>/dev/null)
if [ -n "$popup_toggle" ]; then
    echo "✓ @popup-toggle 已设置: $popup_toggle"

    if [ -x "$popup_toggle" ]; then
        echo "✓ toggle 脚本可执行"
    else
        echo "✗ toggle 脚本不可执行"
    fi
else
    echo "✗ @popup-toggle 未设置"
    echo "  请运行: tmux source ~/.tmux.conf"
    exit 1
fi

# 4. 检查聊天键绑定（默认 b）
chat_key=$(tmux show -gqv @tmux_bot_chat_key 2>/dev/null)
chat_key=${chat_key:-b}  # Default to 'b' if not set

echo ""
echo "=== 聊天键绑定状态 (当前: $chat_key) ==="
v_binding=$(tmux list-keys -T prefix 2>/dev/null | grep "bind-key.*${chat_key} ")
if echo "$v_binding" | grep -q "popup-toggle"; then
    echo "✓ 聊天键 ($chat_key) 使用 POPUP 模式"
elif echo "$v_binding" | grep -q "new-window"; then
    echo "⚠ 聊天键 ($chat_key) 使用 NEW-WINDOW 降级模式"
else
    echo "✗ 聊天键 ($chat_key) 未绑定"
fi

echo ""
echo "=== 验证完成 ==="
echo "按 'prefix + ${chat_key}' 测试 popup 聊天功能（默认为 'prefix + b'）"
