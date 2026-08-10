"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { getShop, ShopResponse } from "@/lib/api";

interface Props {
  shopId: string;
}

export function StoreDetailPage({ shopId }: Props) {
  const [shop, setShop] = useState<ShopResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = parseInt(shopId, 10) || 1;
    setLoading(true);
    getShop(id)
      .then((data: ShopResponse) => { setShop(data); setLoading(false); })
      .catch((err: Error) => { setError(err.message || "Failed to load shop"); setLoading(false); });
  }, [shopId]);

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="page-header">
        <Link href="/client/home" className="back-btn">← Back to Tailors</Link>
        <span className="eyebrow text-[var(--text-muted)]">Savile Row Master Atelier</span>
        <div className="w-8 h-8 rounded-xl bg-white p-1 border border-[var(--gold-400)] flex items-center justify-center">
          <Image src="/Fiti_Logo.png" alt="FITI" width={26} height={26} className="object-contain" />
        </div>
      </div>

      {loading && (
        <div className="p-12 text-center text-sm font-mono text-[var(--gold-300)] animate-pulse">
          Loading atelier details…
        </div>
      )}

      {error && (
        <div className="glass-gold rounded-2xl p-6 max-w-xl mx-auto text-center">
          <p className="text-red-400 font-mono text-sm mb-4">⚠ {error}</p>
          <Link href="/client/home" className="btn-gold py-2 px-4 text-xs inline-block">Return to Tailor Discovery</Link>
        </div>
      )}

      {shop && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start max-w-5xl mx-auto w-full">

          {/* Left Column: Image banner */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="lg:col-span-5 flex flex-col gap-5"
          >
            <div className="relative w-full h-[320px] rounded-2xl overflow-hidden border border-[var(--gold-400)] shadow-xl">
              <Image src="/teaser.png" alt={shop.shop_name} fill className="object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-black)] via-transparent to-transparent p-4 flex items-end">
                <span className="eyebrow text-[var(--gold-300)]">ESTABLISHED SAVILE ROW ATELIER</span>
              </div>
            </div>

            <div className="glass-gold rounded-2xl p-5 flex flex-col gap-2">
              <span className="eyebrow text-[var(--gold-300)]">Craftsmanship & Bio</span>
              <p className="text-body text-[var(--text-secondary)] leading-relaxed">
                {shop.shop_bio || "Renowned for structured silhouettes, hand-padded lapels, and exclusive superfine wool fabric selections."}
              </p>
            </div>
          </motion.div>

          {/* Right Column: Title, Details & CTA */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="lg:col-span-7 flex flex-col gap-5"
          >
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <h1 className="text-display-md font-bold text-[var(--text-primary)]">{shop.shop_name}</h1>
                <p className="text-body text-[var(--text-muted)] mt-1 font-mono">
                  {[shop.shop_address, shop.city].filter(Boolean).join(" · ")}
                </p>
              </div>
              <div className="badge-gold shrink-0">★ {shop.average_rating.toFixed(1)}</div>
            </div>

            {/* Contact info */}
            <div className="surface-card rounded-xl p-4 flex flex-col gap-2">
              <span className="eyebrow text-[var(--text-muted)]">Contact</span>
              {shop.contact_number && (
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)] font-mono">
                  <span className="text-[var(--gold-300)]">📞</span> {shop.contact_number}
                </div>
              )}
              {shop.registration_number && (
                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)] font-mono">
                  <span className="text-[var(--gold-300)]">🏢</span> Reg: {shop.registration_number}
                </div>
              )}
              {shop.latitude && shop.longitude && (
                <a
                  href={`https://www.openstreetmap.org/?mlat=${shop.latitude}&mlon=${shop.longitude}&zoom=16`}
                  target="_blank" rel="noreferrer"
                  className="text-caption text-[var(--gold-300)] hover:underline font-mono mt-1"
                >
                  View on OpenStreetMap ↗
                </a>
              )}
            </div>

            {/* Book CTA */}
            <Link
              href={`/client/book/${shopId}`}
              className="btn-gold w-full py-4 mt-2 text-sm text-center"
            >
              Book Fitting Appointment →
            </Link>
          </motion.div>

        </div>
      )}
    </div>
  );
}
