import connectDB from "@/database/db";
import HardEmails from "@/models/hard_emails";
import { NextRequest, NextResponse } from "next/server";


export async function GET(req: NextRequest) {
    try {

        const { searchParams } = new URL(req.url);
        const user_id = searchParams.get('user_id');

        if (!user_id) {
            return NextResponse.json({ error: "User ID is required" }, { status: 400 });
        }

        await connectDB()
        const hardEmails = await HardEmails.find({ user_id });

        if (!hardEmails || hardEmails.length === 0) {
            return NextResponse.json({ message: "No hard emails found" }, { status: 404 });
        }

        return NextResponse.json({ hardEmails, message: "Hard emails fetched successfully" }, { status: 200 });

    } catch (err: any) {
        console.error("Error fetching hard emails:", err);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}