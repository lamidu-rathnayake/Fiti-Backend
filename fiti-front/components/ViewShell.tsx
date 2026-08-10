"use client";

import { useState } from "react";
import { TopDemoBar } from "./TopDemoBar";

export function ViewShell({ children }: { children: React.ReactNode }) {
  const [frameMode, setFrameMode] = useState<"responsive" | "mobile390">("responsive");

  return (
    <div className="min-h-screen flex flex-col bg-[#080909] text-[#E2E2E2] selection:bg-[#F2CA50] selection:text-[#241A00]">
      {/* Navigation Header */}
      <TopDemoBar
        isMobileFrame={frameMode === "mobile390"}
        onToggleFrame={() =>
          setFrameMode(frameMode === "responsive" ? "mobile390" : "responsive")
        }
      />

      {/* Main Container */}
      <main className="flex-1 w-full flex flex-col items-center justify-center p-3 sm:p-6 lg:p-8">
        {frameMode === "mobile390" ? (
          /* Simulated 390px Mobile Phone Frame */
          <div className="relative w-[390px] max-w-[96vw] min-h-[844px] bg-[#121414] border-2 border-[#D4AF37]/50 rounded-[36px] shadow-[0_0_50px_rgba(0,0,0,0.9),0_0_20px_rgba(242,202,80,0.15)] flex flex-col overflow-hidden my-4">
            {/* Phone Speaker Notch */}
            <div className="w-full h-8 bg-[#0D0F0F] flex items-center justify-between px-6 shrink-0 border-b border-[#4D4635]/30">
              <span className="font-mono text-[11px] font-bold text-[#F2CA50]">9:41</span>
              <div className="w-24 h-4 bg-[#1A1C1C] rounded-full flex items-center justify-center border border-[#4D4635]/50">
                <div className="w-3 h-3 rounded-full bg-[#0D0F0F] border border-[#4D4635]" />
              </div>
              <div className="flex items-center gap-1.5 text-[#F2CA50]">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 3c-4.97 0-9 4.03-9 9 0 2.12.74 4.07 1.97 5.61L4.35 19.4c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0l1.9-1.9C9.2 19.53 10.55 20 12 20c4.97 0 9-4.03 9-9s-4.03-9-9-9zm0 15c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z" />
                </svg>
                <div className="w-4 h-2 border border-[#F2CA50] rounded-sm p-0.5">
                  <div className="w-full h-full bg-[#F2CA50]" />
                </div>
              </div>
            </div>

            {/* Content inside phone */}
            <div className="flex-1 w-full overflow-y-auto custom-scrollbar flex flex-col">
              {children}
            </div>

            {/* Bottom Home Line */}
            <div className="w-full py-2 bg-[#0D0F0F] flex justify-center items-center shrink-0 border-t border-[#4D4635]/20">
              <div className="w-32 h-1 bg-[#4D4635] rounded-full" />
            </div>
          </div>
        ) : (
          /* Natively Responsive View (Desktop Multi-Column / Mobile Stacked) */
          <div className="w-full max-w-7xl mx-auto flex flex-col justify-center my-auto">
            {children}
          </div>
        )}
      </main>

      {/* Global Footer */}
      <footer className="border-t border-[#4D4635]/20 py-4 px-6 text-center font-mono text-[11px] text-[#99907C]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 FITI Bespoke Suiting Platform</span>
          <span className="text-[#D4AF37]/80 font-semibold">
            Fluid Responsive Desktop & Mobile Architecture
          </span>
        </div>
      </footer>
    </div>
  );
}
