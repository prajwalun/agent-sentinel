import { DashboardLayout } from "@/components/dashboard/DashboardLayout"
import { StatusCards } from "@/components/dashboard/StatusCards"
import { RecentActivity } from "@/components/dashboard/RecentActivity"
import { QuickActions } from "@/components/dashboard/QuickActions"
import { SeverityChart } from "@/components/dashboard/SeverityChart"
import { SystemHealth } from "@/components/dashboard/SystemHealth"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Dashboard Overview
          </h1>
          <p className="text-gray-400">
            Monitor your AI agents and security status in real time
          </p>
        </div>

        <StatusCards />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RecentActivity />
          </div>
          <div className="space-y-6">
            <QuickActions />
            <SystemHealth />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SeverityChart />
        </div>
      </div>
    </DashboardLayout>
  )
}
