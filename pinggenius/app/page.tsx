import HeroSection from "@/components/Hero";
import FeaturesSection from "@/components/FeatureSection";
import UseCasesSection from "@/components/UseCasesSection";
import FinalCTA from "@/components/FinalCTA";
import PricingSection from "@/components/PricingSection";
import Tension from "@/components/Tension";
import Proof from "@/components/Proof";
import SocialProof from "@/components/SocialProof";

export default async function Home() {

  return (
    <>
      <HeroSection />
      <Tension />
      <Proof />
      <FeaturesSection />
      <UseCasesSection />
      {/* <SocialProof /> */} {/* 🔴TODO: add this later */}
      <PricingSection />
      <FinalCTA />
    </>
  );
}
