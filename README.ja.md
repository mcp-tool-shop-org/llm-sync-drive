<p align="center">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

リポジトリを構造化された `llms.txt` ファイルにコンパイルし、Google Drive と自動的に同期します。これにより、Gemini などの LLM が `@Google Drive` を通じて最新のコンテキストを取得できます。

## 機能

1. **コンパイル:** リポジトリを単一の構造化された Markdown ドキュメントに変換します (ディレクトリツリー + ファイルの内容)。
2. **対応:** `.gitignore` および `.llmsignore` を尊重し、不要なファイル、機密情報、およびバイナリファイルを排除します。
3. **アップロード:** 単一の Google Drive ファイルにアップロードします (冪等性があり、毎回同じリンクになります)。
4. **監視:** 変更を監視し、設定可能なデバウンス時間で自動的に再同期します。

## クイックスタート

### 1. インストール

```bash
pip install -e .
```

### 2. Google Drive API の設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセスします。
2. プロジェクトを作成するか、既存のプロジェクトを使用します。
3. **APIs & Services → Library** に移動し、**Google Drive API** を検索して、**有効化**します。

#### オプション A: Application Default Credentials (推奨 - 最も簡単)

4. [gcloud CLI](https://cloud.google.com/sdk/docs/install) がインストールされていない場合は、インストールします。
5. 以下のコマンドを実行します。
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. ブラウザが開き、認証を求められます。Google アカウントでサインインします。
7. 完了です。認証ファイルは不要です。ADC トークンは `%APPDATA%/gcloud/application_default_credentials.json` (Windows) または `~/.config/gcloud/application_default_credentials.json` (macOS/Linux) にキャッシュされます。

#### オプション B: サービスアカウント (ヘッドレスキーファイル)

4. **APIs & Services → Credentials** に移動します。
5. **+ Create Credentials → Service account** をクリックします。
6. 名前を付けます (例: `mcp-drive-sync`)。**Create and Continue** をクリックし、その後 **Done** をクリックします。
7. サービスアカウントのメールアドレスをコピーします (例: `mcp-drive-sync@your-project.iam.gserviceaccount.com`)。
8. サービスアカウントをクリックし、**Keys** タブをクリックします。**Add Key → Create new key → JSON** をクリックします。
9. ダウンロードしたファイルを `credentials.json` という名前でリポジトリのディレクトリに保存します。
10. 自分の **Google Drive** に、フォルダを作成します (例: `MCP-Context-Sync`)。
11. 作成したフォルダを、サービスアカウントのメールアドレスで **共有** します (編集権限)。
12. フォルダの URL から **フォルダ ID** をコピーします (URL の `folders/` の後の文字列)。

#### オプション C: OAuth 2.0 (インタラクティブ、CLI 用)

4. **APIs & Services → OAuth consent screen** に移動し、外部向けに設定し、自分のメールアドレスをテストユーザーとして追加します。
5. **Credentials → + Create Credentials → OAuth client ID** (デスクトップアプリ) をクリックします。
6. JSON ファイルをダウンロードし、`credentials.json` という名前で保存します。

### 3. 設定ファイルの初期化

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

これにより、`llm-sync-drive.yaml` が作成されます。このファイルを編集して、以下の設定を行います。

- `auth_mode`: `"adc"` (デフォルト)、`"service-account"」、または `"oauth"`
- `credentials_path`: `credentials.json` へのパス (サービスアカウント/OAuth モードの場合のみ)
- `drive_folder_id`: Google Drive フォルダの ID (フォルダの URL から取得)
- `project_description`: プロジェクトに関する簡単な説明

### 4. 認証 (OAuth のみ)

OAuth モードを使用する場合は、以下のコマンドを実行します。

```bash
llm-sync-drive auth
```

ブラウザが開き、認証を求められます。トークンは `token.json` にキャッシュされます。ADC およびサービスアカウントモードでは、認証の手順は不要です。

### 5. 一度だけ同期

```bash
llm-sync-drive sync
```

コンパイルとアップロードを行います。Drive ファイルの ID が自動的に設定ファイルに保存されます。

### 6. 監視モード

```bash
llm-sync-drive serve
```

最初に同期を実行し、その後、リポジトリの変更を監視します。ファイルが変更されなくなった後、デバウンス時間 (デフォルト 5 秒) が経過すると、再コンパイルと再アップロードが行われます。

### 7. ローカルプレビュー

```bash
llm-sync-drive compile -o llms.txt
```

アップロードせずに、ローカルファイルにコンパイルします。確認に役立ちます。

## MCP サーバー (AI アシスタント連携)

`llm-sync-drive` は、**MCP (Model Context Protocol) サーバー** として動作するため、GitHub Copilot などの AI アシスタントが、会話中にリポジトリを直接 Drive に同期できます。

### VS Code の設定

VS Code のユーザー設定またはワークスペースの `.vscode/mcp.json` に以下を追加します。

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

または、設定ファイルが不要な環境変数を設定して動作させることができます。

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

### MCP Tools

| ツール | 説明 |
|------|-------------|
| `sync_to_drive` | リポジトリをコンパイルし、Google Drive にアップロードします。各フェーズ/マイルストーンの後に実行します。 |
| `compile_context` | ローカルでコンパイルし、アップロードしません（プレビューまたはスナップショットの保存用）。 |
| `sync_status` | 設定、Google Drive のファイル ID、認証ステータスを確認します。 |
| `list_repos` | 既存の同期設定を持つリポジトリを検索します。 |

### 環境変数

| 変数 | 説明 |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | 設定 YAML ファイルのパス（デフォルトではリポジトリのルートディレクトリで自動的に検出されます） |
| `LLM_SYNC_DRIVE_FILE_ID` | Google Drive のファイル ID（設定を上書きします） |
| `LLM_SYNC_DRIVE_FOLDER_ID` | Google Drive のフォルダ ID（設定を上書きします） |
| `LLM_SYNC_DRIVE_CREDENTIALS` | `credentials.json` ファイルのパス（設定を上書きします） |
| `LLM_SYNC_DRIVE_TOKEN` | `token.json` ファイルのパス（設定を上書きします） |

## 設定

すべてのオプションは `llm-sync-drive.yaml` にあります。

| キー | 説明 | デフォルト値 |
|-----|-------------|---------|
| `repo_path` | リポジトリのパス | 必須 |
| `auth_mode` | `"adc"`（最も簡単）、`"service-account"`（キーファイルを使用）、または `"oauth"`（インタラクティブ） | `adc` |
| `credentials_path` | サービスアカウントのキーまたは OAuth の認証情報（JSON 形式） | `credentials.json` |
| `token_path` | キャッシュされた OAuth トークン（OAuth モードでのみ使用） | `token.json` |
| `drive_folder_id` | アップロード先の Google Drive フォルダ | `null` |
| `drive_file_id` | Google Drive のファイル ID（初回アップロード後に自動的に設定されます） | `null` |
| `drive_filename` | Google Drive 上のファイル名 | `llms.txt` |
| `local_output` | ローカルにも保存する | `null` |
| `project_description` | コンパイルされた出力のヘッダーテキスト | `""` |
| `debounce_seconds` | 最後の変更からの待ち時間 | `5.0` |
| `max_file_bytes` | このサイズを超えるファイルをスキップする | `100000` |
| `include_extensions` | これらの拡張子のみを含める | `[]`（すべてのテキストファイル） |
| `extra_ignore_patterns` | 無視する追加のパターン | `[]` |

## 無視ルール

ファイルは以下の順序で除外されます。

1. **組み込みルール**: `.git/`, `node_modules/`, `__pycache__/`, ロックファイル、シークレットファイル
2. **`.gitignore`**: 標準の Git 無視パターン
3. **`.llmsignore`**: LLM のコンテキストに特有の追加パターン（例：テスト用データ、バイナリ資産）
4. **`extra_ignore_patterns`**（設定ファイル内）

開始用のテンプレートとして `.llmsignore.example` を参照してください。

## 出力形式

コンパイルされた `llms.txt` は、この構造に従います。

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

## CLI コマンド

| コマンド | 説明 |
|---------|-------------|
| `llm-sync-drive init` | デフォルトの設定ファイルを作成する |
| `llm-sync-drive auth` | Google Drive と認証する |
| `llm-sync-drive sync` | 一度のコンパイルとアップロード |
| `llm-sync-drive serve` | 自動同期機能付きの監視モード |
| `llm-sync-drive compile` | ローカルでコンパイルする（アップロードしない） |

すべてのコマンドは、デバッグログ出力のために `-v` / `--verbose` オプションを受け入れます。

## セキュリティに関する注意

- **`credentials.json`** と **`token.json`** は `.gitignore` に含まれています。絶対にコミットしないでください。
- このアプリケーションは `drive.file` スコープを使用します（作成したファイルにのみアクセスでき、Google Drive 全体にはアクセスできません）。
- `.llmsignore` は、コンパイルされた出力にシークレットが漏洩するのを防ぐための追加のセキュリティ対策です。
- 組み込みルールでは、常に `.env`, `*.key`, `*.pem` などのファイルは除外されます。

## ライセンス

MIT

---

作成者: <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
