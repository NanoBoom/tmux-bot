#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$CURRENT_DIR/../scripts/helpers.sh"

# 测试计数器
tests_run=0
tests_passed=0

# 断言函数
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
        echo "    Expected: '$expected'"
        echo "    Actual:   '$actual'"
        return 1
    fi
}

assert_not_empty() {
    local value="$1"
    local test_name="$2"

    ((tests_run++))
    if [ -n "$value" ]; then
        echo "  ✓ $test_name"
        ((tests_passed++))
        return 0
    else
        echo "  ✗ $test_name (value is empty)"
        return 1
    fi
}

# 测试1：parse_template 基础替换
test_parse_template_basic() {
    local result
    result=$(parse_template "OS: {OS}, Shell: {SHELL}" "Linux" "bash" "")
    assert_equal "OS: Linux, Shell: bash" "$result" "parse_template basic replacement"
}

# 测试2：parse_template 全局替换
test_parse_template_global() {
    local result
    result=$(parse_template "{OS} {OS} {OS}" "macOS" "zsh" "")
    assert_equal "macOS macOS macOS" "$result" "parse_template global replacement"
}

# 测试3：get_os 返回非空值
test_get_os() {
    local os
    os=$(get_os)
    assert_not_empty "$os" "get_os returns value"
}

# 测试4：get_shell 返回非空值
test_get_shell() {
    local shell
    shell=$(get_shell)
    assert_not_empty "$shell" "get_shell returns value"
}

# 执行所有测试
echo "Testing helpers.sh functions..."
test_parse_template_basic
test_parse_template_global
test_get_os
test_get_shell

# 输出结果
echo ""
echo "Helpers: $tests_passed/$tests_run passed"
[ $tests_passed -eq $tests_run ]
