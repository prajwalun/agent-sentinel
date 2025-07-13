export interface SessionLog {
  timestamp: string
  level: string
  agent_id: string
  message: string
}

export interface SecurityEvent {
  id: string
  timestamp: string
  threat_type: string
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  message: string
  confidence: number
  details: Record<string, any>
}

export interface PerformanceMetrics {
  total_function_calls: number
  average_response_time_ms: number
  memory_usage_mb: number
  cpu_usage_percent: number
  success_rate: number
  error_rate: number
  security_events_count: number
  session_duration_seconds: number
  throughput_requests_per_minute: number
}

export interface ThreatAnalysis {
  total_threats: number
  threat_breakdown: Record<string, number>
  severity_distribution: Record<string, number>
  confidence_analysis: {
    average_confidence: number
    high_confidence_threats: number
    confidence_distribution: Record<string, number>
  }
  risk_score: number
  most_common_threat: string
  highest_severity: string
}

export interface ReportSummary {
  status: "CLEAN" | "WARNING" | "CRITICAL"
  risk_score: number
  threats_detected: number
  performance_score: number
  key_insights: string[]
  next_actions: string[]
}

export interface UnifiedReport {
  agent_id: string
  start_time: string
  end_time: string
  session_logs: SessionLog[]
  security_events: SecurityEvent[]
  performance_metrics: PerformanceMetrics
  threat_analysis: ThreatAnalysis
  recommendations: string[]
  summary: ReportSummary
}
