# Agent Sentinel Dashboard

Next.js dashboard for security events, agents, AI report analysis, and API key management. Built with TypeScript, Tailwind CSS, and shadcn/ui.

**Requires:** [Intelligence backend](../agent-sentinel-intelligence/) running on port 8001.

## Quick start

```bash
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8001' > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Sign up and copy the API key (shown once). Create more keys in **Settings**.

## Pages

| Page | Purpose |
|------|---------|
| Dashboard | System health, severity breakdown, recent events |
| Agents | Agent list with event counts, detail view |
| Reports | Upload SDK reports for AI analysis, export PDF/JSON |
| Settings | API key management (create, revoke) |

## Docs

- [Main README](../README.md) — project overview, getting started
- [System Design](../SYSTEM_DESIGN.md) — frontend architecture, data flows
