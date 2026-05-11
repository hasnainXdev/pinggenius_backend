import NextAuth, { DefaultSession, DefaultUser } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id?: string
      name?: string | null
      email?: string | null
      role?: string
      isWaitlistUser?: boolean
      isProUser?: boolean
      usage: {
        emailAnalyses: number,
        autoReplies: number,
        sequencesCreated: number,
        contactsImported: number,
        lastReset: string,
      }
    } & DefaultSession["user"]
    access_token?: string
    refresh_token?: string
  }

  interface User extends DefaultUser {
    id?: string
    role?: string
    isWaitlistUser?: boolean
    isProUser?: boolean
    usage: {
      emailAnalyses: number,
      autoReplies: number,
      sequencesCreated: number,
      contactsImported: number,
      lastReset: string,
    }
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    access_token?: string
    refresh_token?: string
    role?: string
    isWaitlistUser?: boolean
    isProUser?: boolean
    usage: {
      emailAnalyses: number,
      autoReplies: number,
      sequencesCreated: number,
      contactsImported: number,
      lastReset: string,
    }
    id?: string
  }
}
