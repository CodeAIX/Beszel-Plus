import { t } from "@lingui/core/macro"
import type { TrafficView } from "@/types"
import { trafficBytes, trafficProgress, trafficTimestamp } from "@/lib/traffic-display"

export function trafficStatusLabel(status: string) {
	switch (status) {
		case "ok":
			return t`Collected`
		case "unconfigured":
			return t`Choose an interface`
		case "disabled":
			return t`Disabled`
		case "vnstat_missing":
			return t`vnStat not installed`
		case "unsupported_timebase":
			return t`Verify UTC configuration`
		case "not_enabled":
			return t`Traffic not enabled`
		case "unsupported_platform":
			return t`Unsupported platform`
		case "initializing":
			return t`Initializing`
		case "no_database":
			return t`vnStat database unavailable`
		case "no_interfaces":
			return t`No monitored interfaces`
		case "permission_denied":
			return t`vnStat permission denied`
		case "exec_timeout":
			return t`vnStat query timed out`
		default:
			return t`Collection needs attention`
	}
}

export function TrafficUsageCell({ item, loading, error }: { item?: TrafficView; loading?: boolean; error?: boolean }) {
	if (!item)
		return (
			<span className="text-xs text-muted-foreground">
				{error ? t`Traffic unavailable` : loading ? t`Loading…` : "—"}
			</span>
		)
	const width = trafficProgress(item.percent)
	const unit = item.settings.display_unit
	const warning =
		error ||
		item.status !== "ok" ||
		item.system_status !== "up" ||
		item.freshness === "stale" ||
		item.coverage !== "complete" ||
		item.quality === "suspected_reset"
	const label = error
		? t`Update failed`
		: item.status !== "ok"
			? trafficStatusLabel(item.status)
			: item.quality === "suspected_reset"
				? t`Suspected counter reset`
				: item.system_status === "down"
					? t`Offline · last known`
					: item.system_status === "paused"
						? t`Paused · last known`
						: item.freshness === "stale"
							? t`Stale`
							: item.coverage === "partial"
								? t`Incomplete period`
								: t`Coverage unverified`
	const description = `${item.period_start} → ${item.period_end_exclusive} UTC · ${item.count_mode === "tx" ? t`Outbound only` : t`Received + sent`} · ${trafficTimestamp(item.last_success_at)} · ${item.error_code || label}`
	return (
		<div className="min-w-0 max-w-52 text-xs" title={description}>
			{item.used_bytes == null ? (
				<span className="text-muted-foreground">{trafficStatusLabel(item.status)}</span>
			) : (
				<>
					<div className="flex flex-wrap gap-x-1 tabular-nums">
						<span>{trafficBytes(item.used_bytes, unit)}</span>
						{item.quota_bytes > 0 && (
							<span className="text-muted-foreground">/ {trafficBytes(item.quota_bytes, unit)}</span>
						)}
						{item.percent != null && <span>({item.percent.toFixed(1)}%)</span>}
					</div>
					{width != null && (
						<div
							role="progressbar"
							aria-label={t`Traffic quota usage`}
							aria-valuenow={width}
							aria-valuemin={0}
							aria-valuemax={100}
							aria-valuetext={`${item.percent?.toFixed(1)}%`}
							className="mt-1 h-1 overflow-hidden rounded bg-muted"
						>
							<div
								className={item.percent! >= 100 ? "h-full bg-red-500" : "h-full bg-primary"}
								style={{ width: `${width}%` }}
							/>
						</div>
					)}
					{warning && <div className="mt-0.5 text-amber-600 dark:text-amber-400">{label}</div>}
				</>
			)}
		</div>
	)
}
