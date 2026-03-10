"use client"

import { useEffect, useState } from "react"
import { CheckCircle, XCircle, Loader2 } from "lucide-react"
import { apiService } from "@/lib/api"

interface HealthData {
  status: string
  version: string
  workflow_ready: boolean
  database: string
}

export function SystemHealth() {
  const [health, setHealth] = useState<HealthData | null>(null)
  const [reachable, setReachable] = useState<boolean | null>(null)

  useEffect(() => {
    apiService
      .checkHealth()
      .then((data) => {
        setHealth(data as unknown as HealthData)
        setReachable(true)
      })
      .catch(() => setReachable(false))
  }, [])

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">System Health</h2>
      <div className="space-y-3">
        <HealthRow
          label="Backend API"
          ok={reachable}
          detail={health?.version ? `v${health.version}` : undefined}
        />
        <HealthRow
          label="Database"
          ok={reachable === true ? health?.database === "connected" : reachable}
        />
        <HealthRow
          label="Analysis Engine"
          ok={reachable === true ? health?.workflow_ready ?? false : reachable}
          detail={
            health && !health.workflow_ready
              ? "LLM keys required"
              : undefined
          }
        />
      </div>
    </div>
  )
}

function HealthRow({
  label,
  ok,
  detail,
}: {
  label: string
  ok: boolean | null
  detail?: string
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <span className="text-gray-300 text-sm">{label}</span>
      <div className="flex items-center gap-2">
        {detail && <span className="text-gray-500 text-xs">{detail}</span>}
        {ok === null ? (
          <Loader2 className="h-4 w-4 text-gray-500 animate-spin" />
        ) : ok ? (
          <CheckCircle className="h-4 w-4 text-green-400" />
        ) : (
          <XCircle className="h-4 w-4 text-red-400" />
        )}
      </div>
    </div>
  )
}
