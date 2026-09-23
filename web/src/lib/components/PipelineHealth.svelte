<script lang="ts">
	import type { ClientData } from '$lib/types';

	let { pipeline, generatedAt }: { pipeline: ClientData['pipeline']; generatedAt: string } =
		$props();

	// Status never rides on color alone: every state ships with an icon and a label.
	const STATES = {
		good: { icon: '●', text: 'Within SLA' },
		warning: { icon: '▲', text: 'Approaching SLA' },
		critical: { icon: '■', text: 'SLA breached' }
	} as const;

	let state = $derived(STATES[pipeline.status]);
	let age = $derived(pipeline.hours_since_ingest);
</script>

<div class="health card">
	<span class="dot {pipeline.status}" aria-hidden="true">{state.icon}</span>
	<span class="text">
		<strong>{state.text}</strong>
		<span class="muted">
			{age === null ? 'never ingested' : `${age}h since last ingest`} · SLA {pipeline.sla_hours}h ·
			latest partition {pipeline.latest_partition}
		</span>
	</span>
	<span class="muted built">Data exported {generatedAt.replace('T', ' ').replace('+00:00', ' UTC')}</span>
</div>

<style>
	.health {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		flex-wrap: wrap;
	}

	.dot {
		font-size: 0.8rem;
		line-height: 1;
	}

	.good {
		color: var(--good);
	}

	.warning {
		color: var(--warning);
	}

	.critical {
		color: var(--critical);
	}

	.text {
		display: flex;
		flex-direction: column;
		font-size: 0.85rem;
		/* Keep the status icon and its label on one line; only the timestamp wraps. */
		flex: 1 1 240px;
	}

	.built {
		margin-left: auto;
	}
</style>
