"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { listNearbyShops, listOrdersByClient, ShopResponse, OrderResponse } from "@/lib/api";

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.45, ease: "easeOut" as const },
  }),
};

export function ClientHomePage() {
  const { user } = useAuth();
  const [region, setRegion] = useState<"London" | "Colombo">("London");
  const [shops, setShops] = useState<ShopResponse[]>([]);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const coords =
    region === "London"
      ? { lat: 51.5118, lon: -0.1415 }
      : { lat: 6.9271, lon: 79.8612 };

  useEffect(() => {
    setLoading(true);
    listNearbyShops(coords.lat, coords.lon, 20)
      .then((data: ShopResponse[]) => { setShops(data); setLoading(false); })
      .catch(() => { setShops([]); setLoading(false); });
  }, [region, coords.lat, coords.lon]);

  useEffect(() => {
    if (!user) return;
    listOrdersByClient(user.uid)
      .then((data: OrderResponse[]) => setOrders(data))
      .catch(() => setOrders([]));
  }, [user]);

  const activeOrder = orders[0];
  const mapSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${coords.lon - 0.02}%2C${coords.lat - 0.02}%2C${coords.lon + 0.02}%2C${coords.lat + 0.02}&amp;layer=mapnik&amp;marker=${coords.lat}%2C${coords.lon}`;

  return (
    <div className="page-wrapper">
      {/* Welcome header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <span className="eyebrow text-[var(--gold-300)] block mb-1">Exclusive Client Portal</span>
          <h1 className="text-display-md font-bold text-[var(--text-primary)]">
            Welcome, <span className="font-serif-display text-[var(--gold-300)]">{user?.displayName || "Gentleman"}</span>
          </h1>
        </div>

        {/* Region Switcher */}
        <div className="flex items-center gap-1 glass-gold rounded-xl p-1 font-mono text-xs">
          {(["London", "Colombo"] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRegion(r)}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                region === r
                  ? "bg-[var(--gold-400)] text-[var(--bg-black)] font-bold shadow-sm"
                  : "text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              }`}
            >
              {r === "London" ? "🇬🇧 London" : "🇱🇰 Colombo"}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT column */}
        <div className="lg:col-span-7 flex flex-col gap-6">

          {/* Quick stats row */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Active Orders", value: orders.length ? String(orders.length).padStart(2, "0") : "00" },
              { label: "3D Scans",     value: "01" },
              { label: "Ateliers Near",value: shops.length ? String(shops.length).padStart(2, "0") : "--" },
            ].map((stat, i) => (
              <motion.div key={stat.label} custom={i} variants={fadeUp} initial="hidden" animate="show"
                className="surface-card rounded-2xl p-4 text-center"
              >
                <div className="stat-number">{stat.value}</div>
                <div className="stat-label mt-1">{stat.label}</div>
              </motion.div>
            ))}
          </div>

          {/* Active order card */}
          {activeOrder ? (
            <motion.div custom={1} variants={fadeUp} initial="hidden" animate="show"
              className="glass-gold rounded-2xl p-6 flex flex-col gap-4"
            >
              <div className="flex justify-between items-center">
                <span className="eyebrow text-[var(--gold-300)]">Active Order #${activeOrder.order_id}</span>
                <span className="badge-amber">{activeOrder.order_status.replace(/_/g, " ")}</span>
              </div>

              <div className="progress-track">
                <div className="progress-fill" style={{ width: "60%" }} />
              </div>

              <div className="flex justify-between font-mono text-caption text-[var(--text-muted)]">
                <span>Accepted Price: £{activeOrder.accepted_price}</span>
                <Link href="/client/orders" className="text-[var(--gold-300)] hover:underline">
                  Track Timeline →
                </Link>
              </div>
            </motion.div>
          ) : (
            <motion.div custom={1} variants={fadeUp} initial="hidden" animate="show"
              className="surface-card rounded-2xl p-6 text-center"
            >
              <p className="text-body text-[var(--text-muted)]">No active orders yet.</p>
              <Link href="/client/store/1" className="btn-gold inline-block mt-3 px-5 py-2.5 text-sm">
                Browse Tailors →
              </Link>
            </motion.div>
          )}

          {/* 3D Scan engine card */}
          <motion.div custom={2} variants={fadeUp} initial="hidden" animate="show"
            className="relative rounded-2xl overflow-hidden h-44 border border-[var(--border-dim)] group"
          >
            <Image src="/Fiti_Logo.png" alt="3D Scan" fill className="object-contain p-10 opacity-10 scale-150" />
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--bg-card)] via-[var(--bg-card)]/70 to-transparent p-6 flex flex-col justify-center">
              <span className="eyebrow text-[var(--gold-300)] mb-2">3D precision scan engine</span>
              <h3 className="text-heading-md font-bold text-[var(--text-primary)]">Sub-Millimeter Body Contour Scan</h3>
              <p className="text-caption text-[var(--text-secondary)] mt-1">
                UID: {user?.uid} · Ready for Savile Row master tailors
              </p>
            </div>
          </motion.div>
        </div>

        {/* RIGHT column */}
        <div className="lg:col-span-5 flex flex-col gap-5">

          {/* Map card */}
          <div className="surface-card rounded-2xl overflow-hidden flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-dim)]">
              <span className="eyebrow text-[var(--gold-300)]">Store Locator</span>
              <span className="text-caption text-[var(--text-muted)] font-mono">{region}</span>
            </div>
            <div className="map-wrapper h-52">
              <iframe
                title="OpenStreetMap Atelier Locator"
                width="100%" height="100%"
                frameBorder="0" scrolling="no"
                src={mapSrc}
                className="w-full h-full"
              />
            </div>
            <div className="px-4 py-2 border-t border-[var(--border-dim)] text-center">
              <a href="https://www.openstreetmap.org" target="_blank" rel="noreferrer"
                className="text-caption text-[var(--gold-300)] hover:underline font-mono"
              >
                View on OpenStreetMap ↗
              </a>
            </div>
          </div>

          {/* Nearby stores list from backend */}
          <div className="surface-card rounded-2xl p-5 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="eyebrow text-[var(--gold-300)]">Nearby Ateliers</span>
              {loading && <span className="text-caption text-[var(--text-ghost)] font-mono animate-pulse">Loading…</span>}
            </div>

            {shops.length > 0 ? (
              shops.slice(0, 4).map((shop, i) => (
                <motion.div key={shop.shop_id} custom={i} variants={fadeUp} initial="hidden" animate="show"
                  className="store-card p-4 flex items-center justify-between gap-3"
                >
                  <div>
                    <div className="font-semibold text-sm text-[var(--text-primary)]">{shop.shop_name}</div>
                    <div className="text-caption text-[var(--text-muted)] font-mono mt-0.5">
                      ★ {shop.average_rating.toFixed(1)}
                      {shop.city ? ` · ${shop.city}` : ""}
                      {shop.shop_address ? ` · ${shop.shop_address}` : ""}
                    </div>
                  </div>
                  <Link href={`/client/store/${shop.shop_id}`} className="btn-gold px-3 py-2 text-xs shrink-0">
                    Book
                  </Link>
                </motion.div>
              ))
            ) : !loading ? (
              <p className="text-caption text-[var(--text-ghost)] font-mono py-4 text-center">
                No shops in {region} yet.
              </p>
            ) : (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="store-card p-4 h-14 animate-pulse" />
              ))
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
