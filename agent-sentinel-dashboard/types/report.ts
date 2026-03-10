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
  security_events_count: number
  session_duration_seconds: number
  total_function_calls?: number
  average_response_time_ms?: number
  memory_usage_mb?: number
  cpu_usage_percent?: number
  success_rate?: number
  error_rate?: number
  throughput_requests_per_minute?: number
}

export interface ThreatAnalysis {
  total_threats: number
  threat_breakdown: Record<string, number>
  severity_distribution: Record<string, number>
  confidence_analysis: {
    average_confidence: number
    high_confidence_threats: number
    confidence_distribution?: Record<string, number>
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

// New types for the updated report format
export interface ThreatSummary {
  total_threats: number
  threat_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  threat_breakdown: Record<string, number>
  severity_breakdown: Record<string, number>
  most_common_threat: string
  highest_severity: string
  time_distribution: Record<string, number>
}

export interface RiskAssessment {
  overall_risk_score: number
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  risk_factors: string[]
  trend_analysis: "STABLE" | "INCREASING" | "DECREASING"
  risk_distribution: Record<string, number>
}

export interface ThreatPattern {
  count: number
  severities: string[]
  confidences: number[]
  timestamps: string[]
}

export interface DetailedThreatAnalysis {
  threat_patterns: Record<string, ThreatPattern>
  attack_vectors: Record<string, number>
  vulnerability_analysis: Record<string, number>
  threat_intelligence: {
    known_threats: number
    novel_threats: number
    threat_sources: string[]
  }
}

export interface ComplianceCheck {
  overall_compliance: "COMPLIANT" | "NON_COMPLIANT" | "PARTIAL"
  standards: Record<string, "COMPLIANT" | "NON_COMPLIANT">
  violations: string[]
  recommendations: string[]
}

export interface TimeRange {
  start: string
  end: string
}

// Updated unified report interface
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

// New enhanced report format
export interface EnhancedThreatReport {
  agent_id: string
  report_id: string
  generated_at: string
  time_range: TimeRange
  threat_summary: ThreatSummary
  security_events: string[] // Array of SecurityEvent strings
  risk_assessment: RiskAssessment
  threat_analysis: DetailedThreatAnalysis
  recommendations: string[]
  compliance_check: ComplianceCheck
  executive_summary: string
}
