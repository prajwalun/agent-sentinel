"use client"

import { useState } from "react"
import { ReportUpload } from "./ReportUpload"
import { ReportVisualization } from "./ReportVisualization"
import type { EnhancedIntelligenceReport } from "@/lib/api"

export function ReportsView() {
  const [selectedReport, setSelectedReport] = useState<EnhancedIntelligenceReport | null>(null)

  const handleReportSelect = (report: EnhancedIntelligenceReport) => {
    setSelectedReport(report)
  }

  const handleBackToUpload = () => {
    setSelectedReport(null)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">AI-Enhanced Security Reports</h1>
        <p className="text-gray-400">
          Upload and analyze security reports with AI-powered intelligence and threat analysis
        </p>
      </div>

      {!selectedReport ? (
        <ReportUpload onReportSelect={handleReportSelect} />
      ) : (
        <ReportVisualization report={selectedReport} onBack={handleBackToUpload} />
      )}
    </div>
  )
}
