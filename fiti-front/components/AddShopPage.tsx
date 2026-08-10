"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";
import { createShop } from "@/lib/api";

export function AddShopPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [form, setForm] = useState({ shopName: "", specialty: "Bespoke Suiting Specialist", address: "", city: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createShop({
        seller_id: user?.uid ?? "mock_firebase_uid",
        shop_name: form.shopName,
        shop_bio: form.specialty,
        shop_address: form.address,
        city: form.city,
      });
      router.push("/seller/home");
    } catch (err: any) {
      setError(err.message || "Failed to create shop. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper min-h-[calc(100vh-4rem)] flex items-center justify-center">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(212,175,55,0.08)_0%,transparent_70%)] pointer-events-none" />

      <div className="relative z-10 w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

        {/* Left: feature panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-4 glass-gold rounded-3xl p-8 flex flex-col justify-between gap-8"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-white p-1.5 border border-[var(--gold-400)] flex items-center justify-center">
              <Image src="/Fiti_Logo.png" alt="FITI" width={28} height={28} className="object-contain" />
            </div>
            <span className="eyebrow text-[var(--gold-300)]">Step 2 of 2</span>
          </div>
          <div>
            <span className="eyebrow text-[var(--text-muted)] block mb-2">Atelier Studio Locator</span>
            <h2 className="text-heading-lg font-bold text-[var(--text-primary)] leading-tight mb-3">
              Feature Your Studio<br/>
              <span className="font-serif-display text-[var(--gold-300)]">on the Map.</span>
            </h2>
            <p className="text-body text-[var(--text-secondary)] leading-relaxed">
              Your studio location will appear in the client-facing interactive store discovery map.
            </p>
          </div>
          <div className="flex flex-col gap-2">
            {["OpenStreetMap listing", "Client appointment booking", "Verified atelier badge"].map(f => (
              <div key={f} className="flex items-center gap-2 text-caption text-[var(--text-secondary)] font-mono">
                <span className="text-[var(--gold-300)]">✦</span> {f}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right: form */}
        <motion.div
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-8 glass-gold rounded-3xl p-8 flex flex-col gap-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-heading-lg font-bold text-[var(--text-primary)]">Add Your Shop</h1>
              <p className="text-body text-[var(--text-secondary)] mt-1">Showcase your studio and specialty services</p>
            </div>
            <Link href="/register/seller" className="back-btn">← Back</Link>
          </div>

          {error && (
            <div className="px-4 py-3 rounded-xl bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)] text-sm text-red-400 font-mono">
              ⚠ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="input-label">Shop / Atelier Name</label>
              <input type="text" required value={form.shopName} onChange={set("shopName")} placeholder="CARNAGE TAILORS MAYFAIR" className="input-field" />
            </div>
            <div>
              <label className="input-label">Specialty Category</label>
              <select value={form.specialty} onChange={set("specialty")} className="select-field">
                <option>Bespoke Suiting Specialist</option>
                <option>Classic Savile Row Tailoring</option>
                <option>Made-To-Measure Tuxedos</option>
                <option>Contemporary Italian Cut</option>
              </select>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div><label className="input-label">Studio Address</label><input type="text" required value={form.address} onChange={set("address")} placeholder="14 Savile Row" className="input-field" /></div>
              <div><label className="input-label">City</label><input type="text" required value={form.city} onChange={set("city")} placeholder="London" className="input-field" /></div>
            </div>
            <button type="submit" disabled={loading} className="btn-gold w-full py-4 mt-2">
              {loading ? "Saving atelier…" : "Submit & Go to Dashboard →"}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
