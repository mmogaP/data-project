<script lang="ts">
	import BarList from '$lib/components/BarList.svelte';
	import LineChart from '$lib/components/LineChart.svelte';
	import PipelineHealth from '$lib/components/PipelineHealth.svelte';
	import StatTile from '$lib/components/StatTile.svelte';
	import { clients } from '$lib/clients';
	import { compact, full, percent, shortDate } from '$lib/format';

	let selected = $state(clients[0]?.client.id ?? '');
	let data = $derived(clients.find((c) => c.client.id === selected) ?? clients[0]);

	let companyRows = $derived(
		data.top_companies.map((c) => ({
			label: c.company,
			value: c.complaints,
			note: `${c.share_pct.toFixed(1)}%`
		}))
	);
	let productRows = $derived(
		data.products.slice(0, 6).map((p) => ({ label: p.product, value: p.complaints }))
	);
</script>

<svelte:head>
	<title>{data.client.name} · Complaints</title>
	<meta name="description" content="CFPB complaint analytics for {data.client.name}" />
</svelte:head>

<main>
	<header>
		<div>
			<h1>{data.client.name}</h1>
			<p class="muted">
				CFPB consumer complaints · {shortDate(data.kpis.first_date)} – {shortDate(
					data.kpis.last_date
				)}
			</p>
		</div>
		{#if clients.length > 1}
			<label class="switcher">
				<span class="muted">Client</span>
				<select bind:value={selected}>
					{#each clients as client (client.client.id)}
						<option value={client.client.id}>{client.client.name}</option>
					{/each}
				</select>
			</label>
		{/if}
	</header>

	<PipelineHealth pipeline={data.pipeline} generatedAt={data.generated_at} />

	<section class="tiles">
		<StatTile label="Complaints" value={compact(data.kpis.complaints)} note={full(data.kpis.complaints)} />
		<StatTile label="Companies" value={full(data.kpis.companies)} note="with at least one complaint" />
		<StatTile label="Timely response" value={percent(data.kpis.timely_rate)} note="of all complaints" />
		<StatTile
			label="Days to company"
			value={data.kpis.avg_days_to_company.toFixed(2)}
			note="average, on receipt"
		/>
	</section>

	<section class="card">
		<h2>Complaints per day</h2>
		<p class="muted">All companies, by date received</p>
		<LineChart points={data.daily} label="Complaints per day" />
		<details>
			<summary>Table view</summary>
			<table>
				<thead>
					<tr><th>Date</th><th>Complaints</th><th>Timely</th></tr>
				</thead>
				<tbody>
					{#each data.daily as day (day.date)}
						<tr>
							<td>{day.date}</td>
							<td>{full(day.complaints)}</td>
							<td>{full(day.timely)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</details>
	</section>

	<div class="two-up">
		<section class="card">
			<h2>Top companies</h2>
			<p class="muted">Share of all complaints in the period</p>
			<BarList rows={companyRows} />
		</section>

		<section class="card">
			<h2>Products</h2>
			<p class="muted">Complaints by product category</p>
			<BarList rows={productRows} />
		</section>
	</div>

	<footer class="muted">
		Built from the <code>{data.client.id}</code> marts · source: CFPB Consumer Complaint Database
	</footer>
</main>

<style>
	main {
		max-width: 980px;
		margin: 0 auto;
		padding: 32px 16px 56px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		flex-wrap: wrap;
	}

	header p {
		margin: 2px 0 0;
	}

	.switcher {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	select {
		font: inherit;
		padding: 6px 8px;
		color: var(--ink);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: 8px;
	}

	.tiles {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
		gap: 12px;
	}

	.two-up {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: 16px;
	}

	h2 + p {
		margin: 2px 0 14px;
	}

	footer {
		text-align: center;
		margin-top: 8px;
	}
</style>
