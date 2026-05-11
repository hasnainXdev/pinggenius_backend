import connectDB from "@/database/db";
import Contacts from "@/models/contacts";
import { NextRequest, NextResponse } from "next/server";

export async function DELETE(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const contact_id = searchParams.get("_id");

        if (!contact_id) {
            return NextResponse.json({ error: "Contact ID is required" }, { status: 400 });
        }

        await connectDB();
        await Contacts.findOneAndDelete({ _id: contact_id });

        return NextResponse.json({ message: "Contact deleted successfully" }, { status: 200 });

    } catch (err: any) {
        console.log("Internal Server Error:", err);
        console.error("Error deleting emails:", err.message);
    }
}