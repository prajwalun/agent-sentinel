"use client"

import { useState } from "react"
import { ReportUpload } from "./ReportUpload"
import { ReportVisualization } from "./ReportVisualization"
import type { UnifiedReport } from "@/types/report"

export function ReportsView() {
  const [selectedReport, setSelectedReport] = useState<UnifiedReport | null>(null)

  const handleReportSelect = (report: UnifiedReport) => {
    setSelectedReport(report)
  }

  const handleBackToUpload = () => {
    setSelectedReport(null)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Security Reports</h1>
        <p className="text-gray-400">Upload and analyze unified agent security reports</p>
      </div>

      {!selectedReport ? (
        <ReportUpload onReportSelect={handleReportSelect} />
      ) : (
        <ReportVisualization report={selectedReport} onBack={handleBackToUpload} />
      )}
    </div>
  )
}
