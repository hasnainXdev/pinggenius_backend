import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import connectDB from '@/database/db';
import User from '@/models/users';
import { getCustomerIdFromSubscription } from '@/lib/lemon-customer-id';

export async function POST(req: NextRequest) {
    try {
        const rawBody = await req.text();
        const signature = req.headers.get('X-Signature') || '';
        const secret = process.env.LEMON_SQUEEZY_WEBHOOK_SECRET;

        if (!secret) {
            console.error('❌ Missing LEMON_SQUEEZY_WEBHOOK_SECRET');
            return NextResponse.json({ error: 'Server misconfiguration' }, { status: 500 });
        }

        // Validate signature
        const expectedSignature = crypto
            .createHmac('sha256', secret)
            .update(rawBody)
            .digest('hex');

        if (signature !== expectedSignature) {
            console.warn('⚠️ Invalid webhook signature');
            return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
        }

        // Parse JSON
        let event;
        try {
            event = JSON.parse(rawBody);
        } catch {
            return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
        }

        const eventName = event.meta.event_name;
        const email =
            event.data.attributes?.user_email || event.data.attributes?.customer_email;

        console.log(`✅ Received event: ${eventName}`);

        // ✅ Handle created / payment_success events
        if (eventName === 'subscription_created' || eventName === 'subscription_payment_success') {
            await connectDB();

            // Step 1: Get details from event
            let customerId = event.data.attributes?.customer_id;
            const subscriptionId = event.data.id;

            console.log(`🔄 Event: ${eventName}, Subscription ID: ${subscriptionId}, Customer ID: ${customerId}`);

            console.log("event raw data", event.data);


            // Step 2: If customerId is missing, recover from DB
            if (!customerId && email) {
                const existingUser = await User.findOne({ email });
                if (existingUser?.lemonCustomerId) {
                    customerId = existingUser.lemonCustomerId;
                    console.log('♻️ Restored customer ID from DB:', customerId);
                }
            }

            // Step 3: If still missing, log and skip safely
            if (!email || !customerId) {
                console.warn('⚠️ Missing email or customer_id', { email, customerId });
                return NextResponse.json({ error: 'Missing data' }, { status: 400 });
            }

            // Step 4: Mark as Pro user
            const result = await User.updateOne(
                { email },
                {
                    $set: {
                        isProUser: true,
                        lemonCustomerId: customerId,
                    },
                },
                { upsert: true }
            );

            console.log(`✅ User updated to Pro: ${email}`, result);
            return NextResponse.json({ success: true });
        }


        // Handle cancellation
        if (eventName === 'subscription_cancelled') {
            const customerId = event.data?.attributes?.customer_id;

            if (!email && !customerId) {
                console.warn('⚠️ Missing both email and customer_id');
                return NextResponse.json({ error: 'Missing identifiers' }, { status: 400 });
            }

            await connectDB();
            const updateQuery = customerId ? { lemonCustomerId: customerId } : { email };

            const result = await User.updateOne(updateQuery, { $set: { isProUser: false } });

            console.log(`🔄 Updated user (cancelled): ${email || customerId}`, result);
            return NextResponse.json({ success: true });
        }

        return NextResponse.json({ message: 'Unhandled event' });
    } catch (err) {
        console.error('❌ Webhook error:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
