import { NextResponse, NextRequest } from "next/server";
import connectDB from "@/database/db";
import User from "@/models/users";
import mongoose from "mongoose";

export async function GET(req: NextRequest) {
    try {
        const searchParams = req.nextUrl.searchParams;
        const user_id = searchParams.get("user_id");

        if (!user_id) {
            return NextResponse.json({ error: "User ID is required" }, { status: 400 });
        }

        // validate if it's a valid ObjectId
        if (!mongoose.Types.ObjectId.isValid(user_id)) {
            return NextResponse.json({ error: "Invalid user ID format" }, { status: 400 });
        }

        await connectDB();
        const user = await User.findOne({ _id: user_id });
        if (!user) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        return NextResponse.json({ user, message: "User fetched successfully" }, { status: 200 });
    } catch (error) {
        console.log("internal server error", error);
        return NextResponse.json({ message: "Error fetching user" }, { status: 500 });
    }
};