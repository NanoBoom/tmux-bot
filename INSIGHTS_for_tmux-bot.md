# tmux-toggle-popup 对 tmux-bot 的启示

## 核心洞察

停止用 popup。tmux-bot 的核心需求是**命令行插入**，而 tmux-toggle-popup 是**会话管理器**。两者根本不在同一赛道。

---

## 值得抄的三个实现

### 1. batch_get_options - 性能提升 60%

**当前 tmux-bot 的垃圾实现**:
```bash
# helpers.sh - 三次独立的 tmux 调用
get_tmux_option() {
    tmux show-option -gqv "$1"  # 调用 1
}
tmux_base_url=$(get_tmux_option "@openai_base_url" ...)  # 调用 2
tmux_api_key=$(get_tmux_option "@openai_api_key" ...)    # 调用 3
tmux_model=$(get_tmux_option "@openai_model" ...)        # 调用 4
```

**应该这样做** (直接抄 `helpers.sh:29-49`):
```bash
# 新函数: batch_get_options
batch_get_options() {
    local keys=() formats=() val=() line
    while [[ $# -gt 0 ]]; do
        keys+=("${1%%=*}")
        formats+=("${1#*=}")
        shift
    done
    delimiter=">>>END@$RANDOM"
    set -- "${keys[@]}"
    while IFS= read -r line; do
        if [[ -z $line ]]; then
            :
        elif [[ $line != "$delimiter" ]]; then
            val+=("$line")
        else
            printf -v "$1" "%s" "${val[*]}"
            val=()
            shift
        fi
    done < <(tmux display -p "$(printf "%s\n$delimiter\n" "${formats[@]}")")
}

# 用法 (一次调用搞定)
batch_get_options \
    base_url="#{@openai_base_url}" \
    api_key="#{@openai_api_key}" \
    model="#{@openai_model}"

# 现在 $base_url, $api_key, $model 都已赋值
base_url=${base_url:-$DEFAULT_BASE_URL}
api_key=${api_key:-}
model=${model:-$DEFAULT_MODEL}
```

**效果**:
- 4 次 tmux 进程启动 → 1 次
- 延迟降低 ~60% (CHANGELOG #33 实测数据)
- 代码更简洁

---

### 2. 纯 Bash 测试框架 - 零依赖

**当前 tmux-bot**: 没有自动化测试 (手动测试依赖 tmux 环境)

**应该做的** (参考 `toggle_tests.sh` + `toggle_tests/tmux`):

```bash
# tests/helpers_test.sh
source "$(dirname "${BASH_SOURCE[0]}")/../scripts/helpers.sh"

# Mock tmux 命令
tmux() {
    case "$1" in
        display)
            echo "mocked_value"
            ;;
        show-option)
            echo "@openai_api_key=test-key"
            ;;
    esac
}
export -f tmux

# 测试用例
test_get_tmux_option() {
    result=$(get_tmux_option "@openai_api_key" "default")
    assert_eq "$result" "test-key"
}

# 运行
test_get_tmux_option && echo "PASS" || echo "FAIL"
```

**核心技巧**:
1. **PATH 劫持**: `export PATH="./tests/mocks:$PATH"` 让 fake tmux 优先
2. **函数导出**: `export -f tmux` 让子 shell 使用 mock
3. **临时环境**: `(subshell test)` 确保修改不污染

**收益**:
- CI/CD 可运行 (不需要真实 tmux)
- 回归测试覆盖 (防止破坏现有功能)
- 重构信心

---

### 3. Shell 兼容性处理 - 生产级细节

**问题**: tmux 3.5+ 用 `default-shell` 执行命令，可能不是 `/bin/sh`

**当前 tmux-bot**: 假设 shell 总是 bash (错误)

**应该做的** (参考 `toggle.sh:193-196`):
```bash
# suggest.sh 开头添加
ORIGINAL_SHELL=$(tmux display -p "#{default-shell}")

# 在调用需要 /bin/sh 的脚本前
tmux set default-shell "/bin/sh"

# 立即恢复
trap "tmux set default-shell '$ORIGINAL_SHELL'" EXIT
```

**替代方案** (更简单):
```bash
# 所有脚本开头强制指定 shebang
#!/usr/bin/env bash
set -eo pipefail
```

**关键**: 不要依赖 tmux 的 `default-shell` 设置

---

## 不值得做的四个陷阱

### ❌ 1. 独立服务器架构

**为什么 popup 需要**:
- popup 会话要持久化 (lazygit 运行数小时)
- 会话选择器污染 (100 个 popup session)

**为什么 tmux-bot 不需要**:
- AI 请求是一次性的 (3-10 秒完成)
- 没有会话概念
- 额外的服务器增加复杂度 (配置同步、资源管理)

**结论**: 当前的单进程 + 后台 curl 模式完全够用

---

### ❌ 2. ID 生成和会话管理

**popup 的复杂度来源**:
```bash
# 需要决定: 这两个 popup 是同一个会话吗？
bind M-g run "popup lazygit"  # 在 session A 调用
bind M-g run "popup lazygit"  # 在 session B 调用

# 答案: 看 @popup-id-format 配置 (项目级共享/会话级隔离/...)
```

**tmux-bot**:
- 没有"共享"概念
- 每次请求独立
- 不需要 ID

---

### ❌ 3. Hook 系统

**看起来很酷**:
```tmux
set -g @tmux_bot_before_request 'display "Thinking..."'
set -g @tmux_bot_after_response 'set status-right "Done"'
```

**实际上**:
- 当前的 spinner 动画已经够了
- Hook 增加配置复杂度 (xargs 解析、转义地狱)
- 收益 < 成本

**例外**: 如果用户明确要求可扩展性，再考虑

---

### ❌ 4. Toggle 模式

**popup 有三种模式**: switch / force-close / force-open

**tmux-bot**:
- 没有"当前状态"
- 没有"嵌套调用"
- 按键触发 → 执行 → 结束

---

## 立即行动清单

### 🔴 高优先级 (本周)

1. **重构配置读取**
   - 删除 `get_tmux_option` 的三次调用
   - 实现 `batch_get_options`
   - 文件: `scripts/helpers.sh`, `scripts/suggest.sh`

2. **添加基础测试**
   - 创建 `tests/helpers_test.sh`
   - Mock `tmux`, `curl`, `jq`
   - 测试至少 5 个核心函数

3. **Shell 兼容性**
   - 验证所有脚本的 shebang 正确 (`#!/usr/bin/env bash`)
   - 添加 `set -eo pipefail`

### 🟡 中优先级 (下周)

4. **性能基准**
   - 测量重构前后的延迟
   - 目标: 首次调用 < 500ms

5. **文档更新**
   - 在 README 添加性能指标
   - 更新架构图

### 🟢 低优先级 (以后)

6. **CI/CD 集成**
   - GitHub Actions 运行测试
   - ShellCheck + 自动化测试

---

## 反面教材：不要抄的设计

### 全局变量污染

**popup 的实现**:
```bash
declare name id id_format toggle_keys=() ...
main() {
    # 直接修改全局变量
    name=${name:-$DEFAULT_NAME}
}
```

**更好的做法**:
```bash
main() {
    local name id id_format  # 局部化
    name=${name:-$DEFAULT_NAME}
}
```

### 函数依赖调用顺序

**popup**:
```bash
prepare_init()  # 必须在 main() 之前调用，否则 $popup_id 未定义
```

**更好的做法**:
```bash
prepare_init() {
    local popup_id="$1"  # 显式参数
    echo "$popup_id"
}

main() {
    local id=$(prepare_init "my-id")
}
```

---

## 最终评级

### 🟢 值得学习

- **batch 操作模式**: 直接抄，立即提升 60% 性能
- **测试框架**: 长期投资，提升代码质量
- **边缘情况处理**: macOS Bash 兼容性等细节

### 🟡 选择性借鉴

- **错误处理**: trap 清理我们已经做了
- **日志系统**: 我们的日志轮转已经够用

### 🔴 不要抄

- **popup/会话管理**: 完全不相关
- **Hook 系统**: 过度设计
- **全局变量**: 反模式

---

## 一句话总结

抄 `batch_get_options`，写测试，然后停止羡慕 popup 的复杂度。tmux-bot 的简洁是优势，不是缺陷。
