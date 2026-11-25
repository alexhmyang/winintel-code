#!/usr/bin/env python3
"""winintel AI's Ubuntu launcher and configuration layer for OpenCode."""
import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlparse

VERSION = "0.1.0"
ENGINE_VERSION = "1.19.6"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "winintel-code"
PROMPT = """你是 winintel AI（数萌AI服务器）的编程助手，工作环境为 Ubuntu/Linux。
默认用中文沟通。先阅读项目约定和相关代码，再完成用户授权的开发工作。
实际修改文件并运行与修改相关的检查，报告真实结果；禁止编造测试或性能数据。
优先最小、可维护的修复。执行任务时保持必要的进度说明。
保护 API 密钥。涉及删除数据、生产部署、Git 推送时遵循用户明确授权。
未经要求不创建提交，不改写用户已有修改。失败时分析原因并继续处理。
"""


def write_private(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix(".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.chmod(0o600)
    temporary.replace(path)
    path.chmod(0o600)


def engine_config(settings):
    config = {
        "default_agent": "winintel",
        "agent": {"winintel": {"description": "winintel AI 中文编程助手",
                              "mode": "primary", "prompt": PROMPT}},
        "permission": {"edit": "allow", "bash": "ask", "external_directory": "ask"},
    }
    if settings.get("base_url"):
        config["provider"] = {
            "winintel": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "winintel AI / 自定义模型",
                "options": {"baseURL": settings["base_url"],
                            "apiKey": "{env:WININTEL_API_KEY}"},
                "models": {settings["model"]: {"name": settings["model"]}},
            }
        }
        config["model"] = "winintel/" + settings["model"]
    return config


def load_settings():
    path = CONFIG_DIR / "settings.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def configure(base_url, model, key):
    if base_url:
        parsed = urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("模型接口必须是 http:// 或 https:// 地址")
        if parsed.username or parsed.password:
            raise ValueError("不要在接口 URL 中放入密钥")
        if not model.strip() or "#" in model:
            raise ValueError("请填写服务端的模型 ID，例如 Qwen3-Coder")
    settings = {"base_url": base_url.rstrip("/"), "model": model.strip(),
                "api_key": key or "local"}
    write_private(CONFIG_DIR / "settings.json", settings)
    write_private(CONFIG_DIR / "opencode.json", engine_config(settings))


def engine_environment():
    settings = load_settings()
    write_private(CONFIG_DIR / "opencode.json", engine_config(settings))
    env = os.environ.copy()
    env["OPENCODE_CONFIG"] = str(CONFIG_DIR / "opencode.json")
    env["WININTEL_API_KEY"] = settings.get("api_key", "local")
    return env


def engine_path():
    override = os.environ.get("WININTEL_ENGINE")
    path = override or str(Path.home() / ".local/share/winintel-code/engine/opencode")
    if not Path(path).is_file():
        path = shutil.which("opencode")
    if not path:
        raise RuntimeError("找不到 OpenCode 引擎，请先运行 install.sh")
    return path


def build_command(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise ValueError("项目目录不存在：" + str(project))
    command = [engine_path()]
    if args.command == "web":
        command += ["web", "--hostname", "127.0.0.1", "--port", str(args.port)]
    elif args.command == "run":
        if not args.prompt:
            raise ValueError("请提供任务描述")
        command += ["run", "--agent", "winintel", args.prompt]
    elif args.command == "tui":
        command += ["--agent", "winintel"]
    return command, project


def gui():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        raise RuntimeError("桌面入口需要 tkinter：sudo apt install python3-tk")
    root = tk.Tk()
    root.title("winintel AI · Code Agent")
    root.geometry("700x390")
    settings = load_settings()
    project = tk.StringVar(value=str(Path.home()))
    endpoint = tk.StringVar(value=settings.get("base_url", ""))
    model = tk.StringVar(value=settings.get("model", ""))
    key = tk.StringVar(value=settings.get("api_key", ""))
    status = tk.StringVar(value="选择项目目录，保存模型设置，然后启动编程助手。")
    state = {"process": None, "log": None}
    tk.Label(root, text="winintel AI", font=("", 22, "bold")).pack(pady=12)
    form = tk.Frame(root)
    form.pack(fill="x", padx=24)
    for row, (label, variable) in enumerate([
        ("项目目录", project), ("模型接口 /v1", endpoint),
        ("模型 ID", model), ("API Key", key)
    ]):
        tk.Label(form, text=label, anchor="w", width=16).grid(row=row, column=0, pady=5)
        tk.Entry(form, textvariable=variable, show="*" if row == 3 else "",
                 width=54).grid(row=row, column=1, sticky="ew", pady=5)
    def browse():
        selected = filedialog.askdirectory(initialdir=project.get())
        if selected:
            project.set(selected)
    tk.Button(form, text="选择", command=browse).grid(row=0, column=2, padx=6)
    def save():
        configure(endpoint.get().strip(), model.get(), key.get())
    def stop():
        proc = state["process"]
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        if state["log"]:
            state["log"].close()
        state.update(process=None, log=None)
        status.set("助手已停止")
    def start():
        try:
            save()
            if state["process"] and state["process"].poll() is None:
                messagebox.showinfo("winintel AI", "助手正在运行，请先停止后再切换项目")
                return
            stop()
            args = argparse.Namespace(command="web", project=project.get(), port=4096)
            command, directory = build_command(args)
            logpath = CONFIG_DIR / "desktop.log"
            fd = os.open(logpath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            state["log"] = os.fdopen(fd, "w")
            state["process"] = subprocess.Popen(command, cwd=directory, env=engine_environment(),
                                                 stdout=state["log"], stderr=subprocess.STDOUT)
            status.set("启动中：http://127.0.0.1:4096")
            root.after(1500, check)
        except (ValueError, RuntimeError, OSError) as exc:
            messagebox.showerror("winintel AI", str(exc))
    def check():
        proc = state["process"]
        if not proc:
            return
        if proc.poll() is not None:
            status.set("服务已退出，查看 ~/.config/winintel-code/desktop.log")
        else:
            status.set("助手运行中：http://127.0.0.1:4096")
            root.after(1500, check)
    controls = tk.Frame(root)
    controls.pack(pady=18)
    tk.Button(controls, text="启动编程助手", command=start, width=20).pack(side="left", padx=8)
    tk.Button(controls, text="停止", command=stop, width=12).pack(side="left", padx=8)
    tk.Label(root, textvariable=status, wraplength=650).pack()
    tk.Label(root, text="留空模型接口可在编程界面连接云端模型。引擎与编程界面：OpenCode。",
             fg="#666666").pack(pady=8)
    def close():
        stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="winintel AI Ubuntu Code Agent")
    parser.add_argument("--version", action="version", version=VERSION)
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("gui", help="桌面项目与模型设置")
    setup = commands.add_parser("configure", help="配置 OpenAI 兼容接口")
    setup.add_argument("--base-url", required=True)
    setup.add_argument("--model", required=True)
    for name in ("web", "tui", "run"):
        command = commands.add_parser(name)
        command.add_argument("--project", default=".")
        if name == "web":
            command.add_argument("--port", type=int, choices=range(1, 65536), default=4096,
                                 metavar="PORT")
        if name == "run":
            command.add_argument("--trusted", action="store_true",
                                 help="允许本次非交互任务执行 shell 命令")
            command.add_argument("prompt")
    commands.add_parser("doctor", help="显示运行环境")
    args = parser.parse_args()
    try:
        if args.command in (None, "gui"):
            gui()
            return 0
        if args.command == "configure":
            configure(args.base_url, args.model, getpass.getpass("API Key（本地无认证服务直接回车）："))
            print("已保存模型设置。运行 winintel-code web 或打开桌面入口。")
            return 0
        if args.command == "doctor":
            print("winintel-code", VERSION)
            print("引擎:", engine_path())
            return subprocess.call([engine_path(), "--version"])
        command, project = build_command(args)
        env = engine_environment()
        if args.command == "run":
            env["OPENCODE_CONFIG_CONTENT"] = json.dumps({
                "permission": {"bash": "allow" if args.trusted else "deny"}
            })
        os.chdir(project)
        os.execvpe(command[0], command, env)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print("winintel-code:", exc, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
