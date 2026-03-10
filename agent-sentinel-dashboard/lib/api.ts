import type { EnhancedThreatReport } from "@/types/report"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"

export interface SecurityEvent {
  id: string
  detected_at: string
  agent_id: string
  threat_type: string
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  confidence: number
  message: string
  context_json: string | null
  detection_method: string
}

export interface AgentData {
  id: string
  name: string
  type: string
  status: string
  created_at: string
  last_seen: string | null
  event_count: number
}

export interface DashboardStats {
  total_agents: number
  active_agents: number
  total_events: number
  events_today: number
  severity_counts: Record<string, number>
  severity_today: Record<string, number>
  total_analyses: number
}

export interface EnhancedIntelligenceReport {
  agent_id: string
  start_time: string
  end_time: string
  session_logs: Array<{
    timestamp: string
    level: string
    message: string
    [key: string]: unknown
  }>
  security_events: Array<{
    id: string
    timestamp: string
    threat_type: string
    severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    message: string
    confidence: number
    details: Record<string, unknown>
  }>
  performance_metrics: {
    security_events_count: number
    session_duration_seconds: number
    [key: string]: unknown
  }
  threat_analysis: {
    total_threats: number
    threat_breakdown: Record<string, number>
    severity_distribution: Record<string, number>
    confidence_analysis: {
      average_confidence: number
      high_confidence_threats: number
    }
    risk_score: number
    most_common_threat: string
    highest_severity: string
  }
  recommendations: string[]
  summary: {
    status: "CLEAN" | "WARNING" | "CRITICAL"
    risk_score: number
    threats_detected: number
    performance_score: number
    key_insights: string[]
    next_actions: string[]
  }
  report_id: string
  analysis_type: string
  workflow_execution_time: number
  intelligence_insights: {
    enhanced_analysis: string
    threat_intelligence: string
  }
}

export function convertThreatReportToIntelligenceReport(
  report: EnhancedThreatReport
): EnhancedIntelligenceReport {
  const securityEvents = report.security_events.map((eventStr, index) => {
    const match = eventStr.match(
      /SecurityEvent\(([^,]+),\s*([^,]+),\s*([^)]+)\)/
    )
    if (match) {
      const [, threatType, severity, confidence] = match
      return {
        id: `SE-${index + 1}`,
        timestamp: new Date().toISOString(),
        threat_type: threatType.trim(),
        severity: severity.trim() as "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        message: `${severity.trim()} severity ${threatType.trim()} detected.`,
        confidence: parseFloat(confidence.trim()),
        details: {},
      }
    }
    return {
      id: `SE-${index + 1}`,
      timestamp: new Date().toISOString(),
      threat_type: "unknown",
      severity: "MEDIUM" as const,
      message: eventStr,
      confidence: 0.5,
      details: {},
    }
  })

  return {
    agent_id: report.agent_id,
    start_time: report.time_range.start,
    end_time: report.time_range.end,
    session_logs: [],
    security_events: securityEvents,
    performance_metrics: {
      security_events_count: report.threat_summary.total_threats,
      session_duration_seconds: 0,
    },
    threat_analysis: {
      total_threats: report.threat_summary.total_threats,
      threat_breakdown: report.threat_summary.threat_breakdown,
      severity_distribution: report.threat_summary.severity_breakdown,
      confidence_analysis: {
        average_confidence: 0.86,
        high_confidence_threats: 2,
      },
      risk_score: report.risk_assessment.overall_risk_score,
      most_common_threat: report.threat_summary.most_common_threat,
      highest_severity: report.threat_summary.highest_severity,
    },
    recommendations: report.recommendations,
    summary: {
      status:
        report.risk_assessment.risk_level === "LOW"
          ? "CLEAN"
          : report.risk_assessment.risk_level === "MEDIUM"
            ? "WARNING"
            : "CRITICAL",
      risk_score: report.risk_assessment.overall_risk_score,
      threats_detected: report.threat_summary.total_threats,
      performance_score: 85.0,
      key_insights: report.risk_assessment.risk_factors,
      next_actions: report.compliance_check.recommendations,
    },
    report_id: report.report_id,
    analysis_type: "comprehensive",
    workflow_execution_time: 0,
    intelligence_insights: {
      enhanced_analysis: report.executive_summary,
      threat_intelligence: `Threat Intelligence Summary:\n- Total Threats: ${report.threat_summary.total_threats}\n- Risk Level: ${report.risk_assessment.risk_level}\n- Compliance: ${report.compliance_check.overall_compliance}`,
    },
  }
}

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_BASE_URL
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem("sentinel_token")
  }

  private authHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    }
    const token = this.getToken()
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }
    return headers
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      headers: {
        ...this.authHeaders(),
        ...options?.headers,
      },
      ...options,
    })

    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("sentinel_token")
        localStorage.removeItem("sentinel_user")
        window.location.href = "/auth/login"
      }
      throw new Error("Authentication expired")
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(
        body.detail || `API request failed: ${response.status} ${response.statusText}`
      )
    }

    return response.json()
  }

  async enhanceSecurityReport(
    reportContent: string,
    agentId?: string
  ): Promise<EnhancedIntelligenceReport> {
    const response = await this.request<
      EnhancedIntelligenceReport | EnhancedThreatReport
    >("/analyze", {
      method: "POST",
      body: JSON.stringify({
        report_content: reportContent,
        analysis_type: "comprehensive",
        agent_id: agentId || "unknown",
      }),
    })

    if ("threat_summary" in response) {
      return convertThreatReportToIntelligenceReport(
        response as EnhancedThreatReport
      )
    }

    return response as EnhancedIntelligenceReport
  }

  async uploadReportFile(file: File): Promise<EnhancedIntelligenceReport> {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("analysis_type", "comprehensive")

    const token = this.getToken()
    const response = await fetch(`${this.baseUrl}/analyze/file`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    if ("threat_summary" in result) {
      return convertThreatReportToIntelligenceReport(result as EnhancedThreatReport)
    }
    return result as EnhancedIntelligenceReport
  }

  async checkHealth(): Promise<{
    status: string
    timestamp: string
    version: string
    workflow_ready: boolean
  }> {
    return this.request("/health")
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>("/api/dashboard/stats")
  }

  async getSecurityEvents(
    limit: number = 50,
    filters?: { severity?: string; agent_id?: string }
  ): Promise<{ events: SecurityEvent[]; total: number }> {
    const params = new URLSearchParams({ limit: String(limit) })
    if (filters?.severity) params.set("severity", filters.severity)
    if (filters?.agent_id) params.set("agent_id", filters.agent_id)
    return this.request(`/api/events?${params}`)
  }

  async getAgents(): Promise<{ agents: AgentData[]; total: number }> {
    return this.request("/api/agents")
  }

  async getReports(
    limit: number = 20
  ): Promise<{ reports: Array<Record<string, unknown>>; total: number }> {
    return this.request(`/api/reports?limit=${limit}`)
  }

  async getMetrics(): Promise<Record<string, unknown>> {
    return this.request("/api/metrics")
  }

  async createApiKey(): Promise<{ api_key: string; message: string }> {
    return this.request("/api/keys", { method: "POST" })
  }

  async listApiKeys(): Promise<{
    keys: Array<Record<string, unknown>>
    total: number
  }> {
    return this.request("/api/keys")
  }

  async startAnalysis(
    reportContent: string,
    agentId?: string
  ): Promise<{ run_id: string; status: string }> {
    return this.request("/api/analysis/start", {
      method: "POST",
      body: JSON.stringify({
        report_content: reportContent,
        analysis_type: "comprehensive",
        agent_id: agentId || "unknown",
      }),
    })
  }

  async getAnalysisStatus(
    runId: string
  ): Promise<{
    run_id: string
    status: string
    phase: string
    result?: EnhancedIntelligenceReport
    error?: string
  }> {
    return this.request(`/api/analysis/${runId}/status`)
  }
}

export const apiService = new ApiService()
