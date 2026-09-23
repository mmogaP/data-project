<script lang="ts">
	import { compact, full } from '$lib/format';

	let { rows }: { rows: { label: string; value: number; note?: string }[] } = $props();

	let max = $derived(Math.max(...rows.map((r) => r.value)));
</script>

<ul>
	{#each rows as row (row.label)}
		<li title="{full(row.value)} complaints">
			<span class="name">{row.label}</span>
			<span class="track">
				<span class="bar" style="width: {(row.value / max) * 100}%"></span>
			</span>
			<span class="value">{compact(row.value)}</span>
			{#if row.note}<span class="note muted">{row.note}</span>{/if}
		</li>
	{/each}
</ul>

<style>
	ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	li {
		display: grid;
		grid-template-columns: minmax(0, 13rem) 1fr auto auto;
		align-items: center;
		gap: 10px;
	}

	.name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: 0.85rem;
		color: var(--ink-2);
	}

	.track {
		/* The track is the row's leftover air, not a drawn container. */
		display: block;
		height: 14px;
	}

	.bar {
		display: block;
		height: 100%;
		/* A long tail is normal here: keep tiny values visible instead of hairlines. */
		min-width: 3px;
		background: var(--series);
		border-radius: 0 4px 4px 0;
		transition: width 0.2s ease;
	}

	.value {
		font-size: 0.85rem;
		font-variant-numeric: tabular-nums;
		min-width: 3.2rem;
		text-align: right;
	}

	.note {
		min-width: 3.5rem;
		text-align: right;
	}

	@media (max-width: 620px) {
		li {
			grid-template-columns: 1fr auto;
			grid-template-areas: 'name value' 'track track';
			gap: 4px 10px;
		}

		.name {
			grid-area: name;
		}

		.value {
			grid-area: value;
		}

		.track {
			grid-area: track;
		}

		.note {
			display: none;
		}
	}
</style>
