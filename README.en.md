# winintel-code · Ubuntu AI Coding Agent

[中文](README.md) | **English**

**An open-source coding assistant for Ubuntu and privately hosted models: select a project, describe a task, and let AI read code, edit files, call tools and run checks.**

Maintained by **winintel AI**, built on the MIT-licensed
[OpenCode](https://github.com/anomalyco/opencode) project. Connect your own vLLM,
Ollama or OpenAI-compatible service, or connect a cloud provider through OpenCode.

Our development goal is to make privately deployed models reliable for coding
tasks and deliver the model service, coding assistant, customer configuration
and acceptance documentation together.

[Quick start](#quick-start) · [Model configuration](#model-configuration) ·
[Private deployment](#private-deployment-packages) · [Roadmap](#development-roadmap) ·
[Downloads](https://github.com/alexhmyang/winintel-code/releases)

## Current version and upstream foundation

The current version is **v0.1.0**. The installer pins **OpenCode v1.19.6**.

| Component | Source and responsibility |
|---|---|
| Coding engine, tool calls, sessions and browser workspace | OpenCode |
| Ubuntu installer for the current user | winintel-code |
| Desktop project selection, model setup and service start/stop | winintel-code |
| Chinese agent instructions and command-line entry point | winintel-code |
| Model inference | Your configured private service or cloud provider |

The desktop launcher opens OpenCode's coding interface in a browser. This version
does not include a custom code editor or claim measured improvements over
upstream coding success rates or inference performance.
This project is independent of the OpenCode team and WorkBuddy.

## Available today

| Capability | Usage |
|---|---|
| Ubuntu desktop launcher | Select a project, configure a model, start or stop the service |
| Agent with Chinese defaults | Describe features, explain code, fix issues and edit files |
| Browser workspace | View sessions, tool calls and file changes through OpenCode |
| Terminal interaction | `winintel-code tui --project ~/my-project` |
| Single task | `winintel-code run --project ~/my-project "Describe the task"` |
| Private model connection | Set the endpoint, actual model ID and API key |
| Cloud model connection | Connect a provider account in OpenCode |
| Local service | Web interface binds to `127.0.0.1`, port `4096` by default |

Command execution, testing and complex task completion depend on the model,
server tool-call configuration and effective permissions.
Deploy the model service separately; this repository does not include model weights.

## Platform and verification scope

| Environment | Support and verification scope |
|---|---|
| Ubuntu 24.04 / x86_64 / WSL | Installation, config loading, Web health endpoint and page access checked |
| Ubuntu 22.04 / x86_64 | Target platform; environment acceptance checks remain |
| Ubuntu / ARM64 | Installer has an ARM64 engine path; device acceptance checks remain |
| Native Ubuntu desktop | tkinter launcher provided; desktop interaction checks remain |
| Ubuntu server without a desktop | Start the Web service and access it through SSH forwarding |

Installation requires Python 3, curl and tar. The desktop launcher also needs
`python3-tk`. The application installs into the current user's home directory;
npm, Docker and root installation are not required.
Installing system dependencies uses `sudo`.

## Quick start

Run in an Ubuntu terminal:

```bash
sudo apt update
sudo apt install -y git curl python3 python3-tk
git clone https://github.com/alexhmyang/winintel-code.git
cd winintel-code
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
winintel-code doctor
```

The installer downloads the pinned engine from GitHub, so the first installation
requires network access. Alternatively, download a source archive from
[Releases](https://github.com/alexhmyang/winintel-code/releases), extract it and
run `bash install.sh` inside that directory. The archive does not include a model
or all resources required for offline operation.

### Desktop usage

1. Open **winintel AI Code Agent** from the application menu.
2. Select an existing code project directory.
3. For a private model, enter its endpoint, model ID and API key. For a cloud
   model, leave the endpoint blank.
4. Click the start button, then open `http://127.0.0.1:4096` in your browser.
5. Confirm that the `winintel` agent is selected. Cloud users should connect
   their provider account and choose a model in the coding interface first.
6. Describe a task, such as “Read the project, fix the startup failure and run
   the relevant tests.”

Keep the launcher window open. Its stop button, or closing the window, stops
the service started by that window.
Launcher labels and default agent instructions are in Chinese; you can submit
English tasks to the model.

### Terminal usage

Replace `~/my-project` with an existing project directory:

```bash
# Browser workspace
~/.local/bin/winintel-code web --project ~/my-project

# Terminal interaction
~/.local/bin/winintel-code tui --project ~/my-project

# Choose another local port
~/.local/bin/winintel-code web --project ~/my-project --port 4097
```

CLI services run in the terminal; use `Ctrl+C` to stop them.
The earlier `export PATH=...` affects only the current terminal. In a new
terminal, you can continue using the full executable path.

## Model configuration

### vLLM / winintel-vllm / OpenAI-compatible services

Deploy your model service first. It must support tool calls, with the appropriate
server-side tool-call parser for the model. Use the actual model ID returned by
`/v1/models`.

| Setting | Example and explanation |
|---|---|
| Endpoint | `http://127.0.0.1:8000/v1`; use the server address for remote inference |
| Model ID | The actual served ID; the example below uses `Qwen3-Coder` |
| API key | The server key; leave blank for a local service without authentication |

Enter these settings in the desktop launcher, or run:

```bash
~/.local/bin/winintel-code configure \
  --base-url http://127.0.0.1:8000/v1 \
  --model Qwen3-Coder
```

The command prompts for the key without displaying it. Press Enter for a local
service without authentication, then start `web` or `tui`.
Settings are saved on the client; this does not configure the inference server.

### Ollama

Use `ollama list` to inspect installed models and choose one that supports tools:

| Setting | Value |
|---|---|
| Endpoint | `http://127.0.0.1:11434/v1` |
| Model ID | The actual model name shown by `ollama list` |
| API key | Leave blank for a local service without authentication |

Initial model loading time, generation speed and task quality depend on the
model, hardware and server configuration.

### Cloud models

Leave the model endpoint blank in the desktop launcher, start the coding
interface, then connect a provider and select a model through OpenCode.
OpenCode manages provider credentials. Usage, pricing and account requirements
follow the provider's terms.

## Single tasks and permissions

```bash
# Shell execution is disabled by default
~/.local/bin/winintel-code run --project ~/my-project \
  "Read the code and explain how this project starts"

# Allow shell execution for this task, including tests
~/.local/bin/winintel-code run --trusted --project ~/my-project \
  "Fix the failing tests and run the relevant checks"
```

| Mode | winintel default permissions |
|---|---|
| Interactive Web / TUI | Allow edits; ask for shell and access outside the project |
| Single `run` | Allow edits; deny shell |
| Single `run --trusted` | Allow edits and shell |

These are OpenCode application permissions, not an operating-system sandbox.
Existing project OpenCode configuration also participates in merging; inspect
the effective settings. A task without `--trusted` can still edit files.

Cloud inference sends the required task context to your selected provider.
A private model can keep inference on your own server. Fully disconnected
operation is a separately planned and tested capability.

## Private deployment packages

We plan to deliver **the model service, winintel-code, customer configuration,
usage guides and acceptance results** together. The current version allows
manual private endpoint configuration. Automated customer packaging, full
offline operation and managed upgrade/rollback are on the roadmap.

| Component | Package contents |
|---|---|
| Coding client | Installer, pinned engine, desktop and terminal entry points |
| Private model service | Selected model, inference service and hardware configuration |
| Customer configuration | Endpoint, model, adaptation parameters and permitted task settings |
| Customer credentials | Injected separately or entered by the customer; excluded from public repositories and shared packages |
| Acceptance documentation | Coding task results, server checks and performance tables at agreed concurrency |
| Maintenance documentation | Installation, usage, diagnostics, upgrade and rollback guides |

Related projects:
[winintel-vllm](https://github.com/alexhmyang/winintel-vllm) provides inference,
and [winintel-server-doctor](https://github.com/alexhmyang/winintel-server-doctor)
provides server checks. Automated workflows across these projects are planned,
not available in the current version.

## Development roadmap

| Stage | Planned focus | Intended value |
|---|---|---|
| v0.2 | Customer configuration packages, offline resources, diagnostics and evaluation baseline | Repeatable installation and delivery |
| v0.3 | Model capability detection, adaptation profiles and tool error recovery | More reliable private-model tasks |
| v0.4 | Development, testing, deployment and server acceptance workflows | From code changes to delivery |
| v0.5 | Context selection, task state recovery and caching | Less irrelevant input and repeated work |
| v0.6 | Server request scheduling, accounts and project access boundaries | Shared inference resources for multiple users |
| v1.0 | Complete customer packages and upgrade/rollback acceptance | Maintainable private deployments |

These are development plans, not current features or release date commitments.
See the [detailed innovation roadmap in Chinese](ROADMAP.md) for priorities
and acceptance targets.
Evaluation will compare upstream OpenCode, the stable release and candidate
releases using the same model, hardware and tasks. Reports will track task success,
duration, token usage and concurrency performance. Improvement claims require
measured results.

## Configuration, logs and maintenance

| Item | Default location |
|---|---|
| Application and engine | `~/.local/share/winintel-code/` |
| Executable | `~/.local/bin/winintel-code` |
| Desktop entry | `~/.local/share/applications/winintel-code.desktop` |
| Model settings | `~/.config/winintel-code/settings.json` |
| Generated agent configuration | `~/.config/winintel-code/opencode.json` |
| Desktop startup log | `~/.config/winintel-code/desktop.log` |
| OpenCode sessions and accounts | Managed independently by OpenCode |

Model settings contain the API key and are saved with `0600` permissions.
Do not upload them. Settings and logs respect `XDG_CONFIG_HOME`.
The agent config is regenerated at startup; manual changes to that generated
file are not persistent configuration.

Re-running `bash install.sh` installs the current source version and preserves
model settings. Automated upgrade and rollback management are not included yet.

| Symptom | Action |
|---|---|
| `winintel-code` is not found | Use `~/.local/bin/winintel-code` or set PATH |
| tkinter is missing | Run `sudo apt install python3-tk` |
| Invalid project directory | Select an existing directory; quote paths containing spaces |
| Desktop service exits | Inspect `desktop.log` for startup errors |
| Port is already in use | Stop the existing service or specify another CLI `--port` |
| Model does not call tools | Check model capabilities, actual model ID and server parser |
| Private endpoint cannot be reached | Check the inference service, address, authentication and network |

After starting the service on a remote Ubuntu server, establish forwarding
on the computer where you want to access it:

```bash
ssh -N -L 4096:127.0.0.1:4096 user@server
```

Replace `user@server` with your login details and open
`http://127.0.0.1:4096` in that computer's browser. Web authentication is not
enabled by default in this version. Keep access within a trusted local environment
or use SSH forwarding.

Stop the assistant before uninstalling:

```bash
rm -rf ~/.local/share/winintel-code
rm -f ~/.local/bin/winintel-code ~/.local/share/applications/winintel-code.desktop
```

This preserves model settings, OpenCode sessions and your projects.

## Development and contributions

The winintel launcher uses the Python standard library and tkinter.
The OpenCode engine has its own dependencies.
Copy the [Ubuntu check template](ci/ubuntu-smoke.yml) to
`.github/workflows/ubuntu-smoke.yml` to enable GitHub Actions.
It checks installation, configuration and Web health. It does not call paid models
or measure coding task quality.

Issues, model adaptation reports and pull requests are welcome.
Include your OS, architecture, model, server version, reproduction steps and
logs with credentials removed.

## License and contact

This project uses the [MIT License](LICENSE). OpenCode attribution is included in
[Third-party notices](THIRD_PARTY_NOTICES.md). Preserve applicable copyright and
license notices when modifying, redistributing or using the code commercially.
Models and other dependencies follow their respective licenses. The MIT code
license does not grant upstream trademark rights.

- Maintainer: **winintel AI / Alex YANG**
- Website: https://winintel.com
- Email: service@winintel.com
- Bilibili: https://space.bilibili.com/429959998
- YouTube: https://www.youtube.com/@winintelcom
