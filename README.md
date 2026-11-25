# winintel-code · 数萌 AI 编程助手

**面向 Ubuntu 的开源 Code Agent：选择项目，用中文描述任务，让 AI 读代码、改文件、执行命令和验证结果。**

为希望在 Ubuntu 使用桌面编程助手的用户提供可安装的入口。支持 Ubuntu
x86_64 / ARM64，可接云端模型，也可接自建 vLLM、Ollama 和 OpenAI 兼容接口。
由 **winintel AI（数萌AI服务器）**维护，采用 MIT 许可。

首版基于 [OpenCode](https://github.com/anomalyco/opencode) v1.19.6：
编程引擎和浏览器工作界面来自 OpenCode；本项目实现 Ubuntu 安装器、
桌面项目选择器、模型设置、中文 Agent 和命令行入口。桌面入口打开浏览器中的
完整编程界面，当前不提供自行开发的代码编辑器。本项目与 OpenCode 团队、
WorkBuddy 均无隶属关系，版权见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 能做什么

| 能力 | 使用方式 |
|---|---|
| Ubuntu 桌面入口 | 应用菜单启动，选择项目目录与模型 |
| 中文编程助手 | 需求实现、代码解释、故障修复、运行项目检查 |
| 编程工作界面 | OpenCode 浏览器界面，查看会话、工具调用与文件修改 |
| 终端交互 | `winintel-code tui` |
| 单次任务 | `winintel-code run "任务描述"` |
| 自建模型 | vLLM / Ollama / OpenAI 兼容 API |
| 云端模型 | 在 OpenCode 界面连接服务商账户 |
| 本机访问 | Web 服务固定绑定 `127.0.0.1` |

## Ubuntu 安装

建议 Ubuntu 22.04 / 24.04。需要 Python 3、curl、tar；桌面选择器需要 tkinter。
安装器下载固定版本 OpenCode，不需要 npm、Docker 或 root 安装。

```bash
sudo apt update
sudo apt install -y git curl python3 python3-tk
git clone https://github.com/alexhmyang/winintel-code.git
cd winintel-code
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
winintel-code doctor
```

安装后在应用菜单打开 **winintel AI Code Agent**。选择代码目录：

1. 使用云端模型：模型接口留空，启动后在 OpenCode 界面连接服务商并选择模型。
2. 使用本地模型：填写接口、模型 ID 与 API Key，再点击“启动编程助手”。
3. 浏览器打开 `http://127.0.0.1:4096`。选择 `winintel` Agent 后用中文描述任务。
4. 保持启动器窗口开启；点击“停止”或关闭窗口结束其启动的服务。

也可以直接打开编程界面：

```bash
~/.local/bin/winintel-code web --project ~/你的项目
```

终端交互：

```bash
~/.local/bin/winintel-code tui --project ~/你的项目
```

## 接入自己的 vLLM

先让 vLLM 服务提供 OpenAI 兼容接口。模型必须支持工具调用，
服务端需按所用模型设置对应的 tool-call parser。通过 `/v1/models`
确认实际模型 ID；接口连通不等于模型具备可靠的 Agent 能力。

在桌面设置中填写：

| 设置项 | 示例 |
|---|---|
| 模型接口 | `http://127.0.0.1:8000/v1` |
| 模型 ID | `/v1/models` 返回的实际 ID，例如 `Qwen3-Coder` |
| API Key | 服务端密钥；无认证的本地服务留空 |

命令行设置会隐藏密钥输入：

```bash
winintel-code configure --base-url http://127.0.0.1:8000/v1 --model Qwen3-Coder
```

服务器已有 winintel-vllm 时，可以直接填其服务地址。
[winintel-vllm](https://github.com/alexhmyang/winintel-vllm) 负责模型推理，
winintel-code 负责开发任务。

## 接入 Ollama

在 Ollama 安装并运行一个支持工具调用的编程模型后，将接口设置为
`http://127.0.0.1:11434/v1`，模型 ID 填写 `ollama list` 中的名称，
API Key 留空。首次加载与响应速度取决于模型和硬件。

## 单次任务与权限

```bash
winintel-code run --project ~/你的项目 "阅读代码，解释这个项目的启动流程"
winintel-code run --trusted --project ~/你的项目 "修复测试失败并运行相关测试"
```

交互界面默认允许编辑文件，执行 shell 和访问项目外目录时询问。
单次任务默认禁止 shell；`--trusted` 允许该任务执行 shell。
权限通过 OpenCode 配置实现，不是操作系统沙箱；所选项目原有 OpenCode 配置
也会参与合并。请在你授权 Agent 操作的代码目录中使用。
云端模型会接收任务中使用的代码上下文；自建模型可将推理放在自己的服务器上。

## 配置、日志与卸载

| 项目 | 默认位置 |
|---|---|
| 程序与引擎 | `~/.local/share/winintel-code/` |
| 命令入口 | `~/.local/bin/winintel-code` |
| 模型设置 | `~/.config/winintel-code/settings.json` |
| Agent 配置 | `~/.config/winintel-code/opencode.json` |
| 桌面启动日志 | `~/.config/winintel-code/desktop.log` |
| OpenCode 会话与账号 | 由 OpenCode 管理，独立于上述设置 |

模型设置包含 API Key，以当前用户可读写的 `0600` 权限保存。
设置与日志遵循 `XDG_CONFIG_HOME`。不要上传本地设置文件。
运行 `bash install.sh` 可重新安装当前版本，模型设置不被覆盖。
不建议将 Web 端口直接暴露到公网；远程 Ubuntu 可通过 SSH 转发本机端口访问。

关闭助手后卸载程序：

```bash
rm -rf ~/.local/share/winintel-code
rm -f ~/.local/bin/winintel-code ~/.local/share/applications/winintel-code.desktop
```

模型配置与 OpenCode 会话保留，可按需要另行清理。

## 开发与验证

项目运行代码仅依赖 Python 标准库，桌面使用 tkinter。
Ubuntu 安装、配置加载和 Web 健康接口已在 Ubuntu 24.04 / x86_64 的 WSL 环境实测通过。
仓库提供 [GitHub Actions 模板](ci/ubuntu-smoke.yml)，复制到
`.github/workflows/ubuntu-smoke.yml` 可启用自动检查。模板在 Ubuntu 上下载固定版本引擎，
检查安装、配置加载和 Web 健康接口。这些检查不调用付费模型；
真实编程效果取决于所连接的模型。ARM64 安装分支与桌面窗口尚未在对应环境实测。

```bash
bash -n install.sh
python3 -m py_compile winintel_code.py
```

## 品牌与联系

- 维护者：数萌AI服务器 (winintel) / Alex YANG
- 官网：https://winintel.com
- 邮箱：service@winintel.com
- Bilibili：https://space.bilibili.com/429959998
- YouTube：https://www.youtube.com/@winintelcom

欢迎提交 Issue 与 PR，一起打造 Linux 上方便使用的开放编程助手。
