"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import {
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  AlertTriangle,
} from "lucide-react"
import { apiService, type EnhancedIntelligenceReport } from "@/lib/api"

interface AnalysisRun {
  id: string
  agent_id: string
  status: string
  risk_level: string | null
  created_at: string
  completed_at: string | null
  duration_ms: number | null
  result_json: string | null
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "completed":
      return <CheckCircle className="h-5 w-5 text-green-400" />
    case "failed":
      return <XCircle className="h-5 w-5 text-red-400" />
    case "running":
    case "pending":
      return <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
    default:
      return <Clock className="h-5 w-5 text-gray-400" />
  }
}

function RiskBadge({ level }: { level: string | null }) {
  if (!level) return null
  const colors: Record<string, string> = {
    CLEAN: "bg-green-900/30 text-green-400",
    WARNING: "bg-orange-900/30 text-orange-400",
    CRITICAL: "bg-red-900/30 text-red-400",
  }
  return (
    <span
      className={`text-xs px-2 py-0.5 rounded ${colors[level] || "bg-gray-800 text-gray-400"}`}
    >
      {level}
    </span>
  )
}

interface AnalysisHistoryProps {
  onSelectReport: (report: EnhancedIntelligenceReport) => void
}

export function AnalysisHistory({ onSelectReport }: AnalysisHistoryProps) {
  const [runs, setRuns] = useState<AnalysisRun[]>([])
  const [loading, setLoading] = useState(true)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchRuns = useCallback(async () => {
    try {
      const data = await apiService.getReports(50)
      setRuns(data.reports as unknown as AnalysisRun[])
      return data.reports as unknown as AnalysisRun[]
    } catch {
      setRuns([])
      return []
    } finally {
      setLoading(false)
    }
  }, [])

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  useEffect(() => {
    fetchRuns().then((initial) => {
      const hasActive = initial.some(
        (r) => r.status === "running" || r.status === "pending"
      )
      if (hasActive) {
        pollingRef.current = setInterval(async () => {
          const updated = await fetchRuns()
          const stillActive = updated.some(
            (r) => r.status === "running" || r.status === "pending"
          )
          if (!stillActive) stopPolling()
        }, 3000)
      }
    })
    return () => stopPolling()
  }, [fetchRuns, stopPolling])

  const handleClick = (run: AnalysisRun) => {
    if (run.status !== "completed" || !run.result_json) return
    try {
      const result = JSON.parse(run.result_json)
      onSelectReport(result as EnhancedIntelligenceReport)
    } catch {
      // Invalid JSON — ignore
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-500">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading analysis history...
      </div>
    )
  }

  if (runs.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <FileText className="h-12 w-12 text-gray-600 mx-auto mb-3" />
          <h3 className="text-white text-lg font-medium mb-1">
            No analyses yet
          </h3>
          <p className="text-gray-500 text-sm">
            Upload a security report to run your first AI-powered analysis.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {runs.map((run) => (
        <div
          key={run.id}
          onClick={() => handleClick(run)}
          className={`flex items-center justify-between p-4 rounded-lg border border-gray-800 bg-gray-900/50 ${
            run.status === "completed"
              ? "cursor-pointer hover:border-gray-600 transition-colors"
              : ""
          }`}
        >
          <div className="flex items-center gap-4">
            <StatusIcon status={run.status} />
            <div>
              <p className="text-white text-sm font-medium">
                {run.agent_id}
              </p>
              <p className="text-gray-500 text-xs">
                {new Date(run.created_at).toLocaleString()}
                {run.duration_ms
                  ? ` · ${(run.duration_ms / 1000).toFixed(1)}s`
                  : ""}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <RiskBadge level={run.risk_level} />
            <span
              className={`text-xs capitalize ${
                run.status === "completed"
                  ? "text-green-400"
                  : run.status === "failed"
                    ? "text-red-400"
                    : "text-blue-400"
              }`}
            >
              {run.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
