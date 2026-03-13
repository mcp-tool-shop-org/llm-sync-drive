<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.md">English</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/llm-sync-drive/readme.png" width="400" alt="llm-sync-drive" />
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/llm-sync-drive/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/mcp-tool-shop-org/llm-sync-drive/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a>
  <a href="https://mcp-tool-shop-org.github.io/llm-sync-drive/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page" /></a>
</p>

अपने रिपॉजिटरी को एक संरचित `llms.txt` फ़ाइल में संकलित करें और इसे स्वचालित रूप से Google Drive पर सिंक करें - ताकि Gemini जैसे LLM (बड़े भाषा मॉडल) `@Google Drive` के माध्यम से ताज़ा संदर्भ प्राप्त कर सकें।

## यह क्या करता है

1. **संकलित** करता है आपके रिपॉजिटरी को एक एकल संरचित मार्कडाउन दस्तावेज़ में (डायरेक्टरी ट्री + फ़ाइल सामग्री)
2. **सम्मान** करता है `.gitignore` और `.llmsignore` को, ताकि अनावश्यक सामग्री, गुप्त जानकारी और बाइनरी फ़ाइलों को बाहर रखा जा सके।
3. **अपलोड** करता है एक एकल Google Drive फ़ाइल में (आइडेंपोटेंट - हर बार एक ही लिंक)
4. **निगरानी** करता है परिवर्तनों के लिए और स्वचालित रूप से कॉन्फ़िगर करने योग्य डिबाउंस के साथ फिर से सिंक करता है।

## शुरुआत कैसे करें

### 1. स्थापित करें

```bash
pip install -e .
```

### 2. Google Drive API सेट करें

1. [Google Cloud Console](https://console.cloud.google.com/) पर जाएं
2. एक प्रोजेक्ट बनाएं (या मौजूदा प्रोजेक्ट का उपयोग करें)
3. **APIs & Services → Library** पर जाएं, **Google Drive API** खोजें और इसे **सक्षम** करें।

#### विकल्प A: एप्लीकेशन डिफ़ॉल्ट क्रेडेंशियल्स (अनुशंसित - सबसे सरल)

4. यदि आपके पास नहीं है तो [gcloud CLI](https://cloud.google.com/sdk/docs/install) स्थापित करें।
5. चलाएं:
```bash
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
```
6. एक ब्राउज़र सहमति के लिए खुलता है - अपने Google खाते से साइन इन करें।
7. हो गया। किसी क्रेडेंशियल्स फ़ाइल की आवश्यकता नहीं है। ADC टोकन `%APPDATA%/gcloud/application_default_credentials.json` (Windows) या `~/.config/gcloud/application_default_credentials.json` (macOS/Linux) पर कैश किया गया है।

#### विकल्प B: सर्विस अकाउंट (हेडलेस कुंजी फ़ाइल)

4. **APIs & Services → Credentials** पर जाएं
5. **+ Create Credentials → Service account** पर क्लिक करें
6. इसका नाम दें (जैसे, `mcp-drive-sync`) और **Create and Continue**, फिर **Done** पर क्लिक करें।
7. सर्विस अकाउंट ईमेल कॉपी करें (जैसे, `mcp-drive-sync@your-project.iam.gserviceaccount.com`)
8. सर्विस अकाउंट पर क्लिक करें → **Keys** टैब → **Add Key → Create new key → JSON**
9. डाउनलोड की गई फ़ाइल को `credentials.json` के रूप में अपने रिपॉजिटरी डायरेक्टरी में सहेजें।
10. अपने **व्यक्तिगत Google Drive** में, एक फ़ोल्डर बनाएं (जैसे, `MCP-Context-Sync`)
11. उस फ़ोल्डर को सर्विस अकाउंट ईमेल के साथ **साझा** करें (एडिटर अनुमतियाँ)
12. फ़ोल्डर के URL से **फ़ोल्डर ID** कॉपी करें (फ़ोल्डर के नाम के बाद का स्ट्रिंग, जैसे `folders/`)

#### विकल्प C: OAuth 2.0 (इंटरैक्टिव, CLI उपयोग के लिए)

4. **APIs & Services → OAuth consent screen** पर जाएं, इसे External पर सेट करें, और अपना ईमेल एक परीक्षण उपयोगकर्ता के रूप में जोड़ें।
5. **Credentials → + Create Credentials → OAuth client ID** (Desktop app) पर जाएं।
6. JSON डाउनलोड करें और इसे `credentials.json` के रूप में सहेजें।

### 3. कॉन्फ़िगरेशन आरंभ करें

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

यह `llm-sync-drive.yaml` बनाता है। इसे संपादित करें ताकि आप निम्नलिखित सेट कर सकें:

- `auth_mode`: `"adc"` (डिफ़ॉल्ट), `"service-account"`, या `"oauth"`
- `credentials_path`: आपके `credentials.json` का पथ (केवल सर्विस-अकाउंट/OAuth मोड के लिए)
- `drive_folder_id`: Google Drive फ़ोल्डर ID (फ़ोल्डर के URL से)
- `project_description`: आपके प्रोजेक्ट के बारे में एक संक्षिप्त विवरण

### 4. प्रमाणित करें (केवल OAuth के लिए)

यदि आप OAuth मोड का उपयोग कर रहे हैं, तो चलाएं:

```bash
llm-sync-drive auth
```

यह सहमति के लिए एक ब्राउज़र खोलता है। टोकन `token.json` में कैश किया जाता है। ADC और सर्विस अकाउंट मोड को प्रमाणीकरण चरण की आवश्यकता नहीं होती है।

### 5. एक बार सिंक करें

```bash
llm-sync-drive sync
```

यह संकलित करता है और अपलोड करता है। Drive फ़ाइल ID स्वचालित रूप से आपके कॉन्फ़िगरेशन में सहेजी जाती है।

### 6. निगरानी मोड

```bash
llm-sync-drive serve
```

यह एक प्रारंभिक सिंक चलाता है, फिर रिपॉजिटरी की निगरानी करता है। फ़ाइलों के बदलने के बाद डिबाउंस अंतराल (डिफ़ॉल्ट 5 सेकंड) के लिए, यह फिर से संकलित और अपलोड करता है।

### 7. स्थानीय पूर्वावलोकन

```bash
llm-sync-drive compile -o llms.txt
```

यह स्थानीय फ़ाइल में संकलित करता है बिना अपलोड किए। निरीक्षण के लिए उपयोगी।

## MCP सर्वर (AI असिस्टेंट इंटीग्रेशन)

`llm-sync-drive` एक **MCP (मॉडल कॉन्टेक्स्ट प्रोटोकॉल) सर्वर** के रूप में चलता है, इसलिए GitHub Copilot जैसे AI असिस्टेंट सीधे बातचीत के दौरान आपके रिपॉजिटरी को Drive पर सिंक कर सकते हैं।

### VS Code सेटअप

अपने VS Code उपयोगकर्ता सेटिंग्स या वर्कस्पेस के `.vscode/mcp.json` में निम्नलिखित जोड़ें:

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

या, कॉन्फ़िगरेशन की आवश्यकता के बिना काम करने के लिए, पर्यावरण चर सेट करें:

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

### MCP उपकरण

| उपकरण | विवरण |
|------|-------------|
| `sync_to_drive` | रिपॉजिटरी को संकलित करें और इसे Google Drive पर अपलोड करें। प्रत्येक चरण/मील के पत्थर के बाद इसका उपयोग करें। |
| `compile_context` | बिना अपलोड किए स्थानीय रूप से संकलित करें (पूर्वावलोकन या स्नैपशॉट सहेजें)। |
| `sync_status` | कॉन्फ़िगरेशन, Google Drive फ़ाइल आईडी और प्रमाणीकरण स्थिति की जांच करें। |
| `list_repos` | मौजूदा सिंक कॉन्फ़िगरेशन वाली रिपॉजिटरी खोजें। |

### पर्यावरण चर

| चर | विवरण |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | कॉन्फ़िगरेशन YAML फ़ाइल का पथ (यदि नहीं तो रिपॉजिटरी रूट में स्वचालित रूप से खोजा जाता है) |
| `LLM_SYNC_DRIVE_FILE_ID` | Google Drive फ़ाइल आईडी (कॉन्फ़िगरेशन को ओवरराइड करें) |
| `LLM_SYNC_DRIVE_FOLDER_ID` | Google Drive फ़ोल्डर आईडी (कॉन्फ़िगरेशन को ओवरराइड करें) |
| `LLM_SYNC_DRIVE_CREDENTIALS` | `credentials.json` फ़ाइल का पथ (कॉन्फ़िगरेशन को ओवरराइड करें) |
| `LLM_SYNC_DRIVE_TOKEN` | `token.json` फ़ाइल का पथ (कॉन्फ़िगरेशन को ओवरराइड करें) |

## कॉन्फ़िगरेशन

सभी विकल्प `llm-sync-drive.yaml` में मौजूद हैं:

| कुंजी | विवरण | डिफ़ॉल्ट |
|-----|-------------|---------|
| `repo_path` | रिपॉजिटरी का पथ | आवश्यक |
| `auth_mode` | `"adc"` (सबसे सरल), `"service-account"` (की फ़ाइल), या `"oauth"` (इंटरैक्टिव) | `adc` |
| `credentials_path` | सर्विस अकाउंट की या OAuth क्रेडेंशियल JSON | `credentials.json` |
| `token_path` | कैश्ड OAuth टोकन (केवल oauth मोड में) | `token.json` |
| `drive_folder_id` | वह Google Drive फ़ोल्डर जिसमें अपलोड करना है | `null` |
| `drive_file_id` | Google Drive फ़ाइल आईडी (पहली अपलोड के बाद स्वचालित रूप से सेट हो जाती है) | `null` |
| `drive_filename` | Google Drive पर फ़ाइल का नाम | `llms.txt` |
| `local_output` | स्थानीय रूप से भी सहेजें | `null` |
| `project_description` | संकलित आउटपुट में हेडर टेक्स्ट | `""` |
| `debounce_seconds` | अंतिम परिवर्तन के बाद प्रतीक्षा समय | `5.0` |
| `max_file_bytes` | इस आकार से बड़ी फ़ाइलों को छोड़ दें | `100000` |
| `include_extensions` | केवल इन एक्सटेंशन को शामिल करें | `[]` (सभी टेक्स्ट फ़ाइलें) |
| `extra_ignore_patterns` | अतिरिक्त पैटर्न जिन्हें अनदेखा किया जाना है | `[]` |

## अस्वीकरण नियम

फ़ाइलें (क्रम में) निम्नलिखित द्वारा छोड़ी जाती हैं:

1. **अंतर्निहित नियम**: `.git/`, `node_modules/`, `__pycache__/`, लॉक फ़ाइलें, गुप्त फ़ाइलें
2. **`.gitignore`**: मानक git अनदेखा पैटर्न
3. **`.llmsignore`**: LLM संदर्भ के लिए विशिष्ट अतिरिक्त पैटर्न (जैसे, परीक्षण फिक्स्चर, बाइनरी एसेट)
4. **`extra_ignore_patterns`** कॉन्फ़िगरेशन में

शुरुआती टेम्पलेट के लिए `.llmsignore.example` देखें।

## आउटपुट प्रारूप

संकलित `llms.txt` इस संरचना का पालन करता है:

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

## CLI कमांड

| कमांड | विवरण |
|---------|-------------|
| `llm-sync-drive init` | डिफ़ॉल्ट कॉन्फ़िगरेशन फ़ाइल बनाएं |
| `llm-sync-drive auth` | Google Drive के साथ प्रमाणीकरण करें |
| `llm-sync-drive sync` | एक बार संकलन + अपलोड करें |
| `llm-sync-drive serve` | ऑटो-सिंक के साथ वॉच मोड |
| `llm-sync-drive compile` | स्थानीय रूप से संकलित करें (अपलोड नहीं) |

सभी कमांड डिबग लॉगिंग के लिए `-v` / `--verbose` स्वीकार करते हैं।

## सुरक्षा नोट्स

- **`credentials.json`** और **`token.json`** `.gitignore` में हैं - कभी भी उन्हें कमिट न करें
- ऐप `drive.file` स्कोप का उपयोग करता है (यह केवल उन फ़ाइलों तक पहुंच सकता है जिन्हें यह बनाता है, न कि आपके पूरे Google Drive तक)
- `.llmsignore` संकलित आउटपुट में गुप्त जानकारी लीक होने से बचाव करता है।
- अंतर्निहित नियम हमेशा `.env`, `*.key`, `*.pem`, आदि को छोड़ देते हैं।

## लाइसेंस

MIT

---

<a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a> द्वारा बनाया गया
