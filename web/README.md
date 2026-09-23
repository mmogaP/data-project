# Dashboard

SvelteKit on Cloudflare. Minimal, no chart library: the charts are hand-written SVG.

## How data gets here

The pipeline's last asset (`<client>/dashboard_data`) reads the client's marts from the
warehouse and writes `src/lib/data/<client_id>.json` — a few KB of pre-aggregated rows.
The site bundles those files at build time and is fully prerendered, so:

- no warehouse credentials live in Cloudflare,
- no warehouse query runs per page view,
- the page is static assets served from the edge.

Adding a client adds a JSON file; `src/lib/clients.ts` globs the folder, so the client
switcher picks it up with no code change.

## Commands

```bash
pnpm install
pnpm run dev        # http://localhost:5173
pnpm run check      # svelte-check
pnpm run build      # → .svelte-kit/cloudflare
pnpm run preview
```

Refresh the data first with `uv run dagster asset materialize -m dataplatform.orchestration.definitions --select 'hudson_bank/dashboard_data' --partition <day>`,
or straight from Python: `uv run python -c "from dataplatform.config import load_clients; from dataplatform.export import export_client; export_client(load_clients()[0])"`.

## Deploy

`pnpm dlx wrangler deploy` with the included `wrangler.jsonc`, or point Cloudflare Workers
Builds at this repo (root directory `web`, build `pnpm run build`).

## Design notes

- Colors come from a validated palette: one blue for data, neutral ink for text, and a
  reserved status palette for pipeline health. Status never rides on color alone — each
  state ships with an icon and a label.
- Single-series charts, so no legend; the title names what is plotted.
- Every chart has a table view, and dark mode is a separate set of steps, not an inversion.

## Not done yet

- Per-client access (Cloudflare Access) — today anyone with the URL sees everything.
- Charts per product/state with filters.
- A full pipeline-health page (run history, test results), rather than one status strip.
