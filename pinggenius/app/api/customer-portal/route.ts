import connectDB from "@/database/db";
import User from "@/models/users";
import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();
    const storeId = process.env.LEMON_SQUEEZY_STORE_ID;
    const apiKey = process.env.LEMON_SQUEEZY_API_KEY;

    if (!storeId || !apiKey) {
      console.error("❌ Missing environment variables");
      return NextResponse.json(
        { error: "Server misconfigured" },
        { status: 500 }
      );
    }

    await connectDB();
    const user = await User.findOne({ email });
    if (!user?.lemonCustomerId) {
      return NextResponse.json(
        { error: "Customer not found" },
        { status: 404 }
      );
    }

    // Verify customer exists in Lemon Squeezy
    const customerCheck = await axios.get(
      `https://api.lemonsqueezy.com/v1/customers/${user?.lemonCustomerId}`,
      {
        headers: {
          Authorization: `Bearer ${process.env.LEMON_SQUEEZY_API_KEY}`,
          Accept: 'application/vnd.api+json'
        }
      }
    );

    console.log('✅ Customer Verification:', customerCheck.data);


    // ✅ Generate Customer Portal URL (correct endpoint + body)
    const response = await axios.post(
      `https://api.lemonsqueezy.com/v1/stores/${storeId}/customer-portals`,
      {
        data: {
          type: "customer-portals",
          attributes: {
            store_id: storeId,
            customer_id: user.lemonCustomerId,
            return_url: `${process.env.NEXT_PUBLIC_API_BASE_URL}/dashboard`,
          },
        },
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/vnd.api+json",
          Accept: "application/vnd.api+json",
        },
        timeout: 10000,
      }
    );

    const attrs = response.data?.data?.attributes;
    const portalUrl =
      attrs?.url ||
      attrs?.urls?.customer_portal ||
      attrs?.urls?.customerPortal ||
      null;

    console.log(portalUrl);

    if (!portalUrl)
      throw new Error("Portal URL missing from Lemon Squeezy response");

    return NextResponse.json({ url: portalUrl });
  } catch (error: any) {
    console.error("❌ Full Error:", {
      message: error.message,
      response: error.response?.data,
      config: error.config,
    });

    return NextResponse.json(
      { error: "Failed to generate portal URL" },
      { status: 500 }
    );
  }
}
