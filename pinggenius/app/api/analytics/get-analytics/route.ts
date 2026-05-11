import connectDB from "@/database/db";
import AnalyticsOverview from "@/models/AnalyticsOverview";
import { NextResponse, NextRequest } from "next/server";

export async function GET(req: NextRequest) {
    try {

        const { searchParams } = new URL(req.url);
        const user_id = searchParams.get("user_id") as string | null;

        if (!user_id) {
            return NextResponse.json({ success: false, error: "User ID is required" }, { status: 400 });
        }

        await connectDB();
        const analytics = await AnalyticsOverview.findOne({ userId: user_id });

        if (!analytics) {
            return NextResponse.json(
                { success: false, error: "No analytics found" },
                { status: 404 }
            );
        }


        return NextResponse.json(
            { success: true, data: analytics, message: "Analytics fetched successfully" },
            { status: 200 }
        );


    } catch (error) {
        console.error("Internal Server Error:", error);
        return NextResponse.json({ success: false, message: "Error fetching analytics" }, { status: 500 });
    }
}