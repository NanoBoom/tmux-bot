# 修复多实例问题 - 全局单例 aichat

## 问题诊断

**现象**：在不同目录按 `Alt+t` 会创建多个 aichat 实例

**根本原因**：
tmux-toggle-popup 的默认 `@popup-id-format` 包含 `#{b:pane_current_path}`，导致：
```
目录 /foo  → session ID: default/xxx/foo/default → aichat 实例 1
目录 /bar  → session ID: default/xxx/bar/default → aichat 实例 2
```

**验证方法**：
```bash
tmux -L popup list-sessions
# 输出多个 session，证明问题存在
```

---

## 解决方案（选择一个）

### 方案 A：全局单例（推荐）

**适用场景**：无论在哪个目录，都复用同一个 AI 对话

**配置修改**（在 `~/.tmux.conf` 中添加）：
```tmux
# 设置全局 popup ID 格式（只依赖名称，不依赖路径）
set -gF @popup-id-format "{popup_name}"

# 修改 Alt+t 绑定（添加显式 --name）
bind -n M-t run "#{@popup-toggle} -w85% -h85% --name=aichat '#{@tmux-bot-chat}'"
```

**重载配置**：
```bash
tmux source ~/.tmux.conf
```

**清理旧 sessions**（可选）：
```bash
# 删除旧的多实例 sessions
tmux -L popup kill-session -a  # 保留当前，删除其他
# 或者全部重建
tmux -L popup kill-server
```

---

### 方案 B：项目级隔离

**适用场景**：希望每个项目有独立的 AI 上下文（不推荐，复杂且无必要）

**修改** `scripts/chat.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail

if ! command -v aichat &>/dev/null; then
  echo "Error: aichat is not installed."
  exit 1
fi

# 动态 session 名称（基于项目目录）
project_name=$(basename "$PWD")
session_name="tmux-bot-${project_name}"

cat <<EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  tmux-bot AI Chat Assistant
  Project: $project_name
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

exec aichat --session "$session_name"
```

**问题**：
- 用户需要手动管理多个 session
- 对话历史分散，难以追溯
- aichat 已有 `.clear session` 命令，无需工具层强制隔离

---

## 推荐配置（最终版）

### Step 1: 修改 ~/.tmux.conf

```tmux
# ===== tmux-toggle-popup 全局配置 =====
set -gF @popup-id-format "{popup_name}"  # 全局单例
set -g @popup-autostart on               # 可选：提升首次启动速度

# ===== tmux-bot 快捷键 =====
bind -n M-t run "#{@popup-toggle} -w85% -h85% --name=aichat '#{@tmux-bot-chat}'"
```

### Step 2: 重载配置

```bash
tmux source ~/.tmux.conf
```

### Step 3: 清理旧 sessions（首次修复时执行）

```bash
# 查看旧 sessions
tmux -L popup list-sessions

# 删除所有旧 sessions
tmux -L popup kill-server

# 或者逐个删除
tmux -L popup kill-session -t "default/doodleEsc/doodleEsc/default"
```

### Step 4: 验证

1. 在目录 A 按 `Alt+t` → 打开 aichat
2. 输入一些对话
3. 关闭 popup（再按 `Alt+t` 或 `Ctrl-C`）
4. 切换到目录 B，再按 `Alt+t`
5. **预期结果**：对话历史保留，证明是同一个实例

```bash
# 验证只有一个 session
tmux -L popup list-sessions
# 输出: aichat: 1 windows (created ...)
```

---

## 技术细节（原理）

### tmux-toggle-popup 的 Session ID 生成机制

**默认格式**（`variables.sh`）：
```bash
DEFAULT_ID_FORMAT='#{b:socket_path}/#{session_name}/#{b:pane_current_path}/{popup_name}'
```

**展开示例**：
```
socket_path       = /tmp/tmux-1000/default
session_name      = doodleEsc
pane_current_path = /Users/fanlz/Projects/foo
popup_name        = default (未指定 --name 时的默认值)

→ session ID: default_doodleEsc_foo_default
```

**问题**：
- `pane_current_path` 会随当前目录变化
- 即使 `-d` 参数固定，ID 生成时仍使用 caller pane 的路径
- 结果：不同目录 → 不同 session ID → 启动新的 aichat 实例

**修复后**（`@popup-id-format "{popup_name}"`）：
```
popup_name = aichat (通过 --name=aichat 显式指定)

→ session ID: aichat
```

**效果**：
- ID 固定为 "aichat"
- 所有调用都 attach 到同一个 session
- `tmux new -As aichat` → 已存在则 attach，不存在则创建

---

## 故障排查

### 问题：修改后仍然创建多个实例

**检查步骤**：

1. 确认配置已生效
```bash
tmux show -gv @popup-id-format
# 输出: {popup_name}
```

2. 确认绑定包含 `--name`
```bash
tmux list-keys -T root | grep M-t
# 输出应包含: --name=aichat
```

3. 杀死旧服务器
```bash
tmux -L popup kill-server
```

4. 重新打开 popup 并验证
```bash
tmux -L popup list-sessions
# 应该只有一个 session: aichat
```

### 问题：对话历史丢失

**原因**：aichat session 文件损坏或被删除

**解决**：
```bash
# 查看 aichat session 存储位置
ls ~/.config/aichat/sessions/
# 输出: tmux-bot.yaml

# 检查文件完整性
cat ~/.config/aichat/sessions/tmux-bot.yaml
```

---

## 参考资料

- [tmux-toggle-popup USAGE.md](https://github.com/loichyan/tmux-toggle-popup/blob/master/USAGE.md)
- [@popup-id-format 配置说明](https://github.com/loichyan/tmux-toggle-popup/blob/master/USAGE.md#popup-id-format)
- 本项目研究文档：`RESEARCH_tmux-toggle-popup.md`

---

**生成时间**: 2026-01-04
**适用版本**: tmux-toggle-popup v0.4.4, tmux-bot v1.x
**作者**: Claude Sonnet 4.5 (Linus 模式)
