"use client";

import Image from "next/image";
import Link from "next/link";

export function RegisterSelectionPage() {
  return (
    <div className="relative w-full max-w-5xl mx-auto bg-[#121414] border border-[#4D4635]/40 rounded-3xl p-6 sm:p-10 shadow-2xl my-4 flex flex-col items-center justify-between overflow-hidden">
      {/* Ambient background lighting */}
      <div className="absolute top-10 right-10 w-96 h-96 bg-[#D4AF37]/15 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-96 h-96 bg-[#F2CA50]/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Top Header */}
      <div className="w-full flex items-center justify-between pb-6 border-b border-[#4D4635]/30">
        <Link
          href="/login"
          className="px-3.5 py-1.5 bg-[#0D0F0F] hover:bg-[#1A1C1C] border border-[#4D4635] rounded-xl text-xs font-mono text-[#D0C5AF] hover:text-[#F2CA50] transition-colors flex items-center gap-1.5"
        >
          ← Back to Login
        </Link>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-white p-1 flex items-center justify-center border border-[#D4AF37]">
            <Image src="/Fiti_Logo.png" alt="FITI Logo" width={28} height={28} className="object-contain" />
          </div>
          <span className="font-mono text-xs font-bold text-[#F2CA50] uppercase tracking-wider">
            ACCOUNT SELECTION
          </span>
        </div>
      </div>

      {/* Title & Subtitle */}
      <div className="text-center my-6 max-w-xl">
        <h1 className="font-sans text-3xl font-bold text-[#E2E2E2]">
          Account Type
        </h1>
        <p className="font-sans text-xs sm:text-sm text-[#D0C5AF] mt-2">
          Choose how you wish to experience the FITI bespoke suiting platform
        </p>
      </div>

      {/* 2-Column Side-by-Side Cards (Figma Desktop Layout 5) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl my-4">

        {/* Card 1: Client Registration */}
        <Link
          href="/register/client"
          className="bg-[#0D0F0F] border border-[#4D4635]/60 hover:border-[#F2CA50] rounded-3xl p-8 flex flex-col justify-between items-center text-center gap-6 group transition-all hover:scale-[1.02] shadow-lg"
        >
          <div className="w-16 h-16 rounded-2xl bg-[#1A1C1C] border border-[#D4AF37]/50 flex items-center justify-center text-2xl text-[#F2CA50] group-hover:scale-110 transition-transform">
            👤
          </div>
          <div>
            <h2 className="font-sans text-xl font-bold text-[#E2E2E2] group-hover:text-[#F2CA50] transition-colors">
              Register as a Client
            </h2>
            <p className="font-sans text-xs text-[#D0C5AF] mt-2 leading-relaxed">
              Order handcrafted custom suits, access sub-millimeter 3D body scans, and discover nearby Savile Row tailors.
            </p>
          </div>
          <span className="w-full py-3 bg-[#1A1C1C] group-hover:bg-[#F2CA50] text-[#F2CA50] group-hover:text-[#241A00] font-sans font-bold text-xs uppercase tracking-wider rounded-xl transition-all border border-[#4D4635]">
            Register as Client →
          </span>
        </Link>

        {/* Card 2: Seller Registration */}
        <Link
          href="/register/seller"
          className="bg-[#0D0F0F] border border-[#4D4635]/60 hover:border-[#F2CA50] rounded-3xl p-8 flex flex-col justify-between items-center text-center gap-6 group transition-all hover:scale-[1.02] shadow-lg"
        >
          <div className="w-16 h-16 rounded-2xl bg-[#1A1C1C] border border-[#D4AF37]/50 flex items-center justify-center text-2xl text-[#F2CA50] group-hover:scale-110 transition-transform">
            ✂️
          </div>
          <div>
            <h2 className="font-sans text-xl font-bold text-[#E2E2E2] group-hover:text-[#F2CA50] transition-colors">
              Register as a Seller
            </h2>
            <p className="font-sans text-xs text-[#D0C5AF] mt-2 leading-relaxed">
              Showcase your atelier studio, manage suit order queues, and receive client 3D body scan measurements.
            </p>
          </div>
          <span className="w-full py-3 bg-[#1A1C1C] group-hover:bg-[#F2CA50] text-[#F2CA50] group-hover:text-[#241A00] font-sans font-bold text-xs uppercase tracking-wider rounded-xl transition-all border border-[#4D4635]">
            Register as Seller →
          </span>
        </Link>

      </div>
    </div>
  );
}
