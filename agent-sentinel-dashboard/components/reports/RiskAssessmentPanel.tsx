"use client"

import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield } from "lucide-react"

interface RiskAssessment {
  overall_risk_score: number
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  risk_factors: string[]
  trend_analysis: "STABLE" | "INCREASING" | "DECREASING"
  risk_distribution: Record<string, number>
}

interface RiskAssessmentPanelProps {
  riskAssessment: RiskAssessment
}

export function RiskAssessmentPanel({ riskAssessment }: RiskAssessmentPanelProps) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case "LOW":
        return "text-green-400"
      case "MEDIUM":
        return "text-yellow-400"
      case "HIGH":
        return "text-orange-400"
      case "CRITICAL":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case "LOW":
        return "bg-green-900/20 border-green-500/30"
      case "MEDIUM":
        return "bg-yellow-900/20 border-yellow-500/30"
      case "HIGH":
        return "bg-orange-900/20 border-orange-500/30"
      case "CRITICAL":
        return "bg-red-900/20 border-red-500/30"
      default:
        return "bg-gray-900/20 border-gray-500/30"
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "INCREASING":
        return <TrendingUp className="h-5 w-5 text-red-400" />
      case "DECREASING":
        return <TrendingDown className="h-5 w-5 text-green-400" />
      case "STABLE":
        return <Minus className="h-5 w-5 text-blue-400" />
      default:
        return <Minus className="h-5 w-5 text-gray-400" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "INCREASING":
        return "text-red-400"
      case "DECREASING":
        return "text-green-400"
      case "STABLE":
        return "text-blue-400"
      default:
        return "text-gray-400"
    }
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Shield className="h-6 w-6 text-orange-400" />
        <h2 className="text-xl font-semibold text-white">Risk Assessment</h2>
      </div>

      {/* Overall Risk Score */}
      <div className={`rounded-lg p-4 border mb-6 ${getRiskBgColor(riskAssessment.risk_level)}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-white">Overall Risk Score</h3>
            <p className="text-gray-400 text-sm">Current threat level assessment</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">
              {riskAssessment.overall_risk_score.toFixed(2)}
            </div>
            <div className={`text-sm font-medium ${getRiskColor(riskAssessment.risk_level)}`}>
              {riskAssessment.risk_level}
            </div>
          </div>
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="mb-6">
        <div className="flex items-center justify-between bg-black/50 rounded-lg p-4 border border-gray-800">
          <div className="flex items-center space-x-3">
            {getTrendIcon(riskAssessment.trend_analysis)}
            <span className="text-white font-medium">Risk Trend</span>
          </div>
          <span className={`font-bold ${getTrendColor(riskAssessment.trend_analysis)}`}>
            {riskAssessment.trend_analysis}
          </span>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-white mb-3">Risk Distribution</h3>
        <div className="space-y-2">
          {Object.entries(riskAssessment.risk_distribution).map(([level, count]) => (
            <div key={level} className="flex items-center justify-between bg-black/30 rounded-lg p-3 border border-gray-800">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  level === 'high' ? 'bg-red-400' : 
                  level === 'medium' ? 'bg-yellow-400' : 
                  'bg-green-400'
                }`}></div>
                <span className="text-gray-300 capitalize">{level} Risk</span>
              </div>
              <span className="text-white font-medium">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Factors */}
      {riskAssessment.risk_factors.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-white mb-3">Key Risk Factors</h3>
          <div className="space-y-2">
            {riskAssessment.risk_factors.map((factor, index) => (
              <div key={index} className="flex items-start space-x-3 bg-orange-900/20 rounded-lg p-3 border border-orange-500/30">
                <AlertTriangle className="h-5 w-5 text-orange-400 mt-0.5 flex-shrink-0" />
                <span className="text-orange-300 text-sm">{factor}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 