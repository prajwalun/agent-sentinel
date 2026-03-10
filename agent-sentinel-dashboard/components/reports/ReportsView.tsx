"use client"

import { useState } from "react"
import { ReportUpload } from "./ReportUpload"
import { AnalysisHistory } from "./AnalysisHistory"
import { ReportVisualization } from "./ReportVisualization"
import type { EnhancedIntelligenceReport } from "@/lib/api"

type Tab = "upload" | "history"

export function ReportsView() {
  const [activeTab, setActiveTab] = useState<Tab>("upload")
  const [selectedReport, setSelectedReport] =
    useState<EnhancedIntelligenceReport | null>(null)

  if (selectedReport) {
    return (
      <ReportVisualization
        report={selectedReport}
        onBack={() => setSelectedReport(null)}
      />
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Security Reports
        </h1>
        <p className="text-gray-400">
          Upload reports for AI-powered analysis or review past results
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        <button
          onClick={() => setActiveTab("upload")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "upload"
              ? "bg-red-600 text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          Upload &amp; Analyze
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === "history"
              ? "bg-red-600 text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          Analysis History
        </button>
      </div>

      {activeTab === "upload" ? (
        <ReportUpload onReportSelect={setSelectedReport} />
      ) : (
        <AnalysisHistory onSelectReport={setSelectedReport} />
      )}
    </div>
  )
}
