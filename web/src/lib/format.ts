export const compact = (n: number) =>
	new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n);

export const full = (n: number) => new Intl.NumberFormat('en-US').format(n);

export const percent = (rate: number, digits = 1) =>
	`${(rate * 100).toFixed(digits)}%`;

/** "2026-09-05" -> "Sep 5" (parsed as UTC so the label never shifts by timezone). */
export const shortDate = (iso: string) =>
	new Date(`${iso}T00:00:00Z`).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		timeZone: 'UTC'
	});
