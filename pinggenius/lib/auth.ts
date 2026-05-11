import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import Users from "@/models/users";
import connectDB from "@/database/db";

export const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
            // authorization: {
            //     params: {
            //         scope: "openid email profile https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.send",
            //         access_type: "offline",
            //         prompt: "consent"
            //     },
            // },
        }),
    ],
    callbacks: {
        async jwt({ token, account, profile }) {
            if (account && profile?.email) {
                await connectDB()
                // Find or create user in DB
                const user = await Users.findOneAndUpdate(
                    { email: profile.email },
                    {
                        $setOnInsert: {
                            name: profile.name,
                            email: profile.email,
                            role: "user",
                            isWaitlistUser: false,
                            isProUser: false,
                        },
                        // $set: {
                        //     refresh_token: account.refresh_token || token.refresh_token, // keep existing
                        //     access_token: account.access_token,
                        //     token_created_at: new Date()
                        // }
                    },
                    { upsert: true, new: true }
                )

                token.role = user?.role || "user"
                token.id = user?._id
                token.isWaitlistUser = user?.isWaitlistUser
                token.isProUser = user?.isProUser
                // token.access_token = account.access_token
                // token.refresh_token = account.refresh_token
            }
            return token
        },
        async session({ session, token }) {
            session.user.role = token.role || "user"
            session.user.id = token.id
            session.user.isWaitlistUser = token.isWaitlistUser
            session.user.isProUser = token.isProUser
            // session.access_token = token.access_token
            // session.refresh_token = token.refresh_token
            return session
        }
    },
}


const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };