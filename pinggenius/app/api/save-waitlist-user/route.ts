import { NextResponse } from "next/server";
import connectDB from "@/database/db";
import WaitlistsUser from "@/models/WaitlistsUser";



function extractNameFromEmail(email: string) {
  const username = email.split('@')[0]
  return username.replace(/[\W_]/g, ' ').replace(/\s+/g, ' ').trim()
}
export async function POST(req: Request) {
  await connectDB()
  try {
    const { email, linkedin } = await req.json()

    if (!email) {
      return NextResponse.json({ meesage: 'Email is required' }, { status: 400 })
    }

    const isExistingUser = await WaitlistsUser.findOne({ email })

    if (isExistingUser) {
      return NextResponse.json({ meesage: 'Email already exists' }, { status: 400 })
    }


    const username = extractNameFromEmail(email)

    const waitlistUser = await WaitlistsUser.create({
      email,
      username,
      role: 'user',
      linkedin: linkedin || "not_provided",
      isWaitlisted: true,
    })



    return NextResponse.json({ message: 'Added to waitlist', waitlistUser }, { status: 200 })
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error }, { status: 500 });
  }
}