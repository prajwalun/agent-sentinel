"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, Download, Share } from "lucide-react"
import { ExecutiveSummary } from "./ExecutiveSummary"
import { PerformanceMetrics } from "./PerformanceMetrics"
import { SecurityEvents } from "./SecurityEvents"
import { ThreatAnalysis } from "./ThreatAnalysis"
import { RecommendationsPanel } from "./RecommendationsPanel"
import { CompliancePanel } from "./CompliancePanel"
import { RiskAssessmentPanel } from "./RiskAssessmentPanel"
import type { EnhancedIntelligenceReport } from "@/lib/api"
import { useEffect, useState } from "react"

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
    // PDF export functionality would go here
    console.log("Exporting to PDF...")
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

  const handleShare = () => {
    // Share functionality would go here
    console.log("Sharing report...")
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={onBack} variant="ghost" className="text-gray-400 hover:text-white">
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
        <div className="flex items-center space-x-2">
          <Button onClick={handleExportJSON} variant="outline" className="text-white border-gray-600">
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
          <Button onClick={handleExportPDF} variant="outline" className="text-white border-gray-600">
            <Download className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
          <Button onClick={handleShare} variant="outline" className="text-white border-gray-600">
            <Share className="h-4 w-4 mr-2" />
            Share
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

      {/* Intelligence Insights */}
      {report.intelligence_insights && (
        <div className="card-dark rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">AI Intelligence Insights</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-white mb-2">Enhanced Analysis</h3>
              <div className="text-gray-300 whitespace-pre-wrap">
                {report.intelligence_insights.enhanced_analysis}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-2">Threat Intelligence</h3>
              <div className="text-gray-300 whitespace-pre-wrap">
                {report.intelligence_insights.threat_intelligence}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
