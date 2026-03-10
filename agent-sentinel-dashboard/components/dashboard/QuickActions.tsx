"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { BarChart3, Users, Settings, Shield } from "lucide-react"

export function QuickActions() {
  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Link href="/reports">
          <Button className="btn-primary flex items-center space-x-2 h-12 w-full">
            <BarChart3 className="h-5 w-5" />
            <span>Upload Report</span>
          </Button>
        </Link>
        <Link href="/agents">
          <Button className="btn-primary flex items-center space-x-2 h-12 w-full">
            <Users className="h-5 w-5" />
            <span>View Agents</span>
          </Button>
        </Link>
        <Link href="/settings">
          <Button variant="outline" className="flex items-center space-x-2 h-12 w-full border-gray-700 text-gray-300 hover:text-white">
            <Settings className="h-5 w-5" />
            <span>API Keys</span>
          </Button>
        </Link>
        <Link href="/reports">
          <Button variant="outline" className="flex items-center space-x-2 h-12 w-full border-gray-700 text-gray-300 hover:text-white">
            <Shield className="h-5 w-5" />
            <span>Analysis History</span>
          </Button>
        </Link>
      </div>
    </div>
  )
}
