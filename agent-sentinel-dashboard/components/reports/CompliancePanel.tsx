"use client"

import { Shield, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface ComplianceCheck {
  overall_compliance: "COMPLIANT" | "NON_COMPLIANT" | "PARTIAL"
  standards: Record<string, "COMPLIANT" | "NON_COMPLIANT">
  violations: string[]
  recommendations: string[]
}

interface CompliancePanelProps {
  complianceCheck: ComplianceCheck
}

export function CompliancePanel({ complianceCheck }: CompliancePanelProps) {
  const getComplianceIcon = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return <CheckCircle className="h-5 w-5 text-green-400" />
      case "NON_COMPLIANT":
        return <XCircle className="h-5 w-5 text-red-400" />
      case "PARTIAL":
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />
      default:
        return <Shield className="h-5 w-5 text-gray-400" />
    }
  }

  const getComplianceColor = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return "text-green-400"
      case "NON_COMPLIANT":
        return "text-red-400"
      case "PARTIAL":
        return "text-yellow-400"
      default:
        return "text-gray-400"
    }
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Shield className="h-6 w-6 text-blue-400" />
        <h2 className="text-xl font-semibold text-white">Compliance Status</h2>
      </div>

      {/* Overall Compliance */}
      <div className="mb-6">
        <div className="flex items-center justify-between bg-black/50 rounded-lg p-4 border border-gray-800">
          <div className="flex items-center space-x-3">
            {getComplianceIcon(complianceCheck.overall_compliance)}
            <span className="text-white font-medium">Overall Compliance</span>
          </div>
          <span className={`font-bold ${getComplianceColor(complianceCheck.overall_compliance)}`}>
            {complianceCheck.overall_compliance}
          </span>
        </div>
      </div>

      {/* Standards Breakdown */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-white mb-3">Standards Compliance</h3>
        <div className="space-y-2">
          {Object.entries(complianceCheck.standards).map(([standard, status]) => (
            <div key={standard} className="flex items-center justify-between bg-black/30 rounded-lg p-3 border border-gray-800">
              <div className="flex items-center space-x-3">
                {getComplianceIcon(status)}
                <span className="text-gray-300 capitalize">
                  {standard.replace(/_/g, ' ')}
                </span>
              </div>
              <span className={`text-sm font-medium ${getComplianceColor(status)}`}>
                {status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Violations */}
      {complianceCheck.violations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium text-white mb-3">Violations</h3>
          <div className="space-y-2">
            {complianceCheck.violations.map((violation, index) => (
              <div key={index} className="flex items-start space-x-3 bg-red-900/20 rounded-lg p-3 border border-red-500/30">
                <XCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                <span className="text-red-300 text-sm">{violation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compliance Recommendations */}
      {complianceCheck.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-white mb-3">Compliance Recommendations</h3>
          <div className="space-y-2">
            {complianceCheck.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 bg-blue-900/20 rounded-lg p-3 border border-blue-500/30">
                <Shield className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-blue-300 text-sm">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 