"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, Download, Printer } from "lucide-react"
import { ExecutiveSummary } from "./ExecutiveSummary"
import { PerformanceMetrics } from "./PerformanceMetrics"
import { SecurityEvents } from "./SecurityEvents"
import { ThreatAnalysis } from "./ThreatAnalysis"
import { RecommendationsPanel } from "./RecommendationsPanel"
import { CompliancePanel } from "./CompliancePanel"
import { RiskAssessmentPanel } from "./RiskAssessmentPanel"
import type { EnhancedIntelligenceReport } from "@/lib/api"
import { useEffect, useState } from "react"

/** Returns true if the string is valid JSON (i.e. not LLM prose). */
function looksLikeJson(text: string): boolean {
  const s = text.trim()
  if (!s.startsWith("{") && !s.startsWith("[")) return false
  try { JSON.parse(s); return true } catch { return false }
}

/**
 * Renders LLM-generated markdown prose with basic formatting.
 * Handles ## headings, - bullet points, and **bold** text.
 * Shows a graceful fallback when content is empty or stored as raw JSON.
 */
function InsightSection({ title, content }: { title: string; content: string }) {
  const isEmpty = !content || looksLikeJson(content)

  if (isEmpty) {
    return (
      <div>
        <h3 className="text-base font-semibold text-white mb-3 border-b border-gray-800 pb-2">
          {title}
        </h3>
        <p className="text-sm text-gray-500 italic">
          No narrative insights were generated for this run. Re-run the analysis to produce AI-generated insights.
        </p>
      </div>
    )
  }

  // LLM outputs sometimes use literal \n instead of real newlines when
  // serialised through JSON — normalise both forms.
  const lines = content.replace(/\\n/g, "\n").split("\n")

  return (
    <div>
      <h3 className="text-base font-semibold text-white mb-3 border-b border-gray-800 pb-2">
        {title}
      </h3>
      <div className="space-y-1.5 text-sm">
        {lines.map((line, i) => {
          const trimmed = line.trim()
          if (!trimmed) return <div key={i} className="h-1" />

          // ## or ### heading
          if (/^#{1,3}\s/.test(trimmed)) {
            const text = trimmed.replace(/^#{1,3}\s+/, "")
            return (
              <p key={i} className="text-white font-semibold mt-4 first:mt-0">
                {text}
              </p>
            )
          }

          // - or * bullet
          if (/^[-*•]\s/.test(trimmed)) {
            const text = trimmed.replace(/^[-*•]\s+/, "").replace(/\*\*(.*?)\*\*/g, "$1")
            return (
              <div key={i} className="flex items-start gap-2 ml-2">
                <span className="text-red-500 mt-1 flex-shrink-0 text-xs">▸</span>
                <span className="text-gray-300 leading-relaxed">{text}</span>
              </div>
            )
          }

          // Numbered list: 1. item
          if (/^\d+\.\s/.test(trimmed)) {
            const text = trimmed.replace(/^\d+\.\s+/, "").replace(/\*\*(.*?)\*\*/g, "$1")
            return (
              <div key={i} className="flex items-start gap-2 ml-2">
                <span className="text-gray-500 mt-0.5 flex-shrink-0 text-xs">
                  {trimmed.match(/^(\d+)/)?.[1]}.
                </span>
                <span className="text-gray-300 leading-relaxed">{text}</span>
              </div>
            )
          }

          const formatted = trimmed.replace(/\*\*(.*?)\*\*/g, "$1")
          return (
            <p key={i} className="text-gray-300 leading-relaxed">
              {formatted}
            </p>
          )
        })}
      </div>
    </div>
  )
}

interface ReportVisualizationProps {
  report: EnhancedIntelligenceReport
  onBack: () => void
}

export function ReportVisualization({ report, onBack }: ReportVisualizationProps) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    setMounted(true)
  }, [])

  const handleExportPDF = () => {
    window.print()
  }

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(report, null, 2)
    const dataBlob = new Blob([dataStr], { type: "application/json" })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement("a")
    link.href = url
    link.download = `${report.agent_id}_enhanced_report_${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const formatDate = (dateString: string) => {
    if (!mounted) return "Loading..."
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Check if this is an enhanced threat report with additional data
  const hasEnhancedData = report.intelligence_insights?.enhanced_analysis?.includes('risk_assessment') ||
                         report.intelligence_insights?.enhanced_analysis?.includes('compliance_check')

  return (
    <div className="space-y-6">
      {/* Print stylesheet — inverts the dark theme for PDF export */}
      <style>{`
        @media print {
          body { background: white !important; color: black !important; }
          .card-dark { background: white !important; border: 1px solid #ddd !important; }
          [class*="bg-gray"] { background: white !important; }
          [class*="text-gray"] { color: #333 !important; }
          [class*="text-white"] { color: black !important; }
          [class*="border-gray"] { border-color: #ccc !important; }
          .print-hide { display: none !important; }
        }
      `}</style>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={onBack} variant="ghost" className="text-gray-400 hover:text-white print-hide">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Reports
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-white">{report.agent_id} AI-Enhanced Security Report</h1>
            <p className="text-gray-400">
              {formatDate(report.start_time)} - {formatDate(report.end_time)}
            </p>
            <p className="text-sm text-blue-400">
              Report ID: {report.report_id} • Analysis Time: {report.workflow_execution_time.toFixed(2)}s
            </p>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center space-x-2 print-hide">
          <Button onClick={handleExportJSON} variant="outline" className="text-white border-gray-600">
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
          <Button onClick={handleExportPDF} variant="outline" className="text-white border-gray-600">
            <Printer className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Report Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <ExecutiveSummary summary={report.summary} />
          <SecurityEvents events={report.security_events} />
          <ThreatAnalysis analysis={report.threat_analysis} />
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          <PerformanceMetrics metrics={report.performance_metrics} />
          <RecommendationsPanel 
            recommendations={report.recommendations} 
            nextActions={report.summary.next_actions} 
          />
        </div>
      </div>

      {/* Enhanced Data Panels - Only show if we have enhanced threat report data */}
      {hasEnhancedData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Assessment Panel */}
          <RiskAssessmentPanel 
            riskAssessment={{
              overall_risk_score: report.summary.risk_score,
              risk_level: report.summary.status === 'CLEAN' ? 'LOW' : 
                         report.summary.status === 'WARNING' ? 'MEDIUM' : 'HIGH',
              risk_factors: report.summary.key_insights,
              trend_analysis: 'STABLE',
              risk_distribution: { low: 1, medium: 1, high: 1 }
            }}
          />
          
          {/* Compliance Panel */}
          <CompliancePanel 
            complianceCheck={{
              overall_compliance: report.summary.status === 'CLEAN' ? 'COMPLIANT' : 'NON_COMPLIANT',
              standards: {
                'data_protection': report.summary.status === 'CLEAN' ? 'COMPLIANT' : 'NON_COMPLIANT',
                'access_control': report.summary.status === 'CLEAN' ? 'COMPLIANT' : 'NON_COMPLIANT',
                'audit_logging': 'COMPLIANT',
                'incident_response': 'COMPLIANT'
              },
              violations: report.summary.status !== 'CLEAN' ? ['Security violations detected'] : [],
              recommendations: report.summary.next_actions
            }}
          />
        </div>
      )}

      {/* Intelligence Insights — always show when the field exists so the user
          knows AI analysis ran. InsightSection handles the empty/JSON fallback. */}
      {report.intelligence_insights && (
        <div className="card-dark rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-5">
            AI Intelligence Insights
          </h2>
          <div className="space-y-6">
            <InsightSection
              title="Enhanced Analysis"
              content={report.intelligence_insights.enhanced_analysis ?? ""}
            />
            <InsightSection
              title="Threat Intelligence"
              content={report.intelligence_insights.threat_intelligence ?? ""}
            />
          </div>
        </div>
      )}
    </div>
  )
}
