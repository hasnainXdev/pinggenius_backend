import connectDB from "@/database/db";
import Sequences from "@/models/sequence";
import { NextResponse, NextRequest } from "next/server";


export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const user_id = searchParams.get("user_id");

        if (!user_id) {
            return NextResponse.json({ error: "User ID is required" }, { status: 400 });
        }

        await connectDB();
        const sequences = await Sequences.find({ user_id: user_id });

        if (!sequences || sequences.length === 0) {
            return NextResponse.json({ error: "No sequences found for this user" }, { status: 404 });
        }

        return NextResponse.json({ sequences, message: "Sequences fetched successfully" }, { status: 200 });

    } catch (err: any) {
        console.log("Internal Server Error:", err);
        console.error("Error fetching sequences:", err.message);
    }
}
