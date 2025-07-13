"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Upload, FileText, AlertCircle } from "lucide-react"
import type { UnifiedReport } from "@/types/report"

interface ReportUploadProps {
  onReportSelect: (report: UnifiedReport) => void
}

export function ReportUpload({ onReportSelect }: ReportUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Sample report data for demo
  const sampleReport: UnifiedReport = {
    agent_id: "MathAgent",
    start_time: "2025-07-13T02:12:39.200Z",
    end_time: "2025-07-13T02:22:39.500Z",
    session_logs: [
      {
        timestamp: "2025-07-13 02:12:39,200",
        level: "INFO",
        agent_id: "MathAgent",
        message: "AgentSentinel initialized for agent: MathAgent",
      },
      {
        timestamp: "2025-07-13 02:13:30,200",
        level: "ERROR",
        agent_id: "MathAgent",
        message: "Security event: Potential SQL injection attempt detected",
      },
    ],
    security_events: [
      {
        id: "evt_004",
        timestamp: "2025-07-13T02:13:30.200Z",
        threat_type: "SQL_INJECTION",
        severity: "HIGH",
        message: "Security event: Potential SQL injection attempt detected",
        confidence: 0.96,
        details: {
          input: "'; DROP TABLE users; --",
          action_taken: "blocked",
          pattern_matched: "sql_injection_pattern_1",
        },
      },
    ],
    performance_metrics: {
      total_function_calls: 156,
      average_response_time_ms: 245,
      memory_usage_mb: 512,
      cpu_usage_percent: 45.2,
      success_rate: 99.8,
      error_rate: 0.2,
      security_events_count: 4,
      session_duration_seconds: 600,
      throughput_requests_per_minute: 15.6,
    },
    threat_analysis: {
      total_threats: 4,
      threat_breakdown: {
        FUNCTION_CALL: 2,
        PERFORMANCE_WARNING: 1,
        SQL_INJECTION: 1,
      },
      severity_distribution: {
        LOW: 2,
        MEDIUM: 1,
        HIGH: 1,
        CRITICAL: 0,
      },
      confidence_analysis: {
        average_confidence: 0.93,
        high_confidence_threats: 3,
        confidence_distribution: {
          low: 0,
          medium: 1,
          high: 3,
        },
      },
      risk_score: 28.5,
      most_common_threat: "FUNCTION_CALL",
      highest_severity: "HIGH",
    },
    recommendations: [
      "Investigate the SQL injection attempt and review input validation",
      "Optimize memory usage to stay below 500MB threshold",
      "Continue monitoring for unusual input patterns",
      "Consider implementing additional security measures for database operations",
      "Review agent configuration for performance optimization",
    ],
    summary: {
      status: "WARNING",
      risk_score: 28.5,
      threats_detected: 4,
      performance_score: 87.2,
      key_insights: [
        "1 SQL injection attempt was blocked successfully",
        "Memory usage exceeded recommended threshold",
        "Overall performance is good with 99.8% success rate",
        "Agent is functioning normally with expected security monitoring",
      ],
      next_actions: [
        "Review security logs for the SQL injection attempt",
        "Optimize memory usage in agent code",
        "Schedule regular security review",
      ],
    },
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    setLoading(true)
    setError(null)

    try {
      if (!file.name.endsWith(".json")) {
        throw new Error("Please upload a JSON file")
      }

      const text = await file.text()
      const report = JSON.parse(text) as UnifiedReport

      // Basic validation
      if (!report.agent_id || !report.summary || !report.performance_metrics) {
        throw new Error("Invalid report format")
      }

      onReportSelect(report)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse report")
    } finally {
      setLoading(false)
    }
  }

  const handleSampleReport = () => {
    onReportSelect(sampleReport)
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        className={`card-dark rounded-lg p-8 border-2 border-dashed transition-colors ${
          dragActive ? "border-red-600 bg-red-900/10" : "border-gray-600"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="text-center space-y-4">
          <Upload className="h-12 w-12 text-gray-400 mx-auto" />
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">Upload Report File</h3>
            <p className="text-gray-400">Drag and drop your unified report JSON file here, or click to browse</p>
          </div>

          <Button onClick={() => fileInputRef.current?.click()} className="btn-primary" disabled={loading}>
            {loading ? "Processing..." : "Choose File"}
          </Button>

          <input ref={fileInputRef} type="file" accept=".json" onChange={handleFileInput} className="hidden" />
        </div>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded flex items-center space-x-2">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Sample Report */}
      <div className="card-dark rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="h-8 w-8 text-red-600" />
            <div>
              <h3 className="text-lg font-semibold text-white">Sample Report</h3>
              <p className="text-gray-400">MathAgent Security Analysis - Demo Data</p>
            </div>
          </div>
          <Button onClick={handleSampleReport} className="btn-primary">
            View Sample
          </Button>
        </div>
      </div>
    </div>
  )
}
