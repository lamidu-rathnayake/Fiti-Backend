"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

interface TopDemoBarProps {
  isMobileFrame?: boolean;
  onToggleFrame?: () => void;
}

export function TopDemoBar({ isMobileFrame = false, onToggleFrame }: TopDemoBarProps) {
  const pathname = usePathname();

  const pages = [
    { name: "1. Login", path: "/login" },
    { name: "2. Account Select", path: "/register" },
    { name: "3. Client Register", path: "/register/client" },
    { name: "4. Seller Register", path: "/register/seller" },
    { name: "5. Add Shop", path: "/register/seller/shop" },
    { name: "6. Seller Dashboard", path: "/seller/home" },
    { name: "7. Client Home", path: "/client/home" },
    { name: "8. Store Details", path: "/client/store/carnage" },
    { name: "9. Request Details", path: "/client/book/carnage" },
    { name: "10. Order Status", path: "/client/orders" },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#121414]/95 backdrop-blur-md border-b border-[#4D4635]/40 px-3 sm:px-6 py-2.5 shadow-lg">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-3">
        {/* Brand logo & title */}
        <Link href="/" className="flex items-center gap-3 group shrink-0">
          <div className="w-9 h-9 rounded-xl bg-white p-1 flex items-center justify-center border border-[#D4AF37] shadow-[0_0_15px_rgba(242,202,80,0.3)] group-hover:scale-105 transition-transform">
            <Image
              src="/Fiti_Logo.png"
              alt="FITI Logo"
              width={32}
              height={32}
              className="object-contain"
            />
          </div>
          <div>
            <span className="font-mono text-xs font-bold tracking-widest text-[#F2CA50] uppercase block leading-none">
              FITI PLATFORM
            </span>
            <span className="text-[10px] text-[#99907C] font-mono tracking-tight">
              Responsive Bespoke Suiting WebApp
            </span>
          </div>
        </Link>

        {/* Viewport Mode Switcher Toggle */}
        {onToggleFrame && (
          <button
            onClick={onToggleFrame}
            className="px-3.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-[#1A1C1C] border border-[#F2CA50]/50 text-[#F2CA50] hover:bg-[#F2CA50] hover:text-[#241A00] transition-all flex items-center gap-2 shadow-sm shrink-0"
          >
            <span>{isMobileFrame ? "📱 390px Mobile Frame Mode" : "🖥️ Native Desktop / Responsive Mode"}</span>
            <span className="text-[10px] opacity-75">(Toggle)</span>
          </button>
        )}

        {/* Screens Switcher */}
        <nav className="flex flex-wrap items-center justify-center gap-1 sm:gap-1.5">
          {pages.map((page) => {
            const isActive = pathname === page.path;
            return (
              <Link
                key={page.path}
                href={page.path}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium transition-all ${isActive
                    ? "bg-[#F2CA50] text-[#241A00] font-bold shadow-[0_2px_10px_rgba(242,202,80,0.3)] scale-105"
                    : "text-[#D0C5AF] hover:text-[#FFFFFF] hover:bg-[#333535]/50 border border-transparent hover:border-[#4D4635]/40"
                  }`}
              >
                {page.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
