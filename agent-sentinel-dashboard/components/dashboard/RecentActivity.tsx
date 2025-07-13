"use client"

import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react"
import { useEffect, useState } from "react"
import { apiService, type SecurityEvent } from "@/lib/api"

interface ActivityEvent {
  id: string
  timestamp: string
  type: "security" | "performance" | "info"
  severity: "low" | "medium" | "high" | "critical"
  message: string
  agentId?: string
}

// Convert SecurityEvent to ActivityEvent format
const convertSecurityEvent = (event: SecurityEvent): ActivityEvent => ({
  id: event.id,
  timestamp: new Date(event.timestamp).toLocaleString(),
  type: "security",
  severity: event.severity,
  message: `${event.threat_type} detected in Agent "${event.agent_id}"`,
  agentId: event.agent_id,
})

function ActivityItem({ event }: { event: ActivityEvent }) {
  const getIcon = () => {
    switch (event.severity) {
      case "critical":
        return <XCircle className="h-5 w-5 text-red-400" />
      case "high":
        return <AlertTriangle className="h-5 w-5 text-orange-400" />
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />
      case "low":
        return <CheckCircle className="h-5 w-5 text-green-400" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  return (
    <div className="flex items-start space-x-3 py-3 border-b border-gray-800 last:border-b-0">
      {getIcon()}
      <div className="flex-1 min-w-0">
        <p className="text-white text-sm">{event.message}</p>
        <p className="text-gray-400 text-xs mt-1">{event.timestamp}</p>
      </div>
    </div>
  )
}

export function RecentActivity() {
  const [events, setEvents] = useState<ActivityEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecentEvents = async () => {
      try {
        const securityEvents = await apiService.getSecurityEvents()
        const activityEvents = securityEvents.slice(0, 5).map(convertSecurityEvent)
        setEvents(activityEvents)
      } catch (error) {
        console.error('Error fetching recent events:', error)
        // Show empty state instead of mock data
        setEvents([])
      } finally {
        setLoading(false)
      }
    }

    fetchRecentEvents()
  }, [])

  if (loading) {
    return (
      <div className="card-dark rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-start space-x-3 py-3">
              <div className="h-5 w-5 bg-gray-600 animate-pulse rounded-full"></div>
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-gray-600 animate-pulse rounded mb-2"></div>
                <div className="h-3 bg-gray-700 animate-pulse rounded w-20"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
      <div className="space-y-0">
        {events.length > 0 ? (
          events.map((event) => (
            <ActivityItem key={event.id} event={event} />
          ))
        ) : (
          <div className="text-center py-8">
            <Clock className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No recent activity</p>
            <p className="text-gray-500 text-sm mt-1">Security events will appear here</p>
          </div>
        )}
      </div>
      <div className="mt-4 pt-4 border-t border-gray-800">
        <button className="text-red-400 hover:text-red-300 text-sm font-medium">View All Activity →</button>
      </div>
    </div>
  )
}
