#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$CURRENT_DIR/../scripts/helpers.sh"

tests_run=0
tests_passed=0

# 测试会话管理
setup_test_session() {
    tmux new-session -d -s tmux_bot_test 2>/dev/null || true
}

teardown_test_session() {
    tmux kill-session -t tmux_bot_test 2>/dev/null || true
}

assert_equal() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"

    ((tests_run++))
    if [ "$expected" = "$actual" ]; then
        echo "  ✓ $test_name"
        ((tests_passed++))
        return 0
    else
        echo "  ✗ $test_name"
        echo "    Expected: '$expected', Actual: '$actual'"
        return 1
    fi
}

# 测试1：get_tmux_option 读取自定义值
test_get_tmux_option_custom() {
    setup_test_session
    tmux set-option -g @openai_model "custom-model"
    local result
    result=$(get_tmux_option "@openai_model" "default-model")
    teardown_test_session
    assert_equal "custom-model" "$result" "get_tmux_option reads custom value"
}

# 测试2：get_tmux_option 默认值回退
test_get_tmux_option_default() {
    setup_test_session
    local result
    result=$(get_tmux_option "@nonexistent_option" "fallback-value")
    teardown_test_session
    assert_equal "fallback-value" "$result" "get_tmux_option uses default"
}

# 测试3：set_tmux_option 写入配置
test_set_tmux_option() {
    setup_test_session
    set_tmux_option "@test_write" "written_value"
    local result
    result=$(tmux show-option -gqv "@test_write")
    teardown_test_session
    assert_equal "written_value" "$result" "set_tmux_option writes value"
}

# 执行测试
echo "Testing configuration management..."
test_get_tmux_option_custom
test_get_tmux_option_default
test_set_tmux_option

echo ""
echo "Config: $tests_passed/$tests_run passed"
[ $tests_passed -eq $tests_run ]
