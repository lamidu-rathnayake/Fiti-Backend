"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { listOrdersByClient, OrderResponse } from "@/lib/api";

const STEPS = [
  { statusKey: "PENDING",        title: "3D Body Scan Measurement", desc: "Sub-millimeter mesh submitted & approved by Master Tailor" },
  { statusKey: "CONFIRMED",      title: "Order Confirmed",          desc: "Tailor accepted bid & schedule fitting slot" },
  { statusKey: "FABRIC_CUTTING", title: "Fabric Precision Cutting", desc: "Super 180s Wool cut at Savile Row Atelier" },
  { statusKey: "STITCHING",       title: "Bespoke Hand Assembly",    desc: "Silk lining & horn button hand craft" },
  { statusKey: "FIRST_FITTING",  title: "First Canvas Fitting",     desc: "Fitting session at Mayfair Atelier Studio" },
  { statusKey: "FINAL_FITTING",  title: "Final Garment Fitting",    desc: "Micro adjustments & final press" },
  { statusKey: "COMPLETED",      title: "Garment Handover",         desc: "Inspected & delivered to client" },
];

const ORDER_STATUS_INDEX: Record<string, number> = {
  PENDING: 0,
  CONFIRMED: 1,
  FABRIC_CUTTING: 2,
  STITCHING: 3,
  FIRST_FITTING: 4,
  FINAL_FITTING: 5,
  COMPLETED: 6,
};

export function OrderTrackingPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    listOrdersByClient(user.uid)
      .then((data) => { setOrders(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [user]);

  const activeOrder = orders[0];
  const currentStepIdx = activeOrder ? (ORDER_STATUS_INDEX[activeOrder.order_status] ?? 2) : 2;

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="page-header">
        <Link href="/client/home" className="back-btn">← Client Home</Link>
        <span className="eyebrow text-[var(--gold-300)]">Order Lifecycle & Production</span>
        <div className="w-8 h-8 rounded-xl bg-white p-1 border border-[var(--gold-400)] flex items-center justify-center">
          <Image src="/Fiti_Logo.png" alt="FITI" width={26} height={26} className="object-contain" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start max-w-5xl mx-auto w-full">

        {/* Left: Summary */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-5 glass-gold rounded-2xl p-6 flex flex-col gap-5"
        >
          <div>
            <span className="eyebrow text-[var(--gold-300)] block mb-1">
              Order #{activeOrder ? activeOrder.order_id : "ORD-9821"}
            </span>
            <h1 className="text-heading-lg font-bold text-[var(--text-primary)]">
              Two-Piece Bespoke Suit
            </h1>
            <p className="text-caption text-[var(--text-muted)] font-mono mt-1">
              Savile Row Atelier · London
            </p>
          </div>

          <div className="relative h-44 rounded-xl overflow-hidden border border-[var(--border-dim)]">
            <Image src="/teaser.png" alt="Crafting" fill className="object-cover" />
          </div>

          <div className="surface-card rounded-xl p-4 flex flex-col gap-2 font-mono text-caption">
            <div className="flex justify-between text-[var(--text-muted)]">
              <span>ESTIMATED FITTING</span>
              <span className="text-[var(--text-primary)] font-bold">Aug 28, 2026</span>
            </div>
            <div className="flex justify-between text-[var(--text-muted)]">
              <span>ACCEPTED BID</span>
              <span className="text-[var(--gold-300)] font-bold">
                £{activeOrder ? activeOrder.accepted_price.toLocaleString() : "2,450"}
              </span>
            </div>
            <div className="flex justify-between text-[var(--text-muted)]">
              <span>STATUS</span>
              <span className="text-[var(--status-green)] font-bold">
                {activeOrder ? activeOrder.order_status.replace(/_/g, " ") : "FABRIC CUTTING"}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Right: Milestone Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-7 surface-card rounded-2xl p-6 flex flex-col gap-6"
        >
          <div className="flex justify-between items-center pb-4 border-b border-[var(--border-dim)]">
            <h2 className="text-heading-sm font-bold text-[var(--text-primary)]">Production Milestones</h2>
            {loading && <span className="text-caption text-[var(--text-ghost)] font-mono animate-pulse">Syncing status…</span>}
          </div>

          <div className="flex flex-col gap-6 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-[var(--border-dim)]">
            {STEPS.map((step, i) => {
              const isDone = i < currentStepIdx;
              const isActive = i === currentStepIdx;

              return (
                <motion.div key={step.title}
                  initial={{ opacity: 0, x: 12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 + i * 0.06, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                  className="relative flex items-start gap-5"
                >
                  {isDone ? (
                    <div className="step-dot-done relative z-10">✓</div>
                  ) : isActive ? (
                    <div className="step-dot-active relative z-10">{i + 1}</div>
                  ) : (
                    <div className="step-dot-pending relative z-10">{i + 1}</div>
                  )}

                  <div className="flex-1 pb-1 pt-0.5">
                    <div className={`font-semibold text-sm mb-0.5 ${
                      isActive ? "text-[var(--gold-300)]" : isDone ? "text-[var(--text-primary)]" : "text-[var(--text-muted)]"
                    }`}>
                      {step.title}
                    </div>
                    <div className="text-caption text-[var(--text-muted)]">{step.desc}</div>
                    {isActive && (
                      <span className="inline-block mt-2 badge-amber">In Progress</span>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

      </div>
    </div>
  );
}
