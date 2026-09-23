<script lang="ts">
	let { label, value, note = '' }: { label: string; value: string; note?: string } = $props();
</script>

<div class="tile card">
	<span class="label">{label}</span>
	<span class="value">{value}</span>
	{#if note}<span class="muted">{note}</span>{/if}
</div>

<style>
	.tile {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.label {
		color: var(--ink-2);
		font-size: 0.8rem;
	}

	.value {
		font-size: 1.8rem;
		font-weight: 600;
		letter-spacing: -0.02em;
	}
</style>
