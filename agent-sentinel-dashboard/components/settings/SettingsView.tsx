"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Key, Plus, Copy, Check, Shield, Terminal } from "lucide-react"
import { apiService } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

interface ApiKeyRecord {
  id: string
  description: string
  created_at: string
  last_used: string | null
  call_count: number
  is_active: number
}

export function SettingsView() {
  const { user } = useAuth()
  const [keys, setKeys] = useState<ApiKeyRecord[]>([])
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const fetchKeys = useCallback(async () => {
    try {
      const data = await apiService.listApiKeys()
      setKeys(data.keys as ApiKeyRecord[])
    } catch {
      // Keys will show as empty
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchKeys()
  }, [fetchKeys])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const data = await apiService.createApiKey()
      setNewKey(data.api_key)
      await fetchKeys()
    } catch {
      // Error handled gracefully
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Manage your API keys and account configuration</p>
      </div>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Account
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-400">Email</span>
            <span className="text-white">{user?.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Name</span>
            <span className="text-white">{user?.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Member since</span>
            <span className="text-white">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : "—"}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* API Keys */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Keys
          </CardTitle>
          <Button onClick={handleGenerate} disabled={generating} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            {generating ? "Generating..." : "New Key"}
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {newKey && (
            <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 space-y-2">
              <p className="text-green-400 text-sm font-medium">
                New API key created — copy it now, it will not be shown again.
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 font-mono text-sm text-green-400 select-all break-all">
                  {newKey}
                </code>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(newKey)}
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-400" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          )}

          {loading ? (
            <div className="text-gray-500 text-sm">Loading keys...</div>
          ) : keys.length === 0 ? (
            <div className="text-gray-500 text-sm">
              No API keys yet. Generate one to start using the SDK.
            </div>
          ) : (
            <div className="space-y-2">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between bg-gray-900/50 border border-gray-800 rounded p-3"
                >
                  <div>
                    <p className="text-white text-sm font-medium">
                      {key.description || "API Key"}
                    </p>
                    <p className="text-gray-500 text-xs">
                      Created {new Date(key.created_at).toLocaleDateString()}
                      {key.last_used
                        ? ` · Last used ${new Date(key.last_used).toLocaleDateString()}`
                        : " · Never used"}
                      {" · "}{key.call_count} calls
                    </p>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      key.is_active
                        ? "bg-green-900/30 text-green-400"
                        : "bg-red-900/30 text-red-400"
                    }`}
                  >
                    {key.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Start */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Quick Start
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400 text-sm mb-3">
            Install the Agent Sentinel SDK and set your API key to start
            monitoring your AI agents for security threats.
          </p>
          <pre className="bg-gray-900 border border-gray-700 rounded p-4 text-sm text-gray-300 overflow-x-auto">
{`# Install the SDK
pip install agent-sentinel

# Set environment variables
export SENTINEL_API_KEY="your-api-key-here"
export SENTINEL_API_URL="http://localhost:8001"

# Use in your code
from agent_sentinel import monitor

@monitor
def my_agent(prompt: str) -> str:
    # Your agent logic here
    return response`}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
