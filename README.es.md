<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.md">English</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

Compile tu repositorio en un archivo estructurado `llms.txt` y sincronízalo automáticamente con Google Drive, para que modelos de lenguaje como Gemini puedan obtener información actualizada a través de `@Google Drive`.

## ¿Qué hace?

1. **Compila** tu repositorio en un único documento Markdown estructurado (árbol de directorios + contenido de los archivos).
2. **Respeta** los archivos `.gitignore` y `.llmsignore` para excluir elementos innecesarios, secretos y archivos binarios.
3. **Sube** el contenido a un único archivo de Google Drive (idempotente: el mismo enlace cada vez).
4. **Monitorea** los cambios y sincroniza automáticamente con un intervalo de espera configurable.

## Cómo empezar

### 1. Instala

```bash
pip install -e .
```

### 2. Configura la API de Google Drive

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto (o utiliza uno existente).
3. Navega a **APIs & Services → Library**, busca **Google Drive API** y **actívalo**.

#### Opción A: Credenciales predeterminadas de la aplicación (Recomendada: la más sencilla)

4. Instala la [gcloud CLI](https://cloud.google.com/sdk/docs/install) si no la tienes.
5. Ejecuta:
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. Se abrirá un navegador para la autorización: inicia sesión con tu cuenta de Google.
7. ¡Listo! No se necesita un archivo de credenciales. El token de ADC se guarda en `%APPDATA%/gcloud/application_default_credentials.json` (Windows) o `~/.config/gcloud/application_default_credentials.json` (macOS/Linux).

#### Opción B: Cuenta de servicio (archivo de clave sin interfaz)

4. Ve a **APIs & Services → Credentials**.
5. Haz clic en **+ Create Credentials → Service account**.
6. Asigna un nombre (por ejemplo, `mcp-drive-sync`) y haz clic en **Create and Continue**, luego en **Done**.
7. Copia la dirección de correo electrónico de la cuenta de servicio (por ejemplo, `mcp-drive-sync@your-project.iam.gserviceaccount.com`).
8. Haz clic en la cuenta de servicio → pestaña **Keys** → **Add Key → Create new key → JSON**.
9. Guarda el archivo descargado como `credentials.json` en el directorio de tu repositorio.
10. En tu **Google Drive personal**, crea una carpeta (por ejemplo, `MCP-Context-Sync`).
11. **Comparte** esa carpeta con la dirección de correo electrónico de la cuenta de servicio (con permisos de Editor).
12. Copia el **ID de la carpeta** de la URL de la carpeta (la cadena después de `folders/`).

#### Opción C: OAuth 2.0 (Interactiva, para uso en la línea de comandos)

4. Ve a **APIs & Services → OAuth consent screen**, configúralo como "External" y agrega tu dirección de correo electrónico como usuario de prueba.
5. Ve a **Credentials → + Create Credentials → OAuth client ID** (aplicación de escritorio).
6. Descarga el archivo JSON y guárdalo como `credentials.json`.

### 3. Inicializa la configuración

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

Esto crea `llm-sync-drive.yaml`. Edítalo para establecer:

- `auth_mode`: `"adc"` (por defecto), `"service-account"` o `"oauth"`.
- `credentials_path`: la ruta a tu archivo `credentials.json` (solo para los modos de cuenta de servicio y OAuth).
- `drive_folder_id`: el ID de la carpeta de Google Drive (de la URL de la carpeta).
- `project_description`: una breve descripción de tu proyecto.

### 4. Autentícate (solo para OAuth)

Si utilizas el modo OAuth, ejecuta:

```bash
llm-sync-drive auth
```

Se abrirá un navegador para la autorización. El token se guarda en `token.json`. Los modos ADC y de cuenta de servicio no requieren un paso de autenticación.

### 5. Sincroniza una vez

```bash
llm-sync-drive sync
```

Compila y sube. El ID del archivo de Drive se guarda automáticamente en tu configuración.

### 6. Modo de monitoreo

```bash
llm-sync-drive serve
```

Realiza una sincronización inicial y luego monitorea el repositorio. Después de que los archivos dejen de cambiar durante el intervalo de espera (por defecto, 5 segundos), se vuelve a compilar y se vuelve a subir.

### 7. Vista previa local

```bash
llm-sync-drive compile -o llms.txt
```

Compila a un archivo local sin subirlo. Útil para inspeccionar.

## Servidor MCP (Integración con asistente de IA)

`llm-sync-drive` se ejecuta como un **servidor MCP (Model Context Protocol)**, lo que permite que asistentes de IA como GitHub Copilot sincronicen tus repositorios con Drive directamente durante una conversación.

### Configuración de VS Code

Agregue lo siguiente a la configuración de usuario de VS Code o al archivo `.vscode/mcp.json` de su espacio de trabajo:

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

O bien, configure variables de entorno para un funcionamiento sin configuración:

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

### Herramientas MCP

| Herramienta | Descripción |
|------|-------------|
| `sync_to_drive` | Compila el repositorio y súbelo a Google Drive. Úselo después de cada fase/hito. |
| `compile_context` | Compila localmente sin subir (vista previa o guardar una instantánea). |
| `sync_status` | Verifica la configuración, el ID del archivo de Google Drive y el estado de autenticación. |
| `list_repos` | Encuentra repositorios con configuraciones de sincronización existentes. |

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Ruta al archivo YAML de configuración (se detecta automáticamente en la raíz del repositorio, de lo contrario). |
| `LLM_SYNC_DRIVE_FILE_ID` | ID del archivo de Google Drive (anula la configuración). |
| `LLM_SYNC_DRIVE_FOLDER_ID` | ID de la carpeta de Google Drive (anula la configuración). |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Ruta al archivo `credentials.json` (anula la configuración). |
| `LLM_SYNC_DRIVE_TOKEN` | Ruta al archivo `token.json` (anula la configuración). |

## Configuración

Todas las opciones se encuentran en `llm-sync-drive.yaml`:

| Clave | Descripción | Valor predeterminado |
|-----|-------------|---------|
| `repo_path` | Ruta al repositorio | obligatorio |
| `auth_mode` | `"adc"` (más simple), `"service-account"` (archivo de clave) o `"oauth"` (interactivo) | `adc` |
| `credentials_path` | Archivo JSON de la cuenta de servicio o las credenciales de OAuth. | `credentials.json` |
| `token_path` | Token de OAuth almacenado en caché (solo en modo OAuth). | `token.json` |
| `drive_folder_id` | Carpeta de Google Drive donde se subirán los archivos. | `null` |
| `drive_file_id` | ID del archivo de Google Drive (se establece automáticamente después de la primera subida). | `null` |
| `drive_filename` | Nombre de archivo en Google Drive. | `llms.txt` |
| `local_output` | También guardar localmente. | `null` |
| `project_description` | Texto de encabezado en la salida compilada. | `""` |
| `debounce_seconds` | Tiempo de espera después del último cambio. | `5.0` |
| `max_file_bytes` | Omitir archivos más grandes que este. | `100000` |
| `include_extensions` | Incluir solo estas extensiones. | `[]` (todos los archivos de texto) |
| `extra_ignore_patterns` | Patrones adicionales a ignorar. | `[]` |

## Reglas de exclusión

Los archivos se excluyen (en orden) de la siguiente manera:

1. **Reglas integradas**: `.git/`, `node_modules/`, `__pycache__/`, archivos de bloqueo, archivos secretos.
2. **`.gitignore`**: Patrones estándar de git para ignorar.
3. **`.llmsignore`**: Patrones adicionales específicos para el contexto de LLM (por ejemplo, fixtures de prueba, activos binarios).
4. **`extra_ignore_patterns`** en la configuración.

Consulte `.llmsignore.example` para obtener una plantilla de inicio.

## Formato de salida

El archivo `llms.txt` compilado sigue esta estructura:

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

## Comandos de la línea de comandos

| Comando | Descripción |
|---------|-------------|
| `llm-sync-drive init` | Crea el archivo de configuración predeterminado. |
| `llm-sync-drive auth` | Autentícate con Google Drive. |
| `llm-sync-drive sync` | Compilación y subida únicas. |
| `llm-sync-drive serve` | Modo de observación con sincronización automática. |
| `llm-sync-drive compile` | Compilación local (sin subida). |

Todos los comandos aceptan `-v` / `--verbose` para el registro de depuración.

## Notas de seguridad

- Los archivos **`credentials.json`** y **`token.json`** están en `.gitignore`: nunca los incluyas en el repositorio.
- La aplicación utiliza el alcance `drive.file` (solo puede acceder a los archivos que crea, no a toda tu cuenta de Google Drive).
- `.llmsignore` proporciona una capa adicional de seguridad para evitar que se filtren secretos en la salida compilada.
- Las reglas integradas siempre excluyen `.env`, `*.key`, `*.pem`, etc.

## Licencia

MIT

---

Creado por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
