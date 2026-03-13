"use client"

import { useEffect, useState, useCallback } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Users,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronRight,
  ArrowLeft,
  Loader2,
  BarChart3,
} from "lucide-react"
import { apiService, type AgentData, type SecurityEvent } from "@/lib/api"


function timeAgo(iso: string | null): string {
  if (!iso) return "Never"
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000)
  if (mins < 1) return "Just now"
  if (mins < 60) return `${mins}m ago`
  if (mins < 1440) return `${Math.floor(mins / 60)}h ago`
  return `${Math.floor(mins / 1440)}d ago`
}

function AgentDetail({
  agent,
  onBack,
}: {
  agent: AgentData
  onBack: () => void
}) {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [analyzeMsg, setAnalyzeMsg] = useState<string | null>(null)

  useEffect(() => {
    apiService
      .getSecurityEvents(50, { agent_id: agent.id })
      .then((data) => setEvents(data.events))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false))
  }, [agent.id])

  const handleAnalyze = async () => {
    if (events.length === 0) return
    setAnalyzing(true)
    setAnalyzeMsg(null)

    // Build a plain-text report from the stored events so the analysis
    // engine has something meaningful to work with
    const reportLines = [
      `Security Report — Agent: ${agent.name} (${agent.id})`,
      `Type: ${agent.type}`,
      `Total events: ${events.length}`,
      `Generated: ${new Date().toISOString()}`,
      "",
      "=== Security Events ===",
      ...events.map(
        (e, i) =>
          `[${i + 1}] ${e.severity} | ${e.threat_type} | confidence=${e.confidence} | ${e.message}`
      ),
    ]
    const reportContent = reportLines.join("\n")

    try {
      await apiService.startAnalysis(reportContent, agent.id)
      setAnalyzeMsg(
        "Analysis started. View results in a few minutes."
      )
    } catch (err) {
      setAnalyzeMsg(
        err instanceof Error ? err.message : "Failed to start analysis"
      )
      setAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onBack} className="text-gray-400 hover:text-white">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-white">{agent.name}</h2>
            <p className="text-gray-400 text-sm">
              Last seen {timeAgo(agent.last_seen)}
            </p>
          </div>
        </div>

        {events.length > 0 && (
          <Button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            {analyzing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Starting analysis...
              </>
            ) : (
              <>
                <BarChart3 className="h-4 w-4 mr-2" />
                Analyze Events
              </>
            )}
          </Button>
        )}
      </div>

      {analyzeMsg && (
        <div className={`rounded-lg px-4 py-3 text-sm ${
          analyzeMsg.startsWith("Analysis started")
            ? "bg-blue-900/20 border border-blue-500/30 text-blue-300"
            : "bg-red-900/20 border border-red-500/30 text-red-300"
        }`}>
          {analyzeMsg.startsWith("Analysis started") ? (
            <>
              {analyzeMsg}{" "}
              <Link
                href="/reports?tab=history"
                className="underline hover:text-blue-200 font-medium"
              >
                Go to Analysis History
              </Link>
            </>
          ) : (
            analyzeMsg
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agent.event_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Registered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {new Date(agent.created_at).toLocaleDateString()}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security Events
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-gray-500">Loading events...</div>
          ) : events.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-10 w-10 mx-auto mb-2 text-green-600" />
              No security events recorded for this agent.
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((e) => {
                const parsedCtx = (() => {
                  try { return e.context_json ? JSON.parse(e.context_json) : null } catch { return null }
                })()
                const hasCtx = parsedCtx && Object.keys(parsedCtx).length > 0
                return (
                <div key={e.id} className="rounded border border-gray-800 bg-black/30">
                  <div className="flex items-center justify-between py-2 px-3">
                  <div className="flex items-center gap-3">
                    {e.severity === "CRITICAL" || e.severity === "HIGH" ? (
                      <XCircle className="h-4 w-4 text-red-400 flex-shrink-0" />
                    ) : e.severity === "MEDIUM" ? (
                      <AlertTriangle className="h-4 w-4 text-yellow-400 flex-shrink-0" />
                    ) : (
                      <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                    )}
                    <div>
                      <span className="text-white text-sm">{e.threat_type.replace(/_/g, " ")}</span>
                      <p className="text-gray-500 text-xs max-w-md">
                        {e.message}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        e.severity === "CRITICAL"
                          ? "bg-red-900/30 text-red-400"
                          : e.severity === "HIGH"
                            ? "bg-orange-900/30 text-orange-400"
                            : e.severity === "MEDIUM"
                              ? "bg-yellow-900/30 text-yellow-400"
                              : "bg-green-900/30 text-green-400"
                      }`}
                    >
                      {e.severity}
                    </span>
                    <span className="text-gray-500 text-xs whitespace-nowrap">
                      {timeAgo(e.detected_at)}
                    </span>
                  </div>
                  </div>
                  {hasCtx && (
                    <details className="px-3 pb-2">
                      <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300 select-none">
                        View context
                      </summary>
                      <div className="mt-2 space-y-1">
                        {Object.entries(parsedCtx).map(([k, v]) => (
                          <div key={k} className="flex gap-2 text-xs">
                            <span className="text-gray-500 capitalize min-w-20">{k.replace(/_/g, " ")}:</span>
                            <span className="text-gray-300 break-all">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export function AgentsView() {
  const [agents, setAgents] = useState<AgentData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<AgentData | null>(null)

  const fetchAgents = useCallback(async () => {
    try {
      const data = await apiService.getAgents()
      setAgents(data.agents)
    } catch {
      setAgents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAgents()
  }, [fetchAgents])

  if (selectedAgent) {
    return <AgentDetail agent={selectedAgent} onBack={() => setSelectedAgent(null)} />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Monitored Agents</h1>
        <p className="text-gray-400">
          AI agents being monitored by Agent Sentinel for security threats
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-20 bg-gray-800 animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : agents.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Users className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <h3 className="text-white text-lg font-medium mb-1">No agents yet</h3>
            <p className="text-gray-500 text-sm">
              Agents will appear here once your SDK starts monitoring them.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card
              key={agent.id}
              className="cursor-pointer hover:border-gray-600 transition-colors"
              onClick={() => setSelectedAgent(agent)}
            >
              <CardContent className="p-6">
                <div className="mb-4">
                  <h3 className="text-white font-semibold">{agent.name}</h3>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-gray-500 text-xs">Events</p>
                    <p className="text-white font-bold text-lg">
                      {agent.event_count}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs">Last Seen</p>
                    <p className="text-white text-sm">
                      {timeAgo(agent.last_seen)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-gray-800">
                  <div className="flex items-center gap-1 text-gray-500 text-xs">
                    <Clock className="h-3 w-3" />
                    Registered {new Date(agent.created_at).toLocaleDateString()}
                  </div>
                  <ChevronRight className="h-4 w-4 text-gray-600" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
