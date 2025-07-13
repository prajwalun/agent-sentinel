"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, Shield, Users, AlertTriangle, Clock, TrendingUp } from "lucide-react"
import { useEffect, useState } from "react"
import { apiService, DashboardStats } from "@/lib/api"

export function StatusCards() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error('Error fetching dashboard stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Loading...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 animate-pulse rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!stats) {
    return <div>Error loading dashboard statistics</div>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Total Agents
          </CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_agents}</div>
          <p className="text-xs text-muted-foreground">
            {stats.active_agents} active
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Security Threats
          </CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_threats}</div>
          <p className="text-xs text-muted-foreground">
            {stats.critical_threats} critical
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Avg Response Time
          </CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.avg_response_time}ms</div>
          <p className="text-xs text-muted-foreground">
            {stats.success_rate}% success rate
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            System Health
          </CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.success_rate}%</div>
          <p className="text-xs text-muted-foreground">
            Overall performance
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
