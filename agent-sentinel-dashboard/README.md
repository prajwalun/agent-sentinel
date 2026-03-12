# Agent Sentinel Dashboard

Next.js web dashboard for visualizing security events, managing agents, running AI-powered report analysis, and managing API keys. Built with TypeScript, Tailwind CSS, and shadcn/ui.

## Quick start

```bash
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8001' > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Create an account and copy the API key shown on signup (it won't be shown again). To create more keys later, go to **Settings**.

Requires the [Intelligence backend](../agent-sentinel-intelligence/) to be running.

## Pages

- **Dashboard**: system health, severity breakdown, recent events
- **Agents**: agent list with event counts, detail view
- **Reports**: upload SDK reports for AI analysis, view history, export PDF/JSON
- **Settings**: API key management (create, revoke), preferences

## Docs

- [Main README](../README.md): project overview, getting started
- [System Design](../SYSTEM_DESIGN.md): frontend architecture, data flows
