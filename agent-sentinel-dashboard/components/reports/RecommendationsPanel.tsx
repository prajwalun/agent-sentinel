"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Lightbulb, CheckSquare } from "lucide-react"

interface RecommendationsPanelProps {
  recommendations: string[]
  nextActions: string[]
}

export function RecommendationsPanel({ recommendations, nextActions }: RecommendationsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="card-dark rounded-lg p-6">
      <button onClick={() => setIsExpanded(!isExpanded)} className="flex items-center justify-between w-full text-left">
        <h2 className="text-xl font-semibold text-white">Recommendations & Next Actions</h2>
        {isExpanded ? (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recommendations */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Lightbulb className="h-5 w-5 text-yellow-400" />
              <h3 className="text-lg font-semibold text-white">Recommendations</h3>
            </div>
            <ul className="space-y-3">
              {recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start space-x-3 p-3 bg-black/50 rounded border border-gray-800">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Next Actions */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <CheckSquare className="h-5 w-5 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Next Actions</h3>
            </div>
            <ul className="space-y-3">
              {nextActions.map((action, index) => (
                <li key={index} className="flex items-start space-x-3 p-3 bg-black/50 rounded border border-gray-800">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">{action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
