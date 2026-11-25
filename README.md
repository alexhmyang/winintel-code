# winintel-code · 数萌 AI 编程助手

**中文** | [English](README.en.md)

**面向 Ubuntu 和私有模型的开源编程助手：选择项目，描述任务，让 AI 读取代码、修改文件、调用工具并执行检查。**

由 **winintel AI（数萌AI服务器）**维护，基于 MIT 开源项目
[OpenCode](https://github.com/anomalyco/opencode)。可以接入自己的 vLLM、
Ollama 或 OpenAI 兼容服务，也可以在 OpenCode 界面连接云端模型。

我们持续优化的方向是：让客户部署的模型稳定完成开发任务，并把模型服务、
编程助手、客户配置和验收资料组成一套私有化交付方案。

[快速安装](#快速安装) · [配置模型](#配置模型) · [私有化交付](#私有化交付方案) ·
[优化路线](#持续优化路线) · [版本下载](https://github.com/alexhmyang/winintel-code/releases)

## 当前版本与开源基础

当前版本为 **v0.1.0**，安装器固定下载 **OpenCode v1.19.6**。

| 组成 | 来源与职责 |
|---|---|
| 编程引擎、工具调用、会话和浏览器工作界面 | OpenCode |
| Ubuntu 用户级安装器 | winintel-code |
| 桌面项目选择、模型设置和服务启动／停止 | winintel-code |
| 默认中文 Agent 指令和命令行入口 | winintel-code |
| 模型推理 | 用户配置的私有服务或云端服务 |

桌面入口通过浏览器打开 OpenCode 编程界面；当前没有自研代码编辑器，
也不宣称已经提升原版的编程成功率或推理性能。
本项目与 OpenCode 团队和 WorkBuddy 均无隶属关系。

## 现在可以使用的能力

| 能力 | 使用方式 |
|---|---|
| Ubuntu 桌面启动器 | 应用菜单选择项目目录，设置模型，启动或停止服务 |
| 默认中文编程助手 | 描述需求、解释代码、修复问题、修改文件 |
| 浏览器工作界面 | 使用 OpenCode 查看会话、工具调用和文件修改 |
| 终端交互 | `winintel-code tui --project ~/my-project` |
| 单次任务 | `winintel-code run --project ~/my-project "任务描述"` |
| 私有模型接入 | 配置服务地址、实际模型 ID 和 API Key |
| 云端模型接入 | 在 OpenCode 界面连接服务商账号 |
| 本机服务 | Web 入口绑定 `127.0.0.1`，默认端口 `4096` |

执行命令、运行测试和完成复杂任务取决于模型能力、服务端工具调用配置和实际权限。
模型服务和模型权重需另外部署，本仓库不附带模型。

## 环境与验证范围

| 环境 | 支持与验证范围 |
|---|---|
| Ubuntu 24.04 / x86_64 / WSL | 已完成安装、配置加载、Web 健康接口和页面访问检查 |
| Ubuntu 22.04 / x86_64 | 目标平台；需补对应环境验收 |
| Ubuntu / ARM64 | 安装器提供 ARM64 引擎分支；需补设备验收 |
| Ubuntu 原生桌面 | 已提供 tkinter 启动器；需补桌面交互验收 |
| 无桌面的 Ubuntu 服务器 | 可启动 Web 服务，通过 SSH 转发访问 |

安装依赖 Python 3、curl 和 tar；桌面启动器另外需要 `python3-tk`。
程序安装在当前用户目录，不需要 npm、Docker 或 root 安装。
安装系统依赖时使用 `sudo`。

## 快速安装

在 Ubuntu 终端执行：

```bash
sudo apt update
sudo apt install -y git curl python3 python3-tk
git clone https://github.com/alexhmyang/winintel-code.git
cd winintel-code
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
winintel-code doctor
```

安装器从 GitHub 下载固定版本引擎，首次安装需要网络。
也可在[版本页面](https://github.com/alexhmyang/winintel-code/releases)下载源码包，
解压后进入目录运行 `bash install.sh`。源码包不包含模型或离线运行所需的全部资源。

### 桌面使用

1. 在应用菜单打开 **winintel AI Code Agent**。
2. 选择已有的代码项目目录。
3. 使用私有模型时填写接口、模型 ID 和密钥；使用云端模型时将模型接口留空。
4. 点击“启动编程助手”，在浏览器打开 `http://127.0.0.1:4096`。
5. 确认使用 `winintel` Agent；云端模型用户先在编程界面连接账号并选择模型。
6. 描述任务，例如“阅读项目，修复启动失败，并执行相关测试”。

保持启动器窗口开启。点击“停止”或关闭窗口，会停止该窗口启动的服务。
启动器标签及默认 Agent 指令使用中文；可以向模型输入英文任务。

### 终端使用

将 `~/my-project` 替换为实际存在的项目目录：

```bash
# 浏览器界面
~/.local/bin/winintel-code web --project ~/my-project

# 终端交互
~/.local/bin/winintel-code tui --project ~/my-project

# 自定义本机端口
~/.local/bin/winintel-code web --project ~/my-project --port 4097
```

CLI 启动的服务在终端运行，使用 `Ctrl+C` 停止。
上面的 `export PATH=...` 只影响当前终端；新终端可以继续使用完整命令路径。

## 配置模型

### vLLM / winintel-vllm / OpenAI 兼容服务

先部署模型服务，确认它支持工具调用，并按模型要求配置服务端的
tool-call parser。模型 ID 使用 `/v1/models` 返回的实际值，不能随意填写。

| 设置项 | 示例与说明 |
|---|---|
| 模型接口 | `http://127.0.0.1:8000/v1`；远程模型填写服务器地址 |
| 模型 ID | 服务端实际 ID；下方示例使用 `Qwen3-Coder` |
| API Key | 服务端密钥；无认证的本地服务可留空 |

在桌面填写以上信息，或执行：

```bash
~/.local/bin/winintel-code configure \
  --base-url http://127.0.0.1:8000/v1 \
  --model Qwen3-Coder
```

命令会隐藏密钥输入；无认证的本地服务直接回车。随后启动 `web` 或 `tui`。
配置只保存在当前客户端，不会自动修改推理服务器。

### Ollama

使用 `ollama list` 查看已经安装的模型，选择支持工具调用的模型：

| 设置项 | 值 |
|---|---|
| 模型接口 | `http://127.0.0.1:11434/v1` |
| 模型 ID | `ollama list` 显示的实际模型名称 |
| API Key | 本地无认证服务留空 |

模型首次加载时间、生成速度和任务质量取决于模型、硬件及服务配置。

### 云端模型

在桌面启动器中将模型接口留空，然后启动编程界面，
通过 OpenCode 连接服务商并选择模型。服务商凭据由 OpenCode 管理，
用量、费用和账户条件按对应服务商规则执行。

## 单次任务与权限

```bash
# 默认不允许执行 shell
~/.local/bin/winintel-code run --project ~/my-project \
  "阅读代码，解释项目的启动流程"

# 允许本次任务执行 shell，包括运行测试
~/.local/bin/winintel-code run --trusted --project ~/my-project \
  "修复测试失败并运行相关测试"
```

| 模式 | winintel 默认权限 |
|---|---|
| 交互式 Web / TUI | 文件编辑允许；shell 和项目外目录访问询问 |
| 单次 `run` | 文件编辑允许；shell 禁止 |
| 单次 `run --trusted` | 文件编辑与 shell 允许 |

这些是 OpenCode 应用层权限，不是操作系统沙箱。
项目原有 OpenCode 配置也会参与合并，应检查最终生效设置。
不带 `--trusted` 的单次任务也可能修改文件。

云端推理会向所选服务商发送任务需要的上下文。使用私有模型可以把推理放在自己的
服务器上；完整断网运行是单独规划和验收的能力。

## 私有化交付方案

我们计划将 **模型服务＋winintel-code＋客户配置＋使用与验收资料**一起交付。
现版可以手动预配置私有模型接口；自动客户打包、完整离线运行、升级回退等能力
按下方路线推进。

| 组成 | 交付内容 |
|---|---|
| 编程客户端 | 安装器、固定版本引擎、桌面和终端入口 |
| 私有模型服务 | 客户选择的模型、推理服务和硬件配置方案 |
| 客户配置 | 接口、模型、适配参数与客户允许的任务设置 |
| 客户凭据 | 分别注入或由客户输入，不放入公共仓库及共享包 |
| 验收资料 | 模型任务效果、服务器检查、约定并发下的性能表格 |
| 维护资料 | 安装、使用、诊断、升级和回退教程 |

相关项目：[winintel-vllm](https://github.com/alexhmyang/winintel-vllm) 负责推理，
[winintel-server-doctor](https://github.com/alexhmyang/winintel-server-doctor) 负责服务器检查。
跨项目自动任务流程属于后续规划，当前不作为已实现功能。

## 持续优化路线

| 阶段 | 计划重点 | 预期价值 |
|---|---|---|
| v0.2 | 客户配置包、离线资源、诊断与评测基线 | 可重复安装和交付 |
| v0.3 | 模型能力检测、适配档案、工具错误恢复 | 提高私有模型任务可靠性 |
| v0.4 | 开发、测试、部署和服务器验收流程 | 从修改代码到完整交付 |
| v0.5 | 上下文选择、任务状态恢复和缓存策略 | 减少无效输入与重复工作 |
| v0.6 | 服务端请求调度、账号与项目边界 | 支持多人共用推理资源 |
| v1.0 | 完整客户方案及升级回退验收 | 可长期维护的私有化产品 |

以上是研发规划，不是当前功能或发布日期承诺。详细目标见
[创新与持续优化路线图](ROADMAP.md)。
优化会用同模型、同硬件、同任务对照原版 OpenCode、稳定版和候选版，
记录任务成功率、耗时、token 用量与并发性能，提升结论以实测为依据。

## 配置、日志与维护

| 项目 | 默认位置 |
|---|---|
| 程序与引擎 | `~/.local/share/winintel-code/` |
| 命令入口 | `~/.local/bin/winintel-code` |
| 桌面入口 | `~/.local/share/applications/winintel-code.desktop` |
| 模型设置 | `~/.config/winintel-code/settings.json` |
| 生成的 Agent 配置 | `~/.config/winintel-code/opencode.json` |
| 桌面启动日志 | `~/.config/winintel-code/desktop.log` |
| OpenCode 会话与账号 | 由 OpenCode 独立管理 |

模型设置包含密钥，以 `0600` 文件权限保存，不应上传。
设置与日志遵循 `XDG_CONFIG_HOME`。Agent 配置会在启动时重新生成，
手动编辑这个生成文件不会成为持久配置。

重新运行 `bash install.sh` 会安装当前源码版本，保留模型设置。
现版不提供自动升级或回退管理。

| 常见情况 | 处理方式 |
|---|---|
| `winintel-code` 命令不存在 | 使用 `~/.local/bin/winintel-code`，或设置 PATH |
| 提示缺少 tkinter | 执行 `sudo apt install python3-tk` |
| 项目目录错误 | 选择已存在的目录，含空格的路径用双引号包住 |
| 桌面服务退出 | 查看 `desktop.log` 中的启动错误 |
| 端口已占用 | 停止已运行服务，或用 CLI 指定其他 `--port` |
| 模型没有执行工具 | 检查模型工具能力、实际模型 ID 和服务端解析器 |
| 配置了本地接口但无法连接 | 检查推理服务、地址、认证和网络连通性 |

远程 Ubuntu 服务器上启动服务后，在访问它的电脑上建立 SSH 转发：

```bash
ssh -N -L 4096:127.0.0.1:4096 user@server
```

将 `user@server` 替换为实际登录信息，在该电脑浏览器访问
`http://127.0.0.1:4096`。现版默认不启用 Web 登录认证，
入口应保持在受信任的本机环境或通过 SSH 转发使用。

关闭助手后卸载程序：

```bash
rm -rf ~/.local/share/winintel-code
rm -f ~/.local/bin/winintel-code ~/.local/share/applications/winintel-code.desktop
```

该操作保留模型设置、OpenCode 会话和用户项目。

## 开发与贡献

winintel 启动器依赖 Python 标准库和 tkinter；OpenCode 引擎有其自身依赖。
仓库提供 [Ubuntu 检查模板](ci/ubuntu-smoke.yml)，复制到
`.github/workflows/ubuntu-smoke.yml` 可启用 GitHub Actions。
它检查安装、配置加载和 Web 健康接口，不调用付费模型，也不代表编程任务质量评测。

欢迎提交可复现的问题、模型适配经验和 PR。问题报告请说明系统、架构、
模型、服务版本、复现步骤及去除密钥后的日志。

## 许可证与联系

项目采用 [MIT License](LICENSE)，OpenCode 版权声明见
[第三方声明](THIRD_PARTY_NOTICES.md)。修改、二次分发和商业使用时保留相应版权与许可。
模型和其他依赖各自遵循其许可证；MIT 代码许可不授予上游商标使用权。

- 维护者：**数萌AI服务器 (winintel) / Alex YANG**
- 官网：https://winintel.com
- 联系邮箱：service@winintel.com
- Bilibili：https://space.bilibili.com/429959998
- YouTube：https://www.youtube.com/@winintelcom
