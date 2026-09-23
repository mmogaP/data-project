<script lang="ts">
	import { compact, full, shortDate } from '$lib/format';

	let { points, label }: { points: { date: string; complaints: number }[]; label: string } =
		$props();

	const PAD = { top: 12, right: 16, bottom: 26, left: 44 };
	const HEIGHT = 220;

	let width = $state(720);
	let hovered: number | null = $state(null);

	/** Round the axis top to a clean number (1,000 / 2,000 / 30,000...). */
	function niceMax(value: number) {
		if (value <= 0) return 1;
		const magnitude = 10 ** Math.floor(Math.log10(value));
		return Math.ceil(value / magnitude) * magnitude;
	}

	let max = $derived(niceMax(Math.max(...points.map((p) => p.complaints))));
	let plotWidth = $derived(Math.max(width - PAD.left - PAD.right, 10));
	let plotHeight = $derived(HEIGHT - PAD.top - PAD.bottom);

	let x = $derived((i: number) =>
		points.length < 2 ? PAD.left + plotWidth / 2 : PAD.left + (i / (points.length - 1)) * plotWidth
	);
	let y = $derived((v: number) => PAD.top + plotHeight - (v / max) * plotHeight);

	let line = $derived(points.map((p, i) => `${x(i)},${y(p.complaints)}`).join(' '));
	let area = $derived(
		`${PAD.left},${PAD.top + plotHeight} ${line} ${x(points.length - 1)},${PAD.top + plotHeight}`
	);
	let ticks = $derived([0, max / 2, max]);
	// Enough labels to orient the reader, never so many that they collide.
	let labelEvery = $derived(Math.ceil(points.length / Math.max(Math.floor(width / 90), 2)));

	function onMove(event: PointerEvent) {
		const box = (event.currentTarget as SVGElement).getBoundingClientRect();
		const ratio = (event.clientX - box.left - PAD.left) / plotWidth;
		hovered = Math.min(points.length - 1, Math.max(0, Math.round(ratio * (points.length - 1))));
	}
</script>

<div class="wrapper" bind:clientWidth={width}>
	<svg
		{width}
		height={HEIGHT}
		role="img"
		aria-label="{label}: {points.length} days"
		onpointermove={onMove}
		onpointerleave={() => (hovered = null)}
	>
		{#each ticks as tick (tick)}
			<line class="grid" x1={PAD.left} x2={width - PAD.right} y1={y(tick)} y2={y(tick)} />
			<text class="tick" x={PAD.left - 8} y={y(tick) + 4} text-anchor="end">{compact(tick)}</text>
		{/each}

		<polygon class="area" points={area} />
		<polyline class="line" points={line} />

		{#each points as point, i (point.date)}
			{#if i % labelEvery === 0 || i === points.length - 1}
				<text class="tick" x={x(i)} y={HEIGHT - 8} text-anchor="middle">
					{shortDate(point.date)}
				</text>
			{/if}
		{/each}

		<!-- End marker: the one point worth calling out without labelling every day. -->
		<circle class="dot" cx={x(points.length - 1)} cy={y(points.at(-1)!.complaints)} r="4" />

		{#if hovered !== null}
			<line class="crosshair" x1={x(hovered)} x2={x(hovered)} y1={PAD.top} y2={PAD.top + plotHeight} />
			<circle class="dot" cx={x(hovered)} cy={y(points[hovered].complaints)} r="4" />
		{/if}
	</svg>

	{#if hovered !== null}
		<div
			class="tooltip card"
			style="left: {Math.min(Math.max(x(hovered), 70), width - 70)}px; top: {y(
				points[hovered].complaints
			) - 8}px"
		>
			<strong>{full(points[hovered].complaints)}</strong>
			<span class="muted">{shortDate(points[hovered].date)}</span>
		</div>
	{/if}
</div>

<style>
	.wrapper {
		position: relative;
		width: 100%;
	}

	svg {
		display: block;
		touch-action: none;
	}

	.grid {
		stroke: var(--grid);
		stroke-width: 1;
	}

	.tick {
		fill: var(--ink-muted);
		font-size: 11px;
		font-variant-numeric: tabular-nums;
	}

	.area {
		fill: var(--series);
		opacity: 0.1;
	}

	.line {
		fill: none;
		stroke: var(--series);
		stroke-width: 2;
		stroke-linejoin: round;
		stroke-linecap: round;
	}

	.dot {
		fill: var(--series);
		stroke: var(--surface);
		stroke-width: 2;
	}

	.crosshair {
		stroke: var(--axis);
		stroke-width: 1;
	}

	.tooltip {
		position: absolute;
		transform: translate(-50%, -100%);
		padding: 6px 10px;
		display: flex;
		flex-direction: column;
		line-height: 1.3;
		pointer-events: none;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
		font-variant-numeric: tabular-nums;
	}
</style>
