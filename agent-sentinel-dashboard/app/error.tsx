"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error("Unhandled error:", error)
  }, [error])

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="text-red-500 text-5xl font-bold">Oops</div>
        <h2 className="text-xl font-semibold text-white">
          Something went wrong
        </h2>
        <p className="text-gray-400 text-sm">
          An unexpected error occurred. You can try again or return to the
          dashboard.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Button onClick={reset} variant="outline" className="text-white border-gray-600">
            Try Again
          </Button>
          <Button
            onClick={() => (window.location.href = "/dashboard")}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  )
}
