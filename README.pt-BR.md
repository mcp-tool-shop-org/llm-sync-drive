<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.md">English</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

Compile seu repositório em um arquivo estruturado `llms.txt` e sincronize-o automaticamente com o Google Drive, para que modelos de linguagem como o Gemini possam acessar o contexto mais recente através do `@Google Drive`.

## O que ele faz

1. **Compila** seu repositório em um único documento Markdown estruturado (árvore de diretórios + conteúdo dos arquivos).
2. **Respeita** os arquivos `.gitignore` e `.llmsignore` para excluir informações desnecessárias, segredos e arquivos binários.
3. **Envia** para um único arquivo no Google Drive (idempotente — o mesmo link a cada vez).
4. **Monitora** as alterações e sincroniza automaticamente com um intervalo de tempo configurável.

## Como começar

### 1. Instale

```bash
pip install -e .
```

### 2. Configure a API do Google Drive

1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/)
2. Crie um projeto (ou use um existente)
3. Navegue até **APIs e Serviços → Biblioteca**, procure por **Google Drive API** e **ative-a**.

#### Opção A: Credenciais Padrão da Aplicação (Recomendado — mais simples)

4. Instale a [gcloud CLI](https://cloud.google.com/sdk/docs/install) se você ainda não a tiver.
5. Execute:
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. Um navegador será aberto para solicitação de permissão — faça login com sua conta do Google.
7. Pronto. Nenhum arquivo de credenciais é necessário. O token ADC é armazenado em cache em `%APPDATA%/gcloud/application_default_credentials.json` (Windows) ou `~/.config/gcloud/application_default_credentials.json` (macOS/Linux).

#### Opção B: Conta de Serviço (arquivo de chave sem interface)

4. Acesse **APIs e Serviços → Credenciais**
5. Clique em **+ Criar Credenciais → Conta de serviço**
6. Dê um nome (por exemplo, `mcp-drive-sync`) e clique em **Criar e continuar**, depois em **Concluído**.
7. Copie o endereço de e-mail da conta de serviço (por exemplo, `mcp-drive-sync@your-project.iam.gserviceaccount.com`).
8. Clique na conta de serviço → aba **Chaves** → **Adicionar chave → Criar nova chave → JSON**.
9. Salve o arquivo baixado como `credentials.json` no diretório do seu repositório.
10. No seu **Google Drive pessoal**, crie uma pasta (por exemplo, `MCP-Context-Sync`).
11. **Compartilhe** essa pasta com o endereço de e-mail da conta de serviço (com permissões de Editor).
12. Copie o **ID da pasta** da URL da pasta (a string após `folders/`).

#### Opção C: OAuth 2.0 (Interativo, para uso na linha de comando)

4. Acesse **APIs e Serviços → Tela de consentimento OAuth**, configure como "Externo" e adicione seu e-mail como um usuário de teste.
5. Acesse **Credenciais → + Criar Credenciais → ID do cliente OAuth** (aplicativo para desktop).
6. Baixe o JSON e salve-o como `credentials.json`.

### 3. Inicialize a configuração

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

Isso cria o arquivo `llm-sync-drive.yaml`. Edite-o para definir:

- `auth_mode`: `"adc"` (padrão), `"service-account"` ou `"oauth"`.
- `credentials_path`: o caminho para o seu arquivo `credentials.json` (apenas para os modos "service-account" e "oauth").
- `drive_folder_id`: o ID da pasta do Google Drive (obtido da URL da pasta).
- `project_description`: uma breve descrição do seu projeto.

### 4. Autentique (apenas para OAuth)

Se estiver usando o modo OAuth, execute:

```bash
llm-sync-drive auth
```

Isso abre um navegador para solicitação de permissão. O token é armazenado em cache em `token.json`. Os modos ADC e conta de serviço não exigem nenhuma etapa de autenticação.

### 5. Sincronize uma vez

```bash
llm-sync-drive sync
```

Compila e envia. O ID do arquivo do Drive é salvo automaticamente na sua configuração.

### 6. Modo de monitoramento

```bash
llm-sync-drive serve
```

Executa uma sincronização inicial e, em seguida, monitora o repositório. Após os arquivos pararem de ser alterados pelo intervalo de tempo configurado (padrão: 5 segundos), ele recompila e envia.

### 7. Visualização local

```bash
llm-sync-drive compile -o llms.txt
```

Compila para um arquivo local sem enviar. Útil para inspeção.

## Servidor MCP (Integração com Assistente de IA)

O `llm-sync-drive` funciona como um **servidor MCP (Model Context Protocol)**, permitindo que assistentes de IA, como o GitHub Copilot, sincronizem seus repositórios diretamente com o Drive durante uma conversa.

### Configuração do VS Code

Adicione às configurações de usuário do VS Code ou ao arquivo `.vscode/mcp.json` do seu espaço de trabalho:

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

Ou defina variáveis de ambiente para operação sem configuração:

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

### Ferramentas MCP

| Ferramenta | Descrição |
|------|-------------|
| `sync_to_drive` | Compila o repositório e envia para o Google Drive. Use após cada fase/marco. |
| `compile_context` | Compila localmente sem enviar (visualização ou salvando um instantâneo). |
| `sync_status` | Verifica a configuração, o ID do arquivo do Google Drive e o status de autenticação. |
| `list_repos` | Encontra repositórios com configurações de sincronização existentes. |

### Variáveis de Ambiente

| Variável | Descrição |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Caminho para o arquivo YAML de configuração (detectado automaticamente na raiz do repositório, caso contrário). |
| `LLM_SYNC_DRIVE_FILE_ID` | ID do arquivo do Google Drive (substitui a configuração). |
| `LLM_SYNC_DRIVE_FOLDER_ID` | ID da pasta do Google Drive (substitui a configuração). |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Caminho para o arquivo `credentials.json` (substitui a configuração). |
| `LLM_SYNC_DRIVE_TOKEN` | Caminho para o arquivo `token.json` (substitui a configuração). |

## Configuração

Todas as opções estão em `llm-sync-drive.yaml`:

| Chave | Descrição | Valor Padrão |
|-----|-------------|---------|
| `repo_path` | Caminho para o repositório | obrigatório |
| `auth_mode` | `"adc"` (mais simples), `"service-account"` (arquivo de chave) ou `"oauth"` (interativo) | `adc` |
| `credentials_path` | Arquivo JSON da conta de serviço ou credenciais OAuth | `credentials.json` |
| `token_path` | Token OAuth armazenado em cache (apenas no modo OAuth) | `token.json` |
| `drive_folder_id` | Pasta do Google Drive para upload | `null` |
| `drive_file_id` | ID do arquivo do Google Drive (definido automaticamente após o primeiro upload) | `null` |
| `drive_filename` | Nome do arquivo no Google Drive | `llms.txt` |
| `local_output` | Salva também localmente | `null` |
| `project_description` | Texto do cabeçalho na saída compilada | `""` |
| `debounce_seconds` | Tempo de espera após a última alteração | `5.0` |
| `max_file_bytes` | Ignora arquivos maiores que este | `100000` |
| `include_extensions` | Inclui apenas estas extensões | `[]` (todos os arquivos de texto) |
| `extra_ignore_patterns` | Padrões adicionais a serem ignorados | `[]` |

## Regras de Ignorar

Os arquivos são excluídos (em ordem por):

1. **Regras internas**: `.git/`, `node_modules/`, `__pycache__/`, arquivos de bloqueio, arquivos secretos
2. **`.gitignore`**: Padrões de ignoramento padrão do Git
3. **`.llmsignore`**: Padrões adicionais específicos para o contexto de LLM (por exemplo, fixtures de teste, ativos binários)
4. **`extra_ignore_patterns`** na configuração

Consulte o arquivo `.llmsignore.example` para um modelo inicial.

## Formato de Saída

O arquivo `llms.txt` compilado segue esta estrutura:

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

## Comandos da Linha de Comando (CLI)

| Comando | Descrição |
|---------|-------------|
| `llm-sync-drive init` | Cria o arquivo de configuração padrão |
| `llm-sync-drive auth` | Autentica com o Google Drive |
| `llm-sync-drive sync` | Compila e envia (uma única vez) |
| `llm-sync-drive serve` | Modo de observação com sincronização automática |
| `llm-sync-drive compile` | Compila localmente (sem envio) |

Todos os comandos aceitam `-v` / `--verbose` para registro de depuração.

## Observações de Segurança

- Os arquivos **`credentials.json`** e **`token.json`** estão no `.gitignore` — nunca os inclua no repositório.
- O aplicativo usa o escopo `drive.file` (pode acessar apenas os arquivos que ele cria, não todo o seu Google Drive).
- O arquivo `.llmsignore` oferece uma camada adicional de proteção contra a inclusão de informações confidenciais na saída compilada.
- As regras internas sempre excluem `.env`, `*.key`, `*.pem`, etc.

## Licença

MIT

---

Desenvolvido por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a
