
"use server";

export async function getCustomerIdFromSubscription(subscriptionId: string): Promise<string | undefined> {
    try {
        const url = `https://api.lemonsqueezy.com/v1/subscriptions/${subscriptionId}?include=customer`;

        const res = await fetch(url, {
            headers: {
                Authorization: `Bearer ${process.env.LEMON_SQUEEZY_API_KEY}`,
                Accept: 'application/vnd.api+json',
            },
            cache: 'no-store' // Important for serverless environments
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error('❌ Subscription fetch failed:', {
                status: res.status,
                error: errorText,
                subscriptionId
            });
            return undefined;
        }

        const data = await res.json();

        // Correct path to customer ID with error checking
        const customerId = data?.data?.relationships?.customer?.data?.id;

        if (!customerId) {
            console.error('❌ Customer ID not found in response:', {
                subscriptionId,
                responseData: data
            });
        }

        return customerId;
    } catch (err) {
        console.error('❌ Error in getCustomerIdFromSubscription:', {
            error: err,
            subscriptionId
        });
        return undefined;
    }
}
