"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Key,
  Plus,
  Copy,
  Check,
  Shield,
  Terminal,
  Trash2,
  Bell,
  AlertTriangle,
} from "lucide-react"
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

interface NotificationPrefs {
  criticalAlerts: boolean
  weeklyDigest: boolean
  analysisComplete: boolean
}

const DEFAULT_PREFS: NotificationPrefs = {
  criticalAlerts: true,
  weeklyDigest: false,
  analysisComplete: true,
}

function loadPrefs(): NotificationPrefs {
  try {
    const raw = localStorage.getItem("sentinel_notification_prefs")
    return raw ? { ...DEFAULT_PREFS, ...JSON.parse(raw) } : DEFAULT_PREFS
  } catch {
    return DEFAULT_PREFS
  }
}

export function SettingsView() {
  const { user } = useAuth()
  const [keys, setKeys] = useState<ApiKeyRecord[]>([])
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [keyName, setKeyName] = useState("")
  const [revoking, setRevoking] = useState<string | null>(null)
  const [confirmRevoke, setConfirmRevoke] = useState<string | null>(null)
  const [prefs, setPrefs] = useState<NotificationPrefs>(DEFAULT_PREFS)

  useEffect(() => {
    setPrefs(loadPrefs())
  }, [])

  const fetchKeys = useCallback(async () => {
    try {
      const data = await apiService.listApiKeys()
      setKeys(data.keys as ApiKeyRecord[])
    } catch {
      // Silently handle — empty key list shown
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
      const desc = keyName.trim() || "API key"
      const data = await apiService.createApiKey(desc)
      setNewKey(data.api_key)
      setKeyName("")
      await fetchKeys()
    } catch {
      // Generation failed — user can retry
    } finally {
      setGenerating(false)
    }
  }

  const handleRevoke = async (keyId: string) => {
    setRevoking(keyId)
    try {
      await apiService.revokeApiKey(keyId)
      setConfirmRevoke(null)
      await fetchKeys()
    } catch {
      // Revoke failed — user can retry
    } finally {
      setRevoking(null)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const togglePref = (key: keyof NotificationPrefs) => {
    setPrefs((prev) => {
      const updated = { ...prev, [key]: !prev[key] }
      localStorage.setItem("sentinel_notification_prefs", JSON.stringify(updated))
      return updated
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">
          Manage your API keys and account configuration
        </p>
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
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Keys
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Create new key */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              placeholder="Key name (e.g. Production, CI/CD)"
              className="flex-1 bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              maxLength={256}
            />
            <Button onClick={handleGenerate} disabled={generating} size="sm">
              <Plus className="h-4 w-4 mr-1" />
              {generating ? "Generating..." : "New Key"}
            </Button>
          </div>

          {/* Newly created key banner */}
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

          {/* Key list */}
          {loading ? (
            <div className="text-gray-500 text-sm">Loading keys...</div>
          ) : keys.length === 0 ? (
            <div className="text-gray-500 text-sm">
              No API keys yet. Generate one to start using the SDK.
            </div>
          ) : (
            <>
              {/* Active keys */}
              {keys.filter((k) => k.is_active).length === 0 ? (
                <div className="text-gray-500 text-sm">
                  No active keys. Generate one to start using the SDK.
                </div>
              ) : (
                <div className="space-y-2">
                  {keys
                    .filter((k) => k.is_active)
                    .map((key) => (
                      <div
                        key={key.id}
                        className="bg-gray-900/50 border border-gray-800 rounded p-3"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="text-white text-sm font-medium truncate">
                                {key.description || "API Key"}
                              </p>
                              <code className="text-xs text-gray-500 font-mono">
                                {key.id}
                              </code>
                            </div>
                            <p className="text-gray-500 text-xs mt-0.5">
                              Created{" "}
                              {new Date(key.created_at).toLocaleDateString()}
                              {key.last_used
                                ? ` · Last used ${new Date(key.last_used).toLocaleDateString()}`
                                : " · Never used"}
                              {" · "}
                              {key.call_count} calls
                            </p>
                          </div>
                          <div className="flex items-center gap-2 ml-3">
                            <span className="text-xs px-2 py-0.5 rounded whitespace-nowrap bg-green-900/30 text-green-400">
                              Active
                            </span>
                            {confirmRevoke !== key.id && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-gray-500 hover:text-red-400 p-1 h-auto"
                                onClick={() => setConfirmRevoke(key.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>

                        {confirmRevoke === key.id && (
                          <div className="mt-2 flex items-center gap-2 bg-red-900/10 border border-red-900/30 rounded p-2">
                            <p className="text-red-400 text-xs flex-1">
                              Revoke this key? Any integrations using it will
                              stop working.
                            </p>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-gray-400 text-xs h-7"
                              onClick={() => setConfirmRevoke(null)}
                            >
                              Cancel
                            </Button>
                            <Button
                              variant="destructive"
                              size="sm"
                              className="text-xs h-7"
                              disabled={revoking === key.id}
                              onClick={() => handleRevoke(key.id)}
                            >
                              {revoking === key.id ? "Revoking..." : "Revoke"}
                            </Button>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              )}

              {/* Revoked keys — collapsible */}
              {keys.filter((k) => !k.is_active).length > 0 && (
                <details className="mt-4">
                  <summary className="text-gray-500 text-xs cursor-pointer hover:text-gray-400 select-none">
                    {keys.filter((k) => !k.is_active).length} revoked{" "}
                    {keys.filter((k) => !k.is_active).length === 1
                      ? "key"
                      : "keys"}
                  </summary>
                  <div className="space-y-2 mt-2">
                    {keys
                      .filter((k) => !k.is_active)
                      .map((key) => (
                        <div
                          key={key.id}
                          className="bg-gray-900/30 border border-gray-800/50 rounded p-3 opacity-60"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <p className="text-gray-400 text-sm font-medium truncate line-through">
                                  {key.description || "API Key"}
                                </p>
                                <code className="text-xs text-gray-600 font-mono">
                                  {key.id}
                                </code>
                              </div>
                              <p className="text-gray-600 text-xs mt-0.5">
                                Created{" "}
                                {new Date(key.created_at).toLocaleDateString()}
                                {" · "}
                                {key.call_count} calls
                              </p>
                            </div>
                            <span className="text-xs px-2 py-0.5 rounded whitespace-nowrap bg-red-900/30 text-red-400">
                              Revoked
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </details>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {([
            {
              key: "criticalAlerts" as const,
              label: "Critical security alerts",
              desc: "Get notified immediately when critical threats are detected",
            },
            {
              key: "weeklyDigest" as const,
              label: "Weekly security digest",
              desc: "Receive a weekly summary of all security events",
            },
            {
              key: "analysisComplete" as const,
              label: "Analysis completion",
              desc: "Notify when a background analysis finishes",
            },
          ]).map((item) => (
            <div
              key={item.key}
              className="flex items-center justify-between py-2"
            >
              <div>
                <p className="text-white text-sm font-medium">{item.label}</p>
                <p className="text-gray-500 text-xs">{item.desc}</p>
              </div>
              <button
                onClick={() => togglePref(item.key)}
                className={`relative w-10 h-5 rounded-full transition-colors ${
                  prefs[item.key] ? "bg-blue-600" : "bg-gray-700"
                }`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                    prefs[item.key] ? "translate-x-5" : ""
                  }`}
                />
              </button>
            </div>
          ))}
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
            In a new terminal, install the Agent Sentinel SDK and set your API key to start
            monitoring your AI agents for security threats.
          </p>
          <pre className="bg-gray-900 border border-gray-700 rounded p-4 text-sm text-gray-300 overflow-x-auto">
{`# Create venv and install SDK
python3 -m venv venv && source venv/bin/activate
pip install agent-sentinel

# Set environment variables
export SENTINEL_API_URL="http://localhost:8001"
export SENTINEL_API_KEY="your-api-key-here"

# Use in your code
from agent_sentinel import monitor

@monitor
def my_agent(prompt: str) -> str:
    # Your agent logic here
    return response`}
          </pre>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-900/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="h-5 w-5" />
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white text-sm font-medium">Delete account</p>
              <p className="text-gray-500 text-xs">
                Permanently remove your account and all associated data
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-red-900/50 text-red-400 hover:bg-red-900/20 cursor-not-allowed opacity-50"
              disabled
            >
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
