import connectDB from "@/database/db";
import Email from "@/models/emails";
import HardEmail from "@/models/hard_emails";
import { NextResponse, NextRequest } from "next/server";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id") as string | null;

    if (!user_id) {
      return NextResponse.json(
        { success: false, error: "User ID is required" },
        { status: 400 }
      );
    }

    await connectDB();

    // normal emails collection se data
    const emails = await Email.find({ user_id }).lean();

    // hard_emails collection se data
    const hardEmails = await HardEmail.find({ user_id }).lean();

    return NextResponse.json(
      {
        success: true,
        data: {
          emails,
          hardEmails,
        },
        message: "Emails + HardEmails fetched successfully",
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Internal Server Error:", error);
    return NextResponse.json(
      { success: false, message: "Error fetching emails" },
      { status: 500 }
    );
  }
}
