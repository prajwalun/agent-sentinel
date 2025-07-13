import { Button } from "@/components/ui/button"
import { BarChart3, Users, Settings } from "lucide-react"

export function QuickActions() {
  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Button className="btn-primary flex items-center space-x-2 h-12">
          <BarChart3 className="h-5 w-5" />
          <span>Generate Report</span>
        </Button>
        <Button className="btn-primary flex items-center space-x-2 h-12">
          <Users className="h-5 w-5" />
          <span>View All Agents</span>
        </Button>
        <Button className="btn-primary flex items-center space-x-2 h-12">
          <Settings className="h-5 w-5" />
          <span>Settings</span>
        </Button>
      </div>
    </div>
  )
}
