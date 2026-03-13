<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

Compila il tuo repository in un file strutturato `llms.txt` e sincronizzalo automaticamente con Google Drive, in modo che modelli linguistici come Gemini possano accedere al contesto più recente tramite `@Google Drive`.

## Cosa fa

1. **Compila** il tuo repository in un singolo documento Markdown strutturato (albero delle directory + contenuto dei file).
2. **Rispetta** i file `.gitignore` e `.llmsignore` per escludere elementi non necessari, segreti e file binari.
3. **Carica** il contenuto in un singolo file di Google Drive (operazione idempotente: lo stesso link viene utilizzato ogni volta).
4. **Monitora** le modifiche e sincronizza automaticamente con un intervallo configurabile.

## Guida rapida

### 1. Installazione

```bash
pip install -e .
```

### 2. Configurazione dell'API di Google Drive

1. Vai alla [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un progetto (o utilizza uno esistente)
3. Vai a **API e servizi → Libreria**, cerca **API di Google Drive** e **attivala**.

#### Opzione A: Credenziali predefinite dell'applicazione (consigliata, più semplice)

4. Installa la [CLI di gcloud](https://cloud.google.com/sdk/docs/install) se non l'hai già installata.
5. Esegui:
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. Si apre un browser per l'autorizzazione: accedi con il tuo account Google.
7. Fatto. Non è necessario un file di credenziali. Il token ADC viene memorizzato nella cache in `%APPDATA%/gcloud/application_default_credentials.json` (Windows) o in `~/.config/gcloud/application_default_credentials.json` (macOS/Linux).

#### Opzione B: Account di servizio (file di chiave senza interfaccia utente)

4. Vai a **API e servizi → Credenziali**
5. Clicca su **+ Crea credenziali → Account di servizio**
6. Assegna un nome (ad esempio, `mcp-drive-sync`) e clicca su **Crea e continua**, quindi su **Fatto**.
7. Copia l'indirizzo email dell'account di servizio (ad esempio, `mcp-drive-sync@your-project.iam.gserviceaccount.com`).
8. Clicca sull'account di servizio → scheda **Chiavi** → **Aggiungi chiave → Crea nuova chiave → JSON**.
9. Salva il file scaricato come `credentials.json` nella directory del tuo repository.
10. Nel tuo **Google Drive personale**, crea una cartella (ad esempio, `MCP-Context-Sync`).
11. **Condividi** questa cartella con l'indirizzo email dell'account di servizio (con permessi di scrittura).
12. Copia l'**ID della cartella** dall'URL della cartella (la stringa dopo `folders/`).

#### Opzione C: OAuth 2.0 (interattiva, per l'uso da riga di comando)

4. Vai a **API e servizi → Schermata di consenso OAuth**, imposta su "Esterno", aggiungi il tuo indirizzo email come utente di test.
5. Vai a **Credenziali → + Crea credenziali → ID client OAuth** (app desktop).
6. Scarica il file JSON e salvalo come `credentials.json`.

### 3. Inizializzazione della configurazione

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

Questo crea il file `llm-sync-drive.yaml`. Modificalo per impostare:

- `auth_mode`: `"adc"` (predefinito), `"service-account"` o `"oauth"`.
- `credentials_path`: il percorso del tuo file `credentials.json` (solo per le modalità account di servizio/OAuth).
- `drive_folder_id`: l'ID della cartella di Google Drive (dall'URL della cartella).
- `project_description`: una breve descrizione del tuo progetto.

### 4. Autenticazione (solo per OAuth)

Se utilizzi la modalità OAuth, esegui:

```bash
llm-sync-drive auth
```

Si apre un browser per l'autorizzazione. Il token viene memorizzato in `token.json`. Le modalità ADC e account di servizio non richiedono una fase di autenticazione.

### 5. Sincronizzazione iniziale

```bash
llm-sync-drive sync
```

Compila e carica. L'ID del file di Drive viene salvato automaticamente nella configurazione.

### 6. Modalità di monitoraggio

```bash
llm-sync-drive serve
```

Esegue una sincronizzazione iniziale, quindi monitora il repository. Dopo che i file smettono di cambiare per l'intervallo di debounce (predefinito 5 secondi), ricompila e carica.

### 7. Anteprima locale

```bash
llm-sync-drive compile -o llms.txt
```

Compila in un file locale senza caricamento. Utile per l'ispezione.

## Server MCP (integrazione con l'assistente AI)

`llm-sync-drive` funziona come un **server MCP (Model Context Protocol)**, quindi gli assistenti AI come GitHub Copilot possono sincronizzare i tuoi repository con Drive direttamente durante una conversazione.

### Configurazione di VS Code

Aggiungi alle impostazioni utente di VS Code o al file `.vscode/mcp.json` del workspace:

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

Oppure, imposta le variabili d'ambiente per un funzionamento senza configurazione:

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

| Strumento | Descrizione |
|------|-------------|
| `sync_to_drive` | Compila il repository e caricalo su Drive. Utilizzare dopo ogni fase/traguardo. |
| `compile_context` | Compila localmente senza caricamento (anteprima o salvataggio di uno snapshot). |
| `sync_status` | Verifica la configurazione, l'ID del file di Drive e lo stato di autenticazione. |
| `list_repos` | Trova i repository con configurazioni di sincronizzazione esistenti. |

### Variabili d'ambiente

| Variabile | Descrizione |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Percorso del file YAML di configurazione (rilevato automaticamente nella root del repository, altrimenti). |
| `LLM_SYNC_DRIVE_FILE_ID` | ID del file di Drive (sovrascrive la configurazione). |
| `LLM_SYNC_DRIVE_FOLDER_ID` | ID della cartella di Drive (sovrascrive la configurazione). |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Percorso del file `credentials.json` (sovrascrive la configurazione). |
| `LLM_SYNC_DRIVE_TOKEN` | Percorso del file `token.json` (sovrascrive la configurazione). |

## Configurazione

Tutte le opzioni si trovano in `llm-sync-drive.yaml`:

| Chiave | Descrizione | Valore predefinito |
|-----|-------------|---------|
| `repo_path` | Percorso del repository | obbligatorio |
| `auth_mode` | `"adc"` (il più semplice), `"service-account"` (file chiave), oppure `"oauth"` (interattivo) | `adc` |
| `credentials_path` | File chiave del servizio o credenziali OAuth in formato JSON | `credentials.json` |
| `token_path` | Token OAuth memorizzato nella cache (solo in modalità OAuth) | `token.json` |
| `drive_folder_id` | Cartella di Drive in cui caricare i file | `null` |
| `drive_file_id` | ID del file di Drive (impostato automaticamente dopo il primo caricamento) | `null` |
| `drive_filename` | Nome del file su Drive | `llms.txt` |
| `local_output` | Salva anche localmente | `null` |
| `project_description` | Testo di intestazione nell'output compilato | `""` |
| `debounce_seconds` | Tempo di attesa dopo l'ultima modifica | `5.0` |
| `max_file_bytes` | Ignora i file più grandi di questo | `100000` |
| `include_extensions` | Includi solo queste estensioni | `[]` (tutti i file di testo) |
| `extra_ignore_patterns` | Modelli aggiuntivi da ignorare | `[]` |

## Regole di esclusione

I file vengono esclusi (in ordine) da:

1. **Regole integrate**: `.git/`, `node_modules/`, `__pycache__/`, file di lock, file segreti
2. **`.gitignore`**: Modelli standard di git per l'esclusione
3. **`.llmsignore`**: Modelli aggiuntivi specifici per il contesto LLM (ad esempio, fixture di test, risorse binarie)
4. **`extra_ignore_patterns`** nella configurazione

Consulta il file `.llmsignore.example` per un modello di esempio.

## Formato di output

Il file `llms.txt` compilato segue questa struttura:

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

## Comandi CLI

| Comando | Descrizione |
|---------|-------------|
| `llm-sync-drive init` | Crea il file di configurazione predefinito |
| `llm-sync-drive auth` | Autenticati con Google Drive |
| `llm-sync-drive sync` | Compilazione e caricamento in un'unica operazione |
| `llm-sync-drive serve` | Modalità di monitoraggio con sincronizzazione automatica |
| `llm-sync-drive compile` | Compila localmente (senza caricamento) |

Tutti i comandi accettano `-v` / `--verbose` per la registrazione di debug.

## Note sulla sicurezza

- I file **`credentials.json`** e **`token.json`** sono inclusi in `.gitignore` — non commetterli mai
- L'applicazione utilizza l'ambito `drive.file` (può accedere solo ai file che crea, non all'intero Drive)
- Il file `.llmsignore` fornisce una protezione aggiuntiva contro la divulgazione di segreti nell'output compilato
- Le regole integrate escludono sempre i file `.env`, `*.key`, `*.pem`, ecc.

## Licenza

MIT

---

Creato da <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a
