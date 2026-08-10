"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";
import { createClothingRequest } from "@/lib/api";

interface Props {
  shopId?: number;
}

export function RequestDetailsPage({ shopId }: Props) {
  const router = useRouter();
  const { user } = useAuth();
  const [date, setDate] = useState("2026-08-18");
  const [category, setCategory] = useState("Two-Piece Bespoke Suit");
  const [budget, setBudget] = useState("2500");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createClothingRequest({
        client_id: user?.uid ?? "mock_firebase_uid",
        clothing_category: category,
        target_budget: parseFloat(budget) || 2500,
        target_date: date,
        description: notes,
        target_shop_ids: shopId ? [shopId] : undefined,
        service_type: "online",
      });
      router.push("/client/orders");
    } catch (err: any) {
      setError(err.message || "Failed to submit request.");
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="page-header">
        <Link href={shopId ? `/client/store/${shopId}` : "/client/home"} className="back-btn">← Atelier</Link>
        <span className="eyebrow text-[var(--text-muted)]">Fitting Appointment</span>
        <div className="w-8 h-8 rounded-xl bg-white p-1 border border-[var(--gold-400)] flex items-center justify-center">
          <Image src="/Fiti_Logo.png" alt="FITI" width={26} height={26} className="object-contain" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start max-w-4xl mx-auto w-full">

        {/* Left: Summary */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="md:col-span-5 glass-gold rounded-2xl p-6 flex flex-col gap-5"
        >
          <div>
            <span className="eyebrow text-[var(--text-muted)] block mb-1">Selected atelier</span>
            <h2 className="text-heading-lg font-bold text-[var(--text-primary)]">Hercules Tailors</h2>
            <p className="text-caption text-[var(--text-muted)] font-mono mt-1">14 Savile Row · Mayfair · London</p>
          </div>

          <div className="surface-card rounded-xl p-4">
            <span className="eyebrow text-[var(--status-green)] block mb-2">✦ 3D Body Scan Synced</span>
            <p className="text-sm text-[var(--text-primary)] font-semibold">{user?.displayName ?? "Client Profile"}</p>
            <p className="text-caption text-[var(--text-muted)] font-mono">UID: {user?.uid}</p>
          </div>

          <div className="divider-subtle" />

          <div className="text-caption text-[var(--text-muted)] font-mono leading-relaxed">
            Your 3D body scan measurements will be transmitted to the tailor at confirmation.
            No physical measuring session required.
          </div>
        </motion.div>

        {/* Right: Booking form */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="md:col-span-7 glass-gold rounded-2xl p-6 flex flex-col gap-5"
        >
          <div>
            <h1 className="text-heading-lg font-bold text-[var(--text-primary)]">Schedule Fitting</h1>
            <p className="text-body text-[var(--text-secondary)] mt-1">Choose your preferred date, budget, and preferences</p>
          </div>

          {error && (
            <div className="px-4 py-3 rounded-xl bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)] text-sm text-red-400 font-mono">
              ⚠ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="input-label">Garment Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="select-field">
                <option>Two-Piece Bespoke Suit</option>
                <option>Three-Piece Tuxedo</option>
                <option>Double-Breasted Blazer</option>
                <option>Overcoat & Outerwear</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="input-label">Target Date</label>
                <input type="date" required value={date} onChange={(e) => setDate(e.target.value)} className="input-field" />
              </div>
              <div>
                <label className="input-label">Budget (£)</label>
                <input type="number" required value={budget} onChange={(e) => setBudget(e.target.value)} className="input-field" />
              </div>
            </div>

            <div>
              <label className="input-label">Bespoke preferences & notes</label>
              <textarea
                rows={4} value={notes} onChange={(e) => setNotes(e.target.value)}
                placeholder="Prefer Italian peak lapel with full silk lining, hand-stitched buttonholes…"
                className="textarea-field"
              />
            </div>

            <button type="submit" disabled={loading} className="btn-gold w-full py-4 mt-2">
              {loading ? "Submitting request…" : "Confirm & Submit Request →"}
            </button>
          </form>
        </motion.div>

      </div>
    </div>
  );
}
