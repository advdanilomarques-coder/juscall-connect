import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import SectionEngineer from "@/components/SectionEngineer";
import PowerCards from "@/components/PowerCards";
import CopilotDemo from "@/components/CopilotDemo";
import HowItWorks from "@/components/HowItWorks";
import HybridIntel from "@/components/HybridIntel";
import Compatibility from "@/components/Compatibility";
import About from "@/components/About";
import Community from "@/components/Community";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="relative">
      <Nav />
      <Hero />
      <SectionEngineer />
      <PowerCards />
      <CopilotDemo />
      <HowItWorks />
      <HybridIntel />
      <Compatibility />
      <About />
      <Community />
      <FinalCTA />
      <Footer />
    </main>
  );
}
