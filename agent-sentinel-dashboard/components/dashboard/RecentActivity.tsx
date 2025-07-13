import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react"

interface ActivityEvent {
  id: string
  timestamp: string
  type: "security" | "performance" | "info"
  severity: "low" | "medium" | "high" | "critical"
  message: string
  agentId?: string
}

const mockEvents: ActivityEvent[] = [
  {
    id: "1",
    timestamp: "2 min ago",
    type: "security",
    severity: "critical",
    message: 'SQL injection detected in Agent "DataBot"',
    agentId: "databot-001",
  },
  {
    id: "2",
    timestamp: "5 min ago",
    type: "performance",
    severity: "medium",
    message: 'Performance warning in Agent "ChatBot"',
    agentId: "chatbot-001",
  },
  {
    id: "3",
    timestamp: "12 min ago",
    type: "info",
    severity: "low",
    message: 'Agent "MathAgent" completed successfully',
    agentId: "mathagent-001",
  },
  {
    id: "4",
    timestamp: "15 min ago",
    type: "security",
    severity: "critical",
    message: 'XSS attempt blocked in Agent "WebBot"',
    agentId: "webbot-001",
  },
]

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
  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
      <div className="space-y-0">
        {mockEvents.map((event) => (
          <ActivityItem key={event.id} event={event} />
        ))}
      </div>
      <div className="mt-4 pt-4 border-t border-gray-800">
        <button className="text-red-400 hover:text-red-300 text-sm font-medium">View All Activity →</button>
      </div>
    </div>
  )
}
