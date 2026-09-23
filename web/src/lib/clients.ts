import type { ClientData } from './types';

// Every export the pipeline writes to src/lib/data is bundled at build time: a new
// client shows up in the switcher without touching this file.
const files = import.meta.glob<ClientData>('./data/*.json', { eager: true, import: 'default' });

export const clients: ClientData[] = Object.values(files).sort((a, b) =>
	a.client.name.localeCompare(b.client.name)
);
