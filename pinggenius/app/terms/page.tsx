import Link from "next/link";

export default function TermsPage() {
    return (
        <div className="max-w-3xl mx-auto px-6 py-16">
            <h1 className="text-3xl font-bold mb-6 text-primary">Terms of Service</h1>
            <p className="mb-4">Last updated: October 2025</p>

            <p className="mb-4">
                Welcome to PingGenius! These Terms of Service (“Terms”) govern your use of our website, products, and services.
                By using PingGenius, you agree to comply with and be bound by these Terms.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">1. Use of Our Service</h2>
            <p className="mb-4">
                You agree to use PingGenius only for lawful purposes and in compliance with applicable laws.
                You must not misuse the platform, interfere with its functionality, or attempt unauthorized access.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">2. Accounts and Security</h2>
            <p className="mb-4">
                You are responsible for maintaining the confidentiality of your account credentials and all activity under your account.
                PingGenius is not liable for any loss resulting from unauthorized use of your account.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">3. Intellectual Property</h2>
            <p className="mb-4">
                All content, branding, and features of PingGenius are the property of PingGenius and its founder, Muhammad Hasnain.
                You may not copy, modify, or distribute any part of our platform without written permission.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">4. Limitation of Liability</h2>
            <p className="mb-4">
                PingGenius is provided on an “as is” basis without warranties of any kind.
                We are not liable for any direct, indirect, or incidental damages arising from your use of the service.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">5. Termination</h2>
            <p className="mb-4">
                We may suspend or terminate your access if you violate these Terms or misuse the service.
            </p>

            <h2 className="text-xl font-semibold mt-8 mb-3">6. Changes to Terms</h2>
            <p className="mb-4">
                We may update these Terms at any time. The updated version will always be available on this page.
            </p>

            <p className="mt-8">
                For support or questions, contact the founder at{" "}
                <Link href="https://x.com/HasnainXDev" className="text-primary underline">Twitter @HasnainXDev</Link>.
            </p>
        </div>
    );
}
