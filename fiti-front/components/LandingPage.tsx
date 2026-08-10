"use client";

import Image from "next/image";
import Link from "next/link";

export function LandingPage() {
  return (
    <div className="relative min-h-[900px] w-full flex flex-col items-center justify-between p-2 sm:p-4 overflow-hidden bg-[#0D0F0F]">
      {/* Ambient background glows */}
      <div className="absolute top-[-100px] left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-[#D4AF37]/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-100px] right-[-100px] w-[500px] h-[500px] bg-[#F2CA50]/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Main Landing Container */}
      <div className="relative w-full max-w-6xl bg-[#121414] border border-[#4D4635]/40 rounded-[32px] p-6 sm:p-12 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.7)] z-10 my-6 flex flex-col gap-12 sm:gap-16">

        {/* 1. HERO SECTION */}
        <section className="flex flex-col items-center text-center gap-6 sm:gap-8 pt-4">

          {/* Logo Badge */}
          <div className="flex flex-col items-center gap-3">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-white p-3.5 flex items-center justify-center border-2 border-[#D4AF37] shadow-[0_0_30px_rgba(242,202,80,0.35)] hover:scale-105 transition-transform duration-300">
              <Image
                src="/Fiti_Logo.png"
                alt="FITI Logo"
                width={80}
                height={80}
                className="object-contain"
                priority
              />
            </div>
            <span className="px-4 py-1.5 rounded-full bg-[#1A1C1C] border border-[#D4AF37]/40 font-mono text-xs font-semibold uppercase tracking-[2.5px] text-[#F2CA50] shadow-sm">
              LUXURY BESPOKE SUITING PLATFORM
            </span>
          </div>

          {/* Hero Heading */}
          <div className="max-w-3xl flex flex-col gap-3">
            <h1 className="font-sans text-3xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#E2E2E2] leading-[1.1]">
              Haute Couture Meets <br className="hidden sm:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#F2CA50] via-[#D4AF37] to-[#F2CA50]">
                Precision 3D Fit
              </span>
            </h1>
            <p className="font-sans text-base sm:text-xl text-[#D0C5AF] max-w-2xl mx-auto leading-relaxed mt-2">
              Connect with world-class master tailors, record sub-millimeter 3D body scans, and order handcrafted bespoke suits tailored to your exact contours.
            </p>
          </div>

          {/* Primary Action Buttons Flow */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-md pt-2">
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 h-[56px] bg-[#F2CA50] hover:bg-[#e0b943] text-[#241A00] font-sans font-bold text-base uppercase tracking-[1.2px] rounded-xl flex items-center justify-center gap-3 transition-all btn-gold-shadow"
            >
              <span>SIGN IN TO PORTAL</span>
              <span className="text-lg">→</span>
            </Link>

            <Link
              href="/register"
              className="w-full sm:w-auto px-8 h-[56px] bg-[#1A1C1C] hover:bg-[#252828] text-[#F2CA50] border border-[#D4AF37]/50 font-sans font-semibold text-base uppercase tracking-[1.2px] rounded-xl flex items-center justify-center gap-2 transition-all hover:border-[#F2CA50]"
            >
              <span>CREATE ACCOUNT</span>
            </Link>
          </div>

          {/* Navigation Flow Guide */}
          <div className="flex items-center justify-center gap-2 font-mono text-[11px] text-[#99907C] pt-2">
            <span className="text-[#F2CA50]">USER FLOW:</span>
            <span>LANDING PAGE</span>
            <span>→</span>
            <span className="text-[#E2E2E2] underline">LOGIN</span>
            <span>→</span>
            <span>REGISTER (NEW USER)</span>
            <span>→</span>
            <span className="text-[#F2CA50]">HOME DASHBOARD</span>
          </div>
        </section>

        {/* 2. VALUE PROPOSITION & FEATURE CARDS */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-[#4D4635]/30">

          {/* Feature 1: 3D Scan */}
          <div className="glass-card-gold p-6 sm:p-8 flex flex-col justify-between gap-4 group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-[#333535] border border-[#4D4635] flex items-center justify-center text-[#F2CA50] mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <h3 className="font-sans text-xl font-bold text-[#E2E2E2] mb-2">
                3D Body Scanning
              </h3>
              <p className="font-sans text-xs sm:text-sm text-[#D0C5AF] leading-relaxed">
                Store sub-millimeter precision body measurements digitally. Your profile can be accessed instantly by authorized master tailors anywhere in the world.
              </p>
            </div>
            <div className="font-mono text-[11px] text-[#F2CA50] uppercase tracking-wider font-bold">
              SUB-MILLIMETER ACCURACY
            </div>
          </div>

          {/* Feature 2: OpenStreetMap Store Locator */}
          <div className="glass-card-gold p-6 sm:p-8 flex flex-col justify-between gap-4 group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-[#333535] border border-[#4D4635] flex items-center justify-center text-[#F2CA50] mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                </svg>
              </div>
              <h3 className="font-sans text-xl font-bold text-[#E2E2E2] mb-2">
                Atelier Store Locator
              </h3>
              <p className="font-sans text-xs sm:text-sm text-[#D0C5AF] leading-relaxed">
                Discover top-rated Savile Row and global tailoring ateliers using integrated OpenStreetMap location mapping with real-time appointment booking.
              </p>
            </div>
            <div className="font-mono text-[11px] text-[#F2CA50] uppercase tracking-wider font-bold">
              POWERED BY OPENSTREETMAP
            </div>
          </div>

          {/* Feature 3: Master Atelier Platform */}
          <div className="glass-card-seller p-6 sm:p-8 flex flex-col justify-between gap-4 group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-[#333535] border border-[#4D4635] flex items-center justify-center text-[#F2CA50] mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="font-sans text-xl font-bold text-[#E2E2E2] mb-2">
                Tailor & Atelier Hub
              </h3>
              <p className="font-sans text-xs sm:text-sm text-[#D0C5AF] leading-relaxed">
                Dedicated seller portal for ateliers to manage client queues, review 3D scan data, update order milestones, and showcase signature wool collections.
              </p>
            </div>
            <div className="font-mono text-[11px] text-[#F2CA50] uppercase tracking-wider font-bold">
              VERIFIED SELLER PORTAL
            </div>
          </div>

        </section>

        {/* 3. PLATFORM USER FLOW CARDS */}
        <section className="bg-[#1A1C1C] border border-[#4D4635]/50 rounded-2xl p-6 sm:p-10 flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
            <div>
              <span className="font-mono text-xs font-bold uppercase tracking-[1.4px] text-[#F2CA50]">
                AUTHENTICATION & ACCESS
              </span>
              <h2 className="font-sans text-2xl font-bold text-[#E2E2E2] mt-0.5">
                Ready to Experience FITI?
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Existing User Flow */}
            <div className="bg-[#0D0F0F] border border-[#4D4635] rounded-xl p-5 flex flex-col justify-between gap-4">
              <div>
                <span className="font-mono text-xs text-[#F2CA50] font-bold block uppercase">
                  EXISTING USERS
                </span>
                <h4 className="font-sans text-lg font-bold text-[#E2E2E2] mt-1">
                  Sign In to Dashboard
                </h4>
                <p className="font-sans text-xs text-[#D0C5AF] mt-1">
                  Access saved 3D body metrics, active suit order queues, or atelier dashboard.
                </p>
              </div>
              <Link
                href="/login"
                className="w-full h-11 bg-[#F2CA50] hover:bg-[#e0b943] text-[#241A00] font-sans font-bold text-xs uppercase tracking-[1px] rounded-lg flex items-center justify-center transition-all"
              >
                GO TO LOGIN →
              </Link>
            </div>

            {/* New User Flow */}
            <div className="bg-[#0D0F0F] border border-[#4D4635] rounded-xl p-5 flex flex-col justify-between gap-4">
              <div>
                <span className="font-mono text-xs text-[#F2CA50] font-bold block uppercase">
                  NEW USERS
                </span>
                <h4 className="font-sans text-lg font-bold text-[#E2E2E2] mt-1">
                  Create Client or Seller Account
                </h4>
                <p className="font-sans text-xs text-[#D0C5AF] mt-1">
                  Register as a bespoke client or list your tailoring atelier on the store locator.
                </p>
              </div>
              <Link
                href="/register"
                className="w-full h-11 bg-[#333535] hover:bg-[#4D4635] text-[#F2CA50] border border-[#F2CA50]/40 font-sans font-bold text-xs uppercase tracking-[1px] rounded-lg flex items-center justify-center transition-all"
              >
                REGISTER NEW ACCOUNT →
              </Link>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
