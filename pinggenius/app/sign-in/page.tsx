"use client"

import GoogleSignInButton from "@/components/google-signin-button"

export default function SignInPage() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-200">
      <div className="p-16 rounded-xl bg-white shadow-md items-center">
        <GoogleSignInButton />
      </div>
    </div>
  )
}
