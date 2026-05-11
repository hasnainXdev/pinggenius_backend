import connectDB from "@/database/db";
import Email from "@/models/emails";
import { ObjectId } from "mongoose";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const user_id = searchParams.get("user_id");

        if (!user_id) {
            return NextResponse.json({ error: "User ID is required" }, { status: 400 });
        }

        await connectDB();
        const emails = await Email.find({ user_id: user_id });


        if (!emails || emails.length === 0) {
            return NextResponse.json({ error: "No emails found for this user" }, { status: 404 });
        }

        return NextResponse.json({ emails, message: "Emails fetched successfully" }, { status: 200 });

    } catch (err: any) {
        console.log("Internal Server Error:", err);
        console.error("Error fetching emails:", err.message);
    }
}