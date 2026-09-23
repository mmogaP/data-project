/** Shape of the JSON written by `dataplatform.export.export_client`. */
export type ClientData = {
	client: { id: string; name: string; industry: string };
	generated_at: string;
	kpis: {
		complaints: number;
		companies: number;
		days_covered: number;
		timely_rate: number;
		avg_days_to_company: number;
		first_date: string;
		last_date: string;
	};
	daily: { date: string; complaints: number; timely: number }[];
	top_companies: { company: string; complaints: number; share_pct: number; timely_rate: number }[];
	products: { product: string; complaints: number }[];
	pipeline: {
		last_ingested_at: string;
		latest_partition: string;
		hours_since_ingest: number | null;
		sla_hours: number;
		status: 'good' | 'warning' | 'critical';
	};
};
