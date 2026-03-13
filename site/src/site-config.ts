import type { SiteConfig } from '@mcptoolshop/site-theme';

export const config: SiteConfig = {
  title: 'llm-sync-drive',
  description: 'Compile llms.txt from a repo and sync it to Google Drive',
  logoBadge: 'LS',
  brandName: 'llm-sync-drive',
  repoUrl: 'https://github.com/mcp-tool-shop-org/llm-sync-drive',
  footerText: 'MIT Licensed — built by <a href="https://mcp-tool-shop.github.io/" style="color:var(--color-muted);text-decoration:underline">MCP Tool Shop</a>',

  hero: {
    badge: 'Open source',
    headline: 'llm-sync-drive',
    headlineAccent: 'repo context for LLMs.',
    description: 'Compile your repository into a structured llms.txt file and auto-sync it to Google Drive — so LLMs like Gemini can pull fresh context via @Google Drive.',
    primaryCta: { href: '#usage', label: 'Get started' },
    secondaryCta: { href: 'handbook/', label: 'Read the Handbook' },
    previews: [
      { label: 'Install', code: 'pip install llm-sync-drive' },
      { label: 'Init', code: 'llm-sync-drive init --repo .' },
      { label: 'Sync', code: 'llm-sync-drive sync' },
    ],
  },

  sections: [
    {
      kind: 'features',
      id: 'features',
      title: 'Features',
      subtitle: 'Keep your LLMs in sync with your codebase.',
      features: [
        { title: 'Compile', desc: 'Turns your repo into a single structured Markdown document with directory tree and file contents.' },
        { title: 'Sync', desc: 'Uploads to Google Drive with idempotent file IDs — same link every time, always fresh.' },
        { title: 'Watch', desc: 'Monitors your repo for changes and re-syncs automatically with configurable debounce.' },
        { title: 'MCP Server', desc: 'Runs as a Model Context Protocol server so AI assistants can trigger syncs directly.' },
        { title: 'Smart Filtering', desc: 'Respects .gitignore and .llmsignore to exclude noise, secrets, and binaries.' },
        { title: 'Flexible Auth', desc: 'Supports Application Default Credentials, service accounts, and OAuth 2.0.' },
      ],
    },
    {
      kind: 'code-cards',
      id: 'usage',
      title: 'Usage',
      cards: [
        { title: 'Install', code: 'pip install llm-sync-drive' },
        { title: 'Initialize', code: 'cd /path/to/repo\nllm-sync-drive init --repo .' },
        { title: 'One-shot sync', code: 'llm-sync-drive sync' },
        { title: 'Watch mode', code: 'llm-sync-drive serve' },
      ],
    },
    {
      kind: 'data-table',
      id: 'cli',
      title: 'CLI Commands',
      columns: ['Command', 'Description'],
      rows: [
        ['llm-sync-drive init', 'Create default config file'],
        ['llm-sync-drive auth', 'Authenticate with Google Drive (OAuth only)'],
        ['llm-sync-drive sync', 'One-shot compile + upload'],
        ['llm-sync-drive serve', 'Watch mode with auto-sync'],
        ['llm-sync-drive compile', 'Compile locally without uploading'],
      ],
    },
    {
      kind: 'data-table',
      id: 'mcp-tools',
      title: 'MCP Tools',
      columns: ['Tool', 'Description'],
      rows: [
        ['sync_to_drive', 'Compile repo + upload to Drive'],
        ['compile_context', 'Compile locally without uploading'],
        ['sync_status', 'Check config, Drive file ID, auth status'],
        ['list_repos', 'Find repos with existing sync configs'],
      ],
    },
  ],
};
