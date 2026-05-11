import Link from "next/link";

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold mb-6 text-primary">Privacy Policy</h1>
      <p className="mb-4">
        Last updated: October 2025
      </p>

      <p className="mb-4">
        PingGenius (“we”, “our”, or “us”) respects your privacy and is committed to protecting your personal data.
        This Privacy Policy explains how we collect, use, and store information when you use our website or services.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">1. Information We Collect</h2>
      <p className="mb-4">
        We collect basic account information such as your name, email address, and profile data when you sign in using Google.
        We may also store metadata related to your connected Gmail account, but we never access or read your private emails without your explicit consent.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">2. How We Use Your Information</h2>
      <p className="mb-4">
        The data we collect is used to operate and improve PingGenius. We use it for authentication, sending automated replies, and personalizing your experience.
        We never sell or share your data with third parties for advertising.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">3. Google User Data</h2>
      <p className="mb-4">
        PingGenius uses Google OAuth to connect your Gmail account securely. Access to your Gmail is strictly limited to the features you authorize.
        We comply with Google API Services User Data Policy, including the Limited Use requirements.
      </p>
      <p className="mb-4">
        You can disconnect your Google account at any time from your PingGenius dashboard or your Google account settings.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">4. Data Security</h2>
      <p className="mb-4">
        We use secure HTTPS connections and encrypted data storage to protect your information from unauthorized access, alteration, or destruction.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">5. Your Rights</h2>
      <p className="mb-4">
        You can request deletion of your data or revoke access at any time. Simply contact us at <a href="https://x.com/HasnainXDev" className="text-primary underline">Twitter @HasnainXDev</a>.
      </p>

      <h2 className="text-xl font-semibold mt-8 mb-3">6. Changes to This Policy</h2>
      <p className="mb-4">
        We may update this Privacy Policy from time to time. The updated version will always be available at this page.
      </p>

      <p className="mt-8">
        If you have any questions about this policy or your data, please contact the founder directly at{" "}
        <Link href="https://x.com/HasnainXDev" className="text-primary underline">Twitter @HasnainXDev</Link>.
      </p>
    </div>
  );
}
