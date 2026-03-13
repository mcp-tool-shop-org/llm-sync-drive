<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.md">English</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

Compilez votre dépôt en un fichier structuré `llms.txt` et synchronisez-le automatiquement avec Google Drive, afin que les LLM comme Gemini puissent récupérer le contexte le plus récent via `@Google Drive`.

## Fonctionnalités

1. **Compile** votre dépôt en un seul document Markdown structuré (arborescence des répertoires + contenu des fichiers).
2. **Respecte** les fichiers `.gitignore` et `.llmsignore` pour exclure les éléments inutiles, les secrets et les binaires.
3. **Télécharge** le contenu vers un seul fichier Google Drive (opération idempotente : le même lien est utilisé à chaque fois).
4. **Surveille** les modifications et effectue une nouvelle synchronisation automatiquement, avec un intervalle de délai configurable.

## Premiers pas

### 1. Installation

```bash
pip install -e .
```

### 2. Configuration de l'API Google Drive

1. Accédez à la [console Google Cloud](https://console.cloud.google.com/).
2. Créez un projet (ou utilisez un projet existant).
3. Accédez à **APIs et services → Bibliothèque**, recherchez **Google Drive API** et **activez-le**.

#### Option A : Identifiants par défaut de l'application (recommandé - le plus simple)

4. Installez l'outil de ligne de commande [gcloud](https://cloud.google.com/sdk/docs/install) si vous ne l'avez pas.
5. Exécutez la commande suivante :
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. Un navigateur s'ouvre pour l'autorisation. Connectez-vous avec votre compte Google.
7. Terminé. Aucun fichier d'informations d'identification n'est nécessaire. Le jeton ADC est enregistré dans `%APPDATA%/gcloud/application_default_credentials.json` (Windows) ou `~/.config/gcloud/application_default_credentials.json` (macOS/Linux).

#### Option B : Compte de service (fichier de clé sans tête)

4. Accédez à **APIs et services → Informations d'identification**.
5. Cliquez sur **+ Créer des informations d'identification → Compte de service**.
6. Donnez-lui un nom (par exemple, `mcp-drive-sync`) et cliquez sur **Créer et continuer**, puis sur **Terminé**.
7. Copiez l'adresse e-mail du compte de service (par exemple, `mcp-drive-sync@your-project.iam.gserviceaccount.com`).
8. Cliquez sur le compte de service → onglet **Clés** → **Ajouter une clé → Créer une clé JSON**.
9. Enregistrez le fichier téléchargé sous le nom `credentials.json` dans le répertoire de votre dépôt.
10. Dans votre **Google Drive personnel**, créez un dossier (par exemple, `MCP-Context-Sync`).
11. **Partagez** ce dossier avec l'adresse e-mail du compte de service (autorisations d'éditeur).
12. Copiez l'**ID du dossier** à partir de l'URL du dossier (la chaîne après `folders/`).

#### Option C : OAuth 2.0 (interactif, pour l'utilisation en ligne de commande)

4. Accédez à **APIs et services → Écran de consentement OAuth**, configurez-le en mode "Externe", ajoutez votre adresse e-mail en tant qu'utilisateur de test.
5. Accédez à **Informations d'identification → + Créer des informations d'identification → ID client OAuth** (application de bureau).
6. Téléchargez le fichier JSON et enregistrez-le sous le nom `credentials.json`.

### 3. Initialisation de la configuration

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

Cela crée le fichier `llm-sync-drive.yaml`. Modifiez-le pour définir les paramètres suivants :

- `auth_mode`: `"adc"` (par défaut), `"service-account"` ou `"oauth"`.
- `credentials_path`: chemin d'accès à votre fichier `credentials.json` (modes "service-account" et "oauth" uniquement).
- `drive_folder_id`: l'ID du dossier Google Drive (à partir de l'URL du dossier).
- `project_description`: une brève description de votre projet.

### 4. Authentification (OAuth uniquement)

Si vous utilisez le mode OAuth, exécutez la commande suivante :

```bash
llm-sync-drive auth
```

Ouvre un navigateur pour l'autorisation. Le jeton est enregistré dans `token.json`. Les modes ADC et compte de service ne nécessitent aucune étape d'authentification.

### 5. Synchronisation unique

```bash
llm-sync-drive sync
```

Compile et télécharge le contenu. L'ID du fichier Drive est enregistré automatiquement dans votre fichier de configuration.

### 6. Mode de surveillance

```bash
llm-sync-drive serve
```

Effectue une synchronisation initiale, puis surveille le dépôt. Après que les fichiers ont cessé de changer pendant l'intervalle de délai (par défaut, 5 secondes), il recompile et télécharge le contenu.

### 7. Prévisualisation locale

```bash
llm-sync-drive compile -o llms.txt
```

Compile le contenu dans un fichier local sans le télécharger. Utile pour l'inspection.

## Serveur MCP (intégration de l'assistant IA)

`llm-sync-drive` fonctionne en tant que **serveur MCP (Model Context Protocol)**, ce qui permet aux assistants IA comme GitHub Copilot de synchroniser directement vos dépôts avec Drive pendant une conversation.

### Configuration de VS Code

Ajoutez les paramètres suivants à votre configuration utilisateur VS Code ou au fichier `.vscode/mcp.json` de votre espace de travail :

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

Ou définissez des variables d'environnement pour une utilisation sans configuration :

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

### Outils MCP

| Outil | Description |
|------|-------------|
| `sync_to_drive` | Compile le dépôt et télécharge-le sur Google Drive. À utiliser après chaque phase/étape. |
| `compile_context` | Compile localement sans téléchargement (aperçu ou sauvegarde d'une copie). |
| `sync_status` | Vérifie la configuration, l'ID du fichier Google Drive et le statut d'authentification. |
| `list_repos` | Recherche les dépôts avec des configurations de synchronisation existantes. |

### Variables d'environnement

| Variable | Description |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Chemin vers le fichier YAML de configuration (détecté automatiquement à la racine du dépôt, sinon). |
| `LLM_SYNC_DRIVE_FILE_ID` | ID du fichier Google Drive (remplace la configuration). |
| `LLM_SYNC_DRIVE_FOLDER_ID` | ID du dossier Google Drive (remplace la configuration). |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Chemin vers le fichier `credentials.json` (remplace la configuration). |
| `LLM_SYNC_DRIVE_TOKEN` | Chemin vers le fichier `token.json` (remplace la configuration). |

## Configuration

Toutes les options se trouvent dans le fichier `llm-sync-drive.yaml` :

| Clé | Description | Valeur par défaut |
|-----|-------------|---------|
| `repo_path` | Chemin vers le dépôt | obligatoire |
| `auth_mode` | `"adc"` (le plus simple), `"service-account"` (fichier de clé), ou `"oauth"` (interactif) | `adc` |
| `credentials_path` | Fichier de clé de compte de service ou informations d'identification OAuth JSON | `credentials.json` |
| `token_path` | Jeton OAuth mis en cache (mode OAuth uniquement) | `token.json` |
| `drive_folder_id` | Dossier Google Drive dans lequel les fichiers sont téléchargés | `null` |
| `drive_file_id` | ID du fichier Google Drive (définie automatiquement après le premier téléchargement) | `null` |
| `drive_filename` | Nom de fichier sur Google Drive | `llms.txt` |
| `local_output` | Enregistrer également localement | `null` |
| `project_description` | Texte d'en-tête dans la sortie compilée | `""` |
| `debounce_seconds` | Temps d'attente après le dernier changement | `5.0` |
| `max_file_bytes` | Ignore les fichiers de plus cette taille | `100000` |
| `include_extensions` | Inclure uniquement ces extensions | `[]` (tous les fichiers texte) |
| `extra_ignore_patterns` | Modèles supplémentaires à ignorer | `[]` |

## Règles d'exclusion

Les fichiers sont exclus (dans l'ordre) par :

1. **Règles intégrées** : `.git/`, `node_modules/`, `__pycache__/`, fichiers de verrouillage, fichiers secrets
2. **`.gitignore`** : Modèles d'exclusion standard de Git
3. **`.llmsignore`** : Modèles supplémentaires spécifiques au contexte LLM (par exemple, fixtures de test, ressources binaires)
4. **`extra_ignore_patterns`** dans la configuration

Consultez le fichier `.llmsignore.example` pour un modèle de base.

## Format de sortie

Le fichier `llms.txt` compilé suit cette structure :

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

## Commandes CLI

| Commande | Description |
|---------|-------------|
| `llm-sync-drive init` | Crée un fichier de configuration par défaut |
| `llm-sync-drive auth` | S'authentifie auprès de Google Drive |
| `llm-sync-drive sync` | Compilation et téléchargement en une seule étape |
| `llm-sync-drive serve` | Mode surveillance avec synchronisation automatique |
| `llm-sync-drive compile` | Compile localement (sans téléchargement) |

Toutes les commandes acceptent `-v` / `--verbose` pour la journalisation de débogage.

## Notes de sécurité

- Les fichiers **`credentials.json`** et **`token.json`** sont inclus dans `.gitignore` — ne les ajoutez jamais à votre dépôt.
- L'application utilise la portée `drive.file` (elle peut uniquement accéder aux fichiers qu'elle crée, et non à l'ensemble de votre Google Drive).
- Le fichier `.llmsignore` offre une protection supplémentaire contre la fuite de secrets dans la sortie compilée.
- Les règles intégrées excluent toujours les fichiers `.env`, `*.key`, `*.pem`, etc.

## Licence

MIT

---

Développé par <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
