import { describe, expect, mock, test } from "bun:test"
import { renderToStaticMarkup } from "react-dom/server"
import {
	trafficBytes,
	trafficProgress,
	trafficQuota,
	trafficQuotaInput,
	trafficRange,
} from "../src/lib/traffic-display"
import type { TrafficView } from "../src/types"

mock.module("@lingui/core/macro", () => ({ t: (strings: TemplateStringsArray) => strings.join("") }))
const { TrafficUsageCell } = await import("../src/components/traffic/traffic-usage-cell")

describe("traffic date and byte display", () => {
	test("keeps UTC date boundaries across local offsets and leap days", () => {
		expect(trafficRange(1, new Date("2026-11-06T00:30:00+08:00"))).toEqual({ from: "2026-11-05", to: "2026-11-06" })
		expect(trafficRange(2, new Date("2028-03-01T12:00:00Z"))).toEqual({ from: "2028-02-29", to: "2028-03-02" })
	})
	test("distinguishes SI, binary, missing, zero and unsafe values", () => {
		expect(trafficBytes(1e12)).toBe("1 TB")
		expect(trafficBytes(1024 ** 3, "GiB")).toBe("1 GiB")
		expect(trafficBytes(null)).toBe("—")
		expect(trafficBytes(0)).toBe("0 B")
		expect(trafficBytes(Number.MAX_SAFE_INTEGER + 1)).toBe("—")
	})
	test("round trips quotas exactly through GB and TB without float rounding", () => {
		for (const bytes of [0, 1, 1e12, 1073741824, Number.MAX_SAFE_INTEGER]) {
			for (const factor of [1e9, 1e12]) expect(trafficQuota(trafficQuotaInput(bytes, factor), factor)).toBe(bytes)
		}
		expect(trafficQuota("0.000000001", 1e9)).toBe(1)
		for (const invalid of ["-1", "NaN", "Infinity", "1e3", "0.0000000001", "9007199.254740992"])
			expect(() => trafficQuota(invalid, 1e9)).toThrow()
	})
})

test("over-quota display retains 120% but clamps the actual progress bar", () => {
	const item = {
		used_bytes: 1200,
		quota_bytes: 1000,
		percent: 120,
		status: "ok",
		freshness: "fresh",
		coverage: "unknown",
		quality: "normal",
		system_status: "up",
		count_mode: "tx",
		settings: { display_unit: "GB" },
	} as TrafficView
	const html = renderToStaticMarkup(<TrafficUsageCell item={item} />)
	expect(html).toContain("120.0%")
	expect(html).toContain('aria-valuenow="100"')
	expect(html).toContain("width:100%")
	expect(html).not.toContain("width:120%")
	expect(trafficProgress(null)).toBeNull()
	expect(trafficProgress(0)).toBe(0)
	const missing = renderToStaticMarkup(<TrafficUsageCell item={{ ...item, used_bytes: null, status: "not_enabled" }} />)
	expect(missing).toContain("Traffic not enabled")
	expect(missing).not.toContain("progressbar")
})
