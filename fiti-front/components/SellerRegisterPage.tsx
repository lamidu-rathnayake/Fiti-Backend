"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";
import { registerSeller } from "@/lib/api";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { auth } from "@/lib/firebase";

export function SellerRegisterPage() {
  const router = useRouter();
  const { setRole } = useAuth();
  const [form, setForm] = useState({ 
    email: "", password: "",
    firstName: "", lastName: "", address: "", city: "", phone: "", bio: "" 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, form.email, form.password);
      await updateProfile(userCredential.user, { displayName: `${form.firstName} ${form.lastName}` });

      await registerSeller({ id: userCredential.user.uid });
      setRole("seller");
      router.push("/register/seller/shop");
    } catch (err: any) {
      if (err?.message?.includes("409") || err?.message?.includes("already exists")) {
        setRole("seller");
        router.push("/register/seller/shop");
      } else {
        setError(err.message || "Registration failed. Please try again.");
        setLoading(false);
      }
    }
  };

  return (
    <div className="page-wrapper min-h-[calc(100vh-4rem)] flex items-center justify-center">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,rgba(212,175,55,0.08)_0%,transparent_70%)] pointer-events-none" />

      <div className="relative z-10 w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">

        {/* Left: Feature panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-4 glass-gold rounded-3xl p-8 flex flex-col justify-between gap-8"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-white p-1.5 border border-[var(--gold-400)] flex items-center justify-center">
              <Image src="/Fiti_Logo.png" alt="FITI" width={28} height={28} className="object-contain" />
            </div>
            <span className="eyebrow text-[var(--gold-300)]">Step 1 of 2</span>
          </div>
          <div>
            <span className="eyebrow text-[var(--text-muted)] block mb-2">Master Tailor Portal</span>
            <h2 className="text-heading-lg font-bold text-[var(--text-primary)] leading-tight mb-3">
              Join Savile Row's<br/>
              <span className="font-serif-display text-[var(--gold-300)]">Digital Network.</span>
            </h2>
            <p className="text-body text-[var(--text-secondary)] leading-relaxed">
              Connect with discerning clients and scale your bespoke operations globally.
            </p>
          </div>
          <div className="flex flex-col gap-2">
            {["Receive sub-mm 3D scans", "Bid on bespoke requests", "Manage digital atelier"].map(f => (
              <div key={f} className="flex items-center gap-2 text-caption text-[var(--text-secondary)] font-mono">
                <span className="text-[var(--gold-300)]">✦</span> {f}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right: Form */}
        <motion.div
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="lg:col-span-8 glass-gold rounded-3xl p-8 flex flex-col gap-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-heading-lg font-bold text-[var(--text-primary)]">Personal Details</h1>
              <p className="text-body text-[var(--text-secondary)] mt-1">First, tell us about the master tailor behind the craft.</p>
            </div>
            <Link href="/register" className="back-btn">← Back</Link>
          </div>

          {error && (
            <div className="px-4 py-3 rounded-xl bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)] text-sm text-red-400 font-mono">
              ⚠ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div><label className="input-label">Email</label><input type="email" required value={form.email} onChange={set("email")} placeholder="atelier@savilerow.com" className="input-field" /></div>
              <div><label className="input-label">Password</label><input type="password" required value={form.password} onChange={set("password")} placeholder="••••••••" className="input-field" /></div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div><label className="input-label">First Name</label><input type="text" required value={form.firstName} onChange={set("firstName")} placeholder="Master" className="input-field" /></div>
              <div><label className="input-label">Last Name</label><input type="text" required value={form.lastName} onChange={set("lastName")} placeholder="Tailor" className="input-field" /></div>
            </div>
            <div><label className="input-label">Residential Address (For Verification)</label><input type="text" required value={form.address} onChange={set("address")} placeholder="12 Savile Row" className="input-field" /></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div><label className="input-label">City</label><input type="text" required value={form.city} onChange={set("city")} placeholder="London" className="input-field" /></div>
              <div>
                <label className="input-label">Direct Contact</label>
                <div className="flex gap-2">
                  <span className="input-field w-16 flex items-center justify-center font-mono text-xs text-[var(--gold-300)] shrink-0">+44</span>
                  <input type="tel" required value={form.phone} onChange={set("phone")} placeholder="7911 123456" className="input-field flex-1" />
                </div>
              </div>
            </div>
            <div><label className="input-label">Brief Bio (Optional)</label><textarea value={form.bio} onChange={set("bio")} placeholder="Years of experience, specialties..." className="input-field min-h-[80px] py-3" /></div>
            
            <button type="submit" disabled={loading} className="btn-gold w-full py-4 mt-2">
              {loading ? "Registering..." : "Continue to Shop Details →"}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
