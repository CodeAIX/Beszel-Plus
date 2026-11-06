import { t } from "@lingui/core/macro"
import { Trans } from "@lingui/react/macro"
import { ClientResponseError } from "pocketbase"
import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { pb } from "@/lib/api"

type ImportRow = { name: string; host: string; port: number; action: string; reason?: string }
type ImportPlan = {
	rows: ImportRow[]
	add: number
	skip: number
	errors: number
	created: number
	preview_id: string
}

function rowDescription(row: ImportRow) {
	switch (row.reason) {
		case "existing_endpoint":
			return t`Already listed; keep existing settings and token`
		case "token_conflict":
			return t`Token is already assigned to another address`
		case "unknown_user":
			return t`User email not found; disable original user mapping or create the user first`
		case "invalid_system":
			return t`Invalid name or host`
		case "invalid_token":
			return t`Invalid token (9–255 characters required)`
		case "generated_token":
			return t`Add; a new token will be generated and must be configured on the agent`
		default:
			return t`Add with existing token`
	}
}

export default function ImportSystems() {
	const fileInput = useRef<HTMLInputElement>(null)
	const [content, setContent] = useState("")
	const [matchUsers, setMatchUsers] = useState(false)
	const [plan, setPlan] = useState<ImportPlan | null>(null)
	const [busy, setBusy] = useState(false)
	const [done, setDone] = useState(false)
	const [error, setError] = useState("")

	function resetPreview() {
		setPlan(null)
		setDone(false)
		setError("")
	}

	async function submit(apply: boolean) {
		setBusy(true)
		setError("")
		try {
			const result = await pb.send<ImportPlan>("/api/beszel/config-yaml/import", {
				method: "POST",
				body: {
					config: content,
					user_mode: matchUsers ? "match" : "current",
					apply,
					preview_id: plan?.preview_id ?? "",
				},
			})
			setPlan(result)
			setDone(apply)
			if (apply) {
				setContent("")
				if (fileInput.current) fileInput.current.value = ""
			}
		} catch (error) {
			const err = error instanceof ClientResponseError ? error : new ClientResponseError(error)
			if (err.response?.code === "managed_config") {
				setError(
					t`This Hub uses config.yml startup sync. Remove or migrate that file before importing; otherwise the next restart could delete imported systems.`
				)
			} else if (err.response?.code === "preview_changed") {
				setPlan(err.response.plan)
				setError(t`The import preview changed. Review the new preview before confirming again.`)
			} else if (err.status === 400 || err.status === 413) {
				setError(
					t`Invalid YAML. Use an original Beszel export with 1–1000 systems, at most 1 MiB. Check names, hosts, ports, tokens and users.`
				)
			} else {
				setError(
					t`Import failed. No systems were imported. Check your connection and administrator access, then preview again.`
				)
			}
		} finally {
			setBusy(false)
		}
	}

	return (
		<section className="space-y-4" aria-labelledby="import-systems-title">
			<div>
				<h3 id="import-systems-title" className="text-xl font-medium mb-2">
					<Trans>Import existing systems</Trans>
				</h3>
				<p className="text-sm text-muted-foreground leading-relaxed">
					<Trans>
						Import an original Beszel YAML export. New systems are added in one batch; existing addresses are skipped
						and keep their settings, tokens and history.
					</Trans>
				</p>
			</div>
			<p className="text-sm text-muted-foreground leading-relaxed">
				<Trans>
					Importing adds connection settings, not monitoring history or the Hub key. Existing agents must trust this
					Hub's public key; WebSocket agents must also use this Hub's URL. Reinstalling the agent is unnecessary.
				</Trans>
			</p>
			<div className="space-y-2">
				<Label htmlFor="import-systems-file">
					<Trans>Choose a YAML export (up to 1 MiB)</Trans>
				</Label>
				<Input
					ref={fileInput}
					id="import-systems-file"
					type="file"
					accept=".yml,.yaml,.md,.txt,text/yaml,text/plain"
					disabled={busy}
					onChange={async (e) => {
						const file = e.target.files?.[0]
						resetPreview()
						setContent("")
						if (!file) return
						if (file.size > 1024 * 1024) {
							setError(t`The file exceeds 1 MiB.`)
							return
						}
						try {
							setBusy(true)
							setContent(await file.text())
						} catch {
							setError(t`Unable to read the selected file.`)
						} finally {
							setBusy(false)
						}
					}}
				/>
				<details>
					<summary className="text-sm cursor-pointer py-1">
						<Trans>Or paste YAML</Trans>
					</summary>
					<Label className="sr-only" htmlFor="import-systems-yaml">
						YAML
					</Label>
					<Textarea
						id="import-systems-yaml"
						dir="ltr"
						rows={8}
						spellCheck={false}
						autoComplete="off"
						className="font-mono mt-2"
						value={content}
						disabled={busy}
						onChange={(e) => {
							setContent(e.target.value)
							resetPreview()
						}}
					/>
				</details>
			</div>
			<div className="flex items-start gap-2">
				<Checkbox
					id="import-match-users"
					checked={matchUsers}
					disabled={busy}
					onCheckedChange={(checked) => {
						setMatchUsers(checked === true)
						resetPreview()
					}}
				/>
				<div className="space-y-1">
					<Label htmlFor="import-match-users">
						<Trans>Preserve original user assignments by email</Trans>
					</Label>
					<p className="text-sm text-muted-foreground">
						<Trans>
							By default, new systems belong to the current administrator. Email matching requires every listed user to
							exist in this Hub.
						</Trans>
					</p>
				</div>
			</div>
			{error && (
				<p role="alert" className="text-sm text-destructive">
					{error}
				</p>
			)}
			{plan && (
				<div className="space-y-3" aria-live="polite">
					<p className="text-sm font-medium">
						{done ? (
							<Trans>
								Imported: {plan.created}. Skipped: {plan.skip}.
							</Trans>
						) : (
							<Trans>
								New: {plan.add}. Skipped: {plan.skip}. Errors: {plan.errors}.
							</Trans>
						)}
					</p>
					<div className="max-h-72 overflow-auto rounded-md border">
						<table className="w-full text-sm text-start">
							<thead className="bg-muted">
								<tr>
									<th className="p-3 text-start">
										<Trans>Name</Trans>
									</th>
									<th className="p-3 text-start">
										<Trans>Host / IP</Trans>
									</th>
									<th className="p-3 text-start">
										<Trans>Status</Trans>
									</th>
								</tr>
							</thead>
							<tbody>
								{plan.rows.map((row, i) => (
									<tr key={i} className="border-t">
										<td className="p-3 break-all">{row.name}</td>
										<td className="p-3 break-all">{row.host.startsWith("/") ? row.host : `${row.host}:${row.port}`}</td>
										<td className={`p-3 ${row.action === "error" ? "text-destructive" : "text-muted-foreground"}`}>
											{done && row.action === "add" ? <Trans>Imported</Trans> : rowDescription(row)}
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}
			<div className="flex flex-wrap gap-3">
				<Button variant="outline" disabled={busy || !content.trim()} onClick={() => submit(false)}>
					<Trans>Preview import</Trans>
				</Button>
				{plan && !done && (
					<Button disabled={busy || plan.errors > 0 || plan.add === 0} onClick={() => submit(true)}>
						<Trans>Confirm import</Trans>
					</Button>
				)}
			</div>
		</section>
	)
}
