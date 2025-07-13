"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Upload, FileText, AlertCircle, Loader2, CheckCircle } from "lucide-react"
import { apiService, type EnhancedIntelligenceReport } from "@/lib/api"

interface ReportUploadProps {
  onReportSelect: (report: EnhancedIntelligenceReport) => void
}

export function ReportUpload({ onReportSelect }: ReportUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [processingStage, setProcessingStage] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    const file = files[0]
    
    // Validate file type
    const allowedTypes = ['.json', '.txt', '.log', '.csv']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(fileExtension)) {
      setError(`Unsupported file type. Please upload: ${allowedTypes.join(', ')} files`)
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB")
      return
    }

    setError(null)
    setLoading(true)
    setProcessingStage("Uploading file...")

    try {
      // Upload and analyze the file
      setProcessingStage("Analyzing with AI intelligence...")
      const enhancedReport = await apiService.uploadReportFile(file)
      
      setProcessingStage("Report ready!")
      onReportSelect(enhancedReport)
    } catch (err) {
      console.error("Error processing file:", err)
      setError(err instanceof Error ? err.message : "Failed to process file")
    } finally {
      setLoading(false)
      setProcessingStage("")
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  return (
    <div className="space-y-6">
      {/* File Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? "border-red-500 bg-red-500/10" 
            : "border-gray-600 hover:border-gray-500"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="mx-auto w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center">
            <Upload className="w-6 h-6 text-gray-400" />
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Upload Security Report</h3>
            <p className="text-gray-400 mb-4">
              Drag and drop your security report or click to browse
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supported formats: JSON, TXT, LOG, CSV (max 10MB)
            </p>
          </div>

          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
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
            accept=".json,.txt,.log,.csv"
            onChange={handleFileInput}
            className="hidden"
          />
        </div>
      </div>

      {/* Processing Status */}
      {loading && processingStage && (
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            <span className="text-blue-400 font-medium">{processingStage}</span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-400">{error}</span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-900/50 rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-3">How it works</h3>
        <ol className="text-gray-300 space-y-2 text-sm">
          <li className="flex items-start">
            <span className="bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">1</span>
            Upload your security report in JSON, TXT, LOG, or CSV format
          </li>
          <li className="flex items-start">
            <span className="bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">2</span>
            Our AI intelligence engine analyzes the report for threats and patterns
          </li>
          <li className="flex items-start">
            <span className="bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs mr-3 mt-0.5">3</span>
            Get enhanced insights, threat analysis, and actionable recommendations
          </li>
        </ol>
      </div>
    </div>
  )
}

