"use client"

import type React from "react"
import { useState, useRef, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Upload,
  FileText,
  AlertCircle,
  Loader2,
  Terminal,
} from "lucide-react"
import { apiService, type EnhancedIntelligenceReport } from "@/lib/api"

interface ReportUploadProps {
  onReportSelect: (report: EnhancedIntelligenceReport) => void
}

type AnalysisStage = "idle" | "uploading" | "analyzing" | "polling" | "error"

const STAGE_LABELS: Record<AnalysisStage, string> = {
  idle: "",
  uploading: "Reading file...",
  analyzing: "Starting AI analysis...",
  polling: "AI agents working — this takes a few minutes...",
  error: "Analysis failed",
}

export function ReportUpload({ onReportSelect }: ReportUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stage, setStage] = useState<AnalysisStage>("idle")
  const [runId, setRunId] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  useEffect(() => () => stopPolling(), [stopPolling])

  const startPolling = useCallback(
    (id: string) => {
      setStage("polling")
      setRunId(id)
      pollingRef.current = setInterval(async () => {
        try {
          const status = await apiService.getAnalysisStatus(id)
          if (status.status === "completed" && status.result) {
            stopPolling()
            onReportSelect(status.result)
          } else if (status.status === "failed") {
            stopPolling()
            setStage("error")
            setError(status.error || "Analysis failed")
          }
        } catch {
          // keep polling on transient network error
        }
      }, 3000)
    },
    [onReportSelect, stopPolling]
  )

  const analyzeContent = useCallback(
    async (content: string, agentId?: string) => {
      setError(null)
      setStage("analyzing")
      try {
        const { run_id } = await apiService.startAnalysis(content, agentId)
        startPolling(run_id)
      } catch {
        // Fallback: synchronous analysis
        try {
          const report = await apiService.enhanceSecurityReport(content, agentId)
          onReportSelect(report)
        } catch (err) {
          setStage("error")
          setError(err instanceof Error ? err.message : "Analysis failed")
        }
      }
    },
    [onReportSelect, startPolling]
  )

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    const file = files[0]
    const allowed = [".json", ".txt", ".log", ".csv", ".md"]
    const ext = "." + (file.name.split(".").pop()?.toLowerCase() || "")

    if (!allowed.includes(ext)) {
      setError(`Unsupported file type. Allowed: ${allowed.join(", ")}`)
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10 MB")
      return
    }

    setSelectedFile(file.name)
    setStage("uploading")
    setError(null)

    try {
      const content = await file.text()
      const agentId = file.name.replace(/\.[^.]+$/, "")
      await analyzeContent(content, agentId)
    } catch (err) {
      setStage("error")
      setError(err instanceof Error ? err.message : "Failed to read file")
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === "dragenter" || e.type === "dragover")
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    handleFiles(e.dataTransfer.files)
  }

  const isProcessing =
    stage === "uploading" || stage === "analyzing" || stage === "polling"

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${
          dragActive
            ? "border-red-500 bg-red-500/10"
            : "border-gray-700 hover:border-gray-500"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="mx-auto w-14 h-14 bg-gray-800 rounded-full flex items-center justify-center">
            <Upload className="w-7 h-7 text-gray-400" />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {selectedFile && isProcessing
                ? selectedFile
                : "Upload a Security Report"}
            </h3>
            <p className="text-gray-400 text-sm mb-1">
              Drag and drop, or click to browse
            </p>
            <p className="text-gray-600 text-xs">
              JSON, TXT, LOG, CSV, MD — max 10 MB
            </p>
          </div>

          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {STAGE_LABELS[stage]}
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Choose File
              </>
            )}
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.txt,.log,.csv,.md"
            onChange={(e) => handleFiles(e.target.files)}
            className="hidden"
          />
        </div>
      </div>

      {/* Background analysis notice */}
      {stage === "polling" && (
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 space-y-2">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-blue-400 animate-spin flex-shrink-0" />
            <span className="text-blue-400 font-medium">
              Multi-agent analysis running in background
            </span>
          </div>
          <p className="text-blue-300 text-sm pl-8">
            The AI is working through threat detection, risk assessment, and
            intelligence research. Feel free to navigate the rest of the site —
            check the <strong>Analysis History</strong> tab for results when
            done.
          </p>
          {runId && (
            <p className="text-gray-600 text-xs pl-8 font-mono">
              Run ID: {runId}
            </p>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <span className="text-red-400">{error}</span>
        </div>
      )}

      {/* Where to get a report */}
      <div className="bg-gray-900/60 border border-gray-800 rounded-lg p-6 space-y-4">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <Terminal className="h-4 w-4 text-red-500" />
          Where do I get a report file?
        </h3>

        <p className="text-gray-400 text-sm">
          After monitoring your agent with the SDK, generate a JSON report
          and upload it here for AI-powered analysis:
        </p>

        <div className="bg-black rounded-lg p-4 font-mono text-sm text-gray-300 space-y-1">
          <p className="text-gray-500"># pip install agent-sentinel</p>
          <p>
            <span className="text-red-400">from</span> agent_sentinel{" "}
            <span className="text-red-400">import</span> AgentSentinel, monitor
          </p>
          <p>&nbsp;</p>
          <p>sentinel = AgentSentinel()</p>
          <p>&nbsp;</p>
          <p className="text-gray-500"># Wrap your agent with @monitor</p>
          <p>@monitor</p>
          <p>
            <span className="text-red-400">def</span>{" "}
            <span className="text-blue-400">my_agent</span>(prompt):
          </p>
          <p>    <span className="text-red-400">return</span> llm.invoke(prompt)</p>
          <p>&nbsp;</p>
          <p className="text-gray-500"># Run your agent, then generate the report</p>
          <p>my_agent(<span className="text-green-400">&quot;user query&quot;</span>)</p>
          <p>report_path = sentinel.generate_unified_report()</p>
          <p className="text-gray-500"># Upload the JSON file at report_path here</p>
        </div>

        <p className="text-gray-500 text-xs">
          The report is saved to the{" "}
          <code className="text-gray-400">logs/</code> folder in your project
          directory. Alternatively, trigger analysis directly from the{" "}
          <strong className="text-gray-300">Agents</strong> page for any agent
          that has already pushed events to this dashboard via the SDK.
        </p>
      </div>

      {/* How analysis works */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { step: 1, label: "Upload", desc: "Submit your SDK-generated report" },
          { step: 2, label: "Detect", desc: "AI scans for threats and patterns" },
          { step: 3, label: "Research", desc: "Enriched with threat intelligence" },
          { step: 4, label: "Report", desc: "Actionable recommendations" },
        ].map(({ step, label, desc }) => (
          <div key={step} className="flex items-start gap-3">
            <span className="bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs flex-shrink-0 mt-0.5">
              {step}
            </span>
            <div>
              <p className="text-white text-sm font-medium">{label}</p>
              <p className="text-gray-500 text-xs">{desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
