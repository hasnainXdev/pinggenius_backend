"use client"

import { signIn, signOut, useSession } from "next-auth/react"
import { Button } from "@/components/ui/button"
import Image from "next/image"
import { Skeleton } from "@/components/ui/skeleton"
import { useRouter } from "next/navigation";

export default function GoogleSignInButton() {
  const { data: session, status } = useSession()
  const router = useRouter()

  if (status === "loading") {
    return (
      <Skeleton className="h-10 w-36 rounded-md bg-gray-200" />
    )
  }


  if (session) {
    return (
      <div className="flex flex-col items-center justify-center gap-6">
        <p className="text-base md:text-lg font-semibold text-black">
          Welcome, {session.user?.name}!
        </p>
        <Button
          size={"sm"}
          onClick={() => { router.push("/"); signOut() }}
          className="rounded-lg bg-red-500 hover:bg-red-700 flex items-center justify-center cursor-pointer"
        >
          Sign Out
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center gap-8">
      <h1 className="text-xl md:text-2xl font-bold text-gray-900">Welcome, to PingGenius</h1>
      <Button
        onClick={() => signIn("google")}
        className="cursor-pointer bg-gray-900 hover:bg-gray-700 text-white rounded-md font-normal transition-all duration-300 hover:shadow-lg hover:scale-105"
      >
        Sign in with Google <Image src="/google-icon.svg" alt="Google Logo icon" width={16} height={16} className="inline-block h-4 w-4 ml-2" />
      </Button>
    </div>
  )
}
