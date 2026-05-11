import connectDB from "@/database/db";
import Contacts from "@/models/contacts";
import { NextRequest, NextResponse } from "next/server";


export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const contact_id = searchParams.get("_id");

        if (!contact_id) {
            return NextResponse.json({ error: "Contact ID is required" }, { status: 400 });
        }

        await connectDB();
        const contact = await Contacts.findOne({ _id: contact_id });

        if (!contact) {
            return NextResponse.json({ error: "Contact not found" }, { status: 404 });
        }

        return NextResponse.json({ contact, message: "Contact fetched successfully" }, { status: 200 });

    } catch (error) {
        console.log("Internal Server Error:", error)
        return NextResponse.json({ message: "Error fetching contact" }, { status: 500 });
    }
}