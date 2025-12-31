#!/usr/bin/env bash

tests_run=0
tests_passed=0

assert_match() {
    local pattern="$1"
    local text="$2"
    local test_name="$3"

    ((tests_run++))
    if echo "$text" | grep -q "$pattern"; then
        echo "  ✓ $test_name"
        ((tests_passed++))
        return 0
    else
        echo "  ✗ $test_name (pattern not found: $pattern)"
        return 1
    fi
}

assert_not_match() {
    local pattern="$1"
    local text="$2"
    local test_name="$3"

    ((tests_run++))
    if ! echo "$text" | grep -q "$pattern"; then
        echo "  ✓ $test_name"
        ((tests_passed++))
        return 0
    else
        echo "  ✗ $test_name (pattern should not exist: $pattern)"
        return 1
    fi
}

# 测试1：日志中 API key 已脱敏
test_api_key_redaction() {
    local latest_log
    latest_log=$(ls -t /tmp/tmux-bot-logs/*.log 2>/dev/null | head -1)

    if [ -z "$latest_log" ]; then
        echo "  - No log files found, skipping API key test"
        echo "    (Run './scripts/suggest.sh \"test\"' first to generate logs)"
        return 0
    fi

    local log_content
    log_content=$(cat "$latest_log")

    # 验证包含 REDACTED 关键字
    assert_match "REDACTED" "$log_content" "Log contains REDACTED keyword"

    # 验证不包含真实 API key 格式（sk-xxx，OpenAI key 长度约 48+ 字符）
    assert_not_match "sk-[A-Za-z0-9]\{40,\}" "$log_content" "Log does not expose API keys"
}

# 测试2：临时文件不残留
test_temp_file_cleanup() {
    local temp_count
    temp_count=$(ls /tmp/tmux-bot-response.* 2>/dev/null | wc -l)

    if [ "$temp_count" -eq 0 ]; then
        echo "  ✓ No leaked temporary files"
        ((tests_run++))
        ((tests_passed++))
        return 0
    else
        echo "  ✗ Found $temp_count leaked temporary files"
        ((tests_run++))
        ls /tmp/tmux-bot-response.*
        return 1
    fi
}

# 执行测试
echo "Testing security measures..."
test_api_key_redaction
test_temp_file_cleanup

echo ""
echo "Security: $tests_passed/$tests_run passed"
[ $tests_passed -eq $tests_run ]
