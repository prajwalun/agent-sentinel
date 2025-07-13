"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Target, BarChart3 } from "lucide-react"
import type { ThreatAnalysis as ThreatAnalysisType } from "@/types/report"

interface ThreatAnalysisProps {
  analysis: ThreatAnalysisType
}

export function ThreatAnalysis({ analysis }: ThreatAnalysisProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const threatTypes = Object.entries(analysis.threat_breakdown)
  const severityLevels = Object.entries(analysis.severity_distribution)

  return (
    <div className="card-dark rounded-lg p-6">
      <button onClick={() => setIsExpanded(!isExpanded)} className="flex items-center justify-between w-full text-left">
        <h2 className="text-xl font-semibold text-white">Threat Analysis</h2>
        {isExpanded ? (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-6 space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
              <div className="flex items-center space-x-2 mb-2">
                <Target className="h-5 w-5 text-red-400" />
                <span className="text-gray-400">Total Threats</span>
              </div>
              <p className="text-2xl font-bold text-white">{analysis.total_threats}</p>
            </div>

            <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
              <div className="flex items-center space-x-2 mb-2">
                <BarChart3 className="h-5 w-5 text-orange-400" />
                <span className="text-gray-400">Risk Score</span>
              </div>
              <p className="text-2xl font-bold text-white">{analysis.risk_score}</p>
            </div>

            <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
              <div className="flex items-center space-x-2 mb-2">
                <Target className="h-5 w-5 text-purple-400" />
                <span className="text-gray-400">Avg Confidence</span>
              </div>
              <p className="text-2xl font-bold text-white">
                {Math.round(analysis.confidence_analysis.average_confidence * 100)}%
              </p>
            </div>
          </div>

          {/* Threat Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Threat Types</h3>
              <div className="space-y-2">
                {threatTypes.map(([type, count]) => (
                  <div
                    key={type}
                    className="flex items-center justify-between p-3 bg-black/50 rounded border border-gray-800"
                  >
                    <span className="text-gray-300">{type.replace("_", " ")}</span>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Severity Distribution</h3>
              <div className="space-y-2">
                {severityLevels.map(([severity, count]) => (
                  <div
                    key={severity}
                    className="flex items-center justify-between p-3 bg-black/50 rounded border border-gray-800"
                  >
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          severity === "CRITICAL" || severity === "HIGH"
                            ? "bg-red-400"
                            : severity === "MEDIUM"
                              ? "bg-orange-400"
                              : "bg-green-400"
                        }`}
                      />
                      <span className="text-gray-300">{severity}</span>
                    </div>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Additional Insights */}
          <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
            <h3 className="text-lg font-semibold text-white mb-3">Key Findings</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Most Common Threat:</span>
                <span className="text-white ml-2">{analysis.most_common_threat}</span>
              </div>
              <div>
                <span className="text-gray-400">Highest Severity:</span>
                <span className="text-white ml-2">{analysis.highest_severity}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
