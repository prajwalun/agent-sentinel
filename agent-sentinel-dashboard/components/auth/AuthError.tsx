"use client"

import { useSearchParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { AlertTriangle, ArrowLeft } from "lucide-react"
import { AuthLayout } from "./AuthLayout"

const errorMessages = {
  Configuration: "There is a problem with the server configuration.",
  AccessDenied: "You do not have permission to sign in.",
  Verification: "The verification token has expired or has already been used.",
  Default: "An error occurred during authentication.",
  OAuthSignin: "Error in constructing an authorization URL.",
  OAuthCallback: "Error in handling the response from an OAuth provider.",
  OAuthCreateAccount: "Could not create OAuth account in the database.",
  EmailCreateAccount: "Could not create email account in the database.",
  Callback: "Error in the OAuth callback handler route.",
  OAuthAccountNotLinked: "The email on the account is already linked, but not with this OAuth account.",
  EmailSignin: "Sending the e-mail with the verification token failed.",
  CredentialsSignin: "The credentials you provided are incorrect.",
  SessionRequired: "You must be signed in to view this page.",
}

export function AuthError() {
  const searchParams = useSearchParams()
  const error = searchParams.get("error") as keyof typeof errorMessages

  const errorMessage = errorMessages[error] || errorMessages.Default

  return (
    <AuthLayout title="Authentication Error" subtitle="There was a problem signing you in">
      <div className="text-center space-y-4">
        <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5" />
          <span>{errorMessage}</span>
        </div>

        <div className="space-y-2">
          <Link href="/auth/login">
            <Button className="w-full btn-primary">Try Again</Button>
          </Link>

          <Link href="/auth/login">
            <Button variant="ghost" className="w-full text-red-400 hover:text-red-300">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Sign In
            </Button>
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}
