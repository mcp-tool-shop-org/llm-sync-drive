<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.md">English</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

将您的代码仓库编译成结构化的 `llms.txt` 文件，并自动同步到 Google Drive，以便像 Gemini 这样的 LLM 可以通过 `@Google Drive` 获取最新的上下文信息。

## 功能

1. **编译**您的代码仓库，生成单个结构化的 Markdown 文档（目录树 + 文件内容）。
2. **遵循** `.gitignore` 和 `.llmsignore` 文件，以排除不必要的文件、敏感信息和二进制文件。
3. **上传**到单个 Google Drive 文件（幂等性，每次都使用相同的链接）。
4. **监控**文件变化，并自动重新同步，可配置防抖延迟。

## 快速开始

### 1. 安装

```bash
pip install -e .
```

### 2. 配置 Google Drive API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个项目（或使用现有项目）
3. 导航到 **API 和服务 → 库**，搜索 **Google Drive API**，并 **启用**它。

#### 选项 A：应用默认凭据 (推荐 - 最简单)

4. 如果您没有安装，请安装 [gcloud CLI](https://cloud.google.com/sdk/docs/install)
5. 运行：
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. 浏览器会打开以进行授权 — 使用您的 Google 帐户登录。
7. 完成。不需要凭据文件。 ADC 令牌缓存在 `%APPDATA%/gcloud/application_default_credentials.json` (Windows) 或 `~/.config/gcloud/application_default_credentials.json` (macOS/Linux)

#### 选项 B：服务帐户 (无头密钥文件)

4. 访问 **API 和服务 → 凭据**
5. 点击 **+ 创建凭据 → 服务帐户**
6. 为其命名（例如，`mcp-drive-sync`），然后点击 **创建并继续**，然后点击 **完成**
7. 复制服务帐户的电子邮件地址（例如，`mcp-drive-sync@your-project.iam.gserviceaccount.com`）
8. 点击服务帐户 → **密钥** 选项卡 → **添加密钥 → 创建新密钥 → JSON**
9. 将下载的文件保存为 `credentials.json`，并将其放在您的代码仓库目录中。
10. 在您的 **个人 Google Drive** 中，创建一个文件夹（例如，`MCP-Context-Sync`）
11. **共享**该文件夹，并授予服务帐户电子邮件地址编辑权限。
12. 从文件夹的 URL 中复制 **文件夹 ID**（文件夹 URL 之后的字符串）。

#### 选项 C：OAuth 2.0 (交互式，用于 CLI 使用)

4. 访问 **API 和服务 → OAuth 同意屏幕**，设置为外部模式，添加您的电子邮件地址作为测试用户。
5. 访问 **凭据 → + 创建凭据 → OAuth 客户端 ID** (桌面应用程序)
6. 下载 JSON 文件，并将其保存为 `credentials.json`

### 3. 初始化配置

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

这会创建一个 `llm-sync-drive.yaml` 文件。编辑该文件以设置以下内容：

- `auth_mode`: `"adc"` (默认), `"service-account"` 或 `"oauth"`
- `credentials_path`: 指向您的 `credentials.json` 文件的路径（仅适用于服务帐户/OAuth 模式）
- `drive_folder_id`: Google Drive 文件夹 ID（来自文件夹的 URL）
- `project_description`: 简要描述您的项目

### 4. 身份验证 (仅限 OAuth)

如果使用 OAuth 模式，请运行：

```bash
llm-sync-drive auth
```

打开浏览器进行授权。令牌将缓存在 `token.json` 文件中。ADC 和服务帐户模式不需要身份验证步骤。

### 5. 首次同步

```bash
llm-sync-drive sync
```

编译并上传。Google Drive 文件 ID 将自动保存到您的配置文件中。

### 6. 监控模式

```bash
llm-sync-drive serve
```

运行初始同步，然后监控代码仓库。当文件停止变化一段时间（默认 5 秒）后，它会重新编译并上传。

### 7. 本地预览

```bash
llm-sync-drive compile -o llms.txt
```

编译到本地文件，但不上传。这对于检查很有用。

## MCP 服务器 (AI 助手集成)

`llm-sync-drive` 运行为 **MCP (模型上下文协议) 服务器**，因此像 GitHub Copilot 这样的 AI 助手可以在对话过程中直接将您的代码仓库同步到 Google Drive。

### VS Code 设置

将以下内容添加到 VS Code 用户设置或工作区中的 `.vscode/mcp.json` 文件：

```json
{
  "servers": {
    "llm-sync-drive": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "llm_sync_drive.server"]
    }
  }
}
```

或者，设置环境变量以实现无需配置的运行：

```json
{
  "servers": {
    "llm-sync-drive": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "llm_sync_drive.server"],
      "env": {
        "LLM_SYNC_DRIVE_CONFIG": "F:/AI/my-project/llm-sync-drive.yaml"
      }
    }
  }
}
```

### MCP 工具

| 工具 | 描述 |
|------|-------------|
| `sync_to_drive` | 编译仓库并上传到 Google Drive。每个阶段/里程碑后使用。 |
| `compile_context` | 本地编译，不上传（预览或保存快照）。 |
| `sync_status` | 检查配置、Google Drive 文件 ID 和身份验证状态。 |
| `list_repos` | 查找具有现有同步配置的仓库。 |

### 环境变量

| 变量 | 描述 |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | 配置 YAML 文件的路径（如果未指定，则在仓库根目录自动查找）。 |
| `LLM_SYNC_DRIVE_FILE_ID` | Google Drive 文件 ID（覆盖配置）。 |
| `LLM_SYNC_DRIVE_FOLDER_ID` | Google Drive 文件夹 ID（覆盖配置）。 |
| `LLM_SYNC_DRIVE_CREDENTIALS` | `credentials.json` 文件的路径（覆盖配置）。 |
| `LLM_SYNC_DRIVE_TOKEN` | `token.json` 文件的路径（覆盖配置）。 |

## 配置

所有选项都位于 `llm-sync-drive.yaml` 文件中：

| 键 | 描述 | 默认值 |
|-----|-------------|---------|
| `repo_path` | 仓库的路径 | 必需 |
| `auth_mode` | `"adc"`（最简单），`"service-account"`（密钥文件），或 `"oauth"`（交互式） | `adc` |
| `credentials_path` | 服务帐户密钥或 OAuth 凭据 JSON 文件 | `credentials.json` |
| `token_path` | 缓存的 OAuth 令牌（仅在 oauth 模式下使用） | `token.json` |
| `drive_folder_id` | 用于上传的 Google Drive 文件夹 | `null` |
| `drive_file_id` | Google Drive 文件 ID（首次上传后自动设置） | `null` |
| `drive_filename` | Google Drive 中的文件名 | `llms.txt` |
| `local_output` | 同时保存到本地 | `null` |
| `project_description` | 编译输出中的标题文本 | `""` |
| `debounce_seconds` | 上次更改后的等待时间 | `5.0` |
| `max_file_bytes` | 跳过大于此大小的文件 | `100000` |
| `include_extensions` | 仅包含这些扩展名 | `[]`（所有文本文件） |
| `extra_ignore_patterns` | 要忽略的其他模式 | `[]` |

## 忽略规则

以下文件将被排除（顺序排列）：

1. **内置规则**：`.git/`、`node_modules/`、`__pycache__/`、锁定文件、密钥文件
2. **`.gitignore`**：标准的 Git 忽略模式
3. **`.llmsignore`**：针对 LLM 环境的附加模式（例如，测试用例、二进制资源）
4. **`extra_ignore_patterns`**（在配置文件中）

请参阅 `.llmsignore.example` 文件以获取入门模板。

## 输出格式

编译后的 `llms.txt` 文件遵循以下结构：

```markdown
# project-name

> Auto-generated by llm-sync-drive on 2026-03-12 18:00 UTC
> Source: /path/to/repo
> Files included: 42

## Directory Structure

​```
src/
  index.ts
  utils/
    helpers.ts
​```

## File Contents

### src/index.ts

​```ts
// file contents here
​```
```

## 命令行

| 命令 | 描述 |
|---------|-------------|
| `llm-sync-drive init` | 创建默认配置文件 |
| `llm-sync-drive auth` | 使用 Google Drive 进行身份验证 |
| `llm-sync-drive sync` | 一次性编译 + 上传 |
| `llm-sync-drive serve` | 自动同步的监视模式 |
| `llm-sync-drive compile` | 本地编译（不上传） |

所有命令都支持 `-v` / `--verbose` 参数，用于调试日志。

## 安全提示

- **`credentials.json`** 和 **`token.json`** 文件应在 `.gitignore` 文件中 — 绝不能提交到代码仓库。
- 该应用程序使用 `drive.file` 权限范围（只能访问其创建的文件，而不能访问整个 Google Drive）。
- `.llmsignore` 文件提供了一种深度防御机制，以防止敏感信息泄露到编译输出中。
- 内置规则始终排除 `.env`、`*.key`、`*.pem` 等文件。

## 许可证

MIT

---

由 <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a> 构建。
