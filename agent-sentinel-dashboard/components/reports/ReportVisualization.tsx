"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, Download, Share } from "lucide-react"
import { ExecutiveSummary } from "./ExecutiveSummary"
import { PerformanceMetrics } from "./PerformanceMetrics"
import { SecurityEvents } from "./SecurityEvents"
import { ThreatAnalysis } from "./ThreatAnalysis"
import { RecommendationsPanel } from "./RecommendationsPanel"
import type { UnifiedReport } from "@/types/report"

interface ReportVisualizationProps {
  report: UnifiedReport
  onBack: () => void
}

export function ReportVisualization({ report, onBack }: ReportVisualizationProps) {
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
    link.download = `${report.agent_id}_report_${new Date().toISOString().split("T")[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleShare = () => {
    // Share functionality would go here
    console.log("Sharing report...")
  }

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
            <h1 className="text-2xl font-bold text-white">{report.agent_id} Security Report</h1>
            <p className="text-gray-400">
              {new Date(report.start_time).toLocaleDateString()} - {new Date(report.end_time).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center space-x-2">
          <Button onClick={handleExportPDF} variant="outline" className="bg-transparent">
            <Download className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
          <Button onClick={handleExportJSON} variant="outline" className="bg-transparent">
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
          <Button onClick={handleShare} className="btn-primary">
            <Share className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <ExecutiveSummary summary={report.summary} />

      {/* Performance Metrics */}
      <PerformanceMetrics metrics={report.performance_metrics} />

      {/* Security Events */}
      <SecurityEvents events={report.security_events} />

      {/* Threat Analysis */}
      <ThreatAnalysis analysis={report.threat_analysis} />

      {/* Recommendations */}
      <RecommendationsPanel recommendations={report.recommendations} nextActions={report.summary.next_actions} />
    </div>
  )
}
