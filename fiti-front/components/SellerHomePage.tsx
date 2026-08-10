"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { listShopsBySeller, listOrdersByShop, ShopResponse, OrderResponse } from "@/lib/api";

const STATUS_BADGE: Record<string, string> = {
  PENDING: "badge-amber",
  CONFIRMED: "badge-blue",
  FABRIC_CUTTING: "badge-gold",
  STITCHING: "badge-gold",
  FIRST_FITTING: "badge-blue",
  FINAL_FITTING: "badge-blue",
  COMPLETED: "badge-green",
  CANCELLED: "badge-red",
};

export function SellerHomePage() {
  const { user } = useAuth();
  const [shops, setShops] = useState<ShopResponse[]>([]);
  const [activeShop, setActiveShop] = useState<ShopResponse | null>(null);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    listShopsBySeller(user.uid)
      .then((data: ShopResponse[]) => {
        setShops(data);
        if (data.length > 0) setActiveShop(data[0]);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [user]);

  useEffect(() => {
    if (!activeShop) return;
    listOrdersByShop(activeShop.shop_id)
      .then((data: OrderResponse[]) => setOrders(data))
      .catch(() => setOrders([]));
  }, [activeShop]);

  const shopName = activeShop?.shop_name || "My Atelier";

  return (
    <div className="page-wrapper">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <span className="eyebrow text-[var(--gold-300)] block mb-1">Master Tailor Dashboard</span>
          <h1 className="text-display-md font-bold text-[var(--text-primary)]">
            {shopName}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/register/seller/shop" className="btn-gold px-4 py-2 text-xs">
            + Add New Atelier Shop
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Active Orders", value: orders.length ? String(orders.length).padStart(2, "0") : "00" },
          { label: "Total Shops",  value: shops.length ? String(shops.length).padStart(2, "0") : "00" },
          { label: "Average Rating", value: activeShop ? `★ ${activeShop.average_rating.toFixed(1)}` : "5.0" },
          { label: "3D Scans",     value: "100% verified" },
        ].map((m, i) => (
          <motion.div key={m.label}
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.4 }}
            className="surface-card rounded-2xl p-5 flex flex-col justify-between gap-2"
          >
            <span className="stat-label">{m.label}</span>
            <span className="stat-number">{m.value}</span>
          </motion.div>
        ))}
      </div>

      {/* Orders table */}
      <div className="surface-card rounded-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-dim)]">
          <span className="eyebrow text-[var(--gold-300)]">Order Queue</span>
          {loading
            ? <span className="text-caption text-[var(--text-ghost)] font-mono animate-pulse">Loading…</span>
            : <span className="text-caption text-[var(--text-muted)] font-mono">{orders.length} orders</span>
          }
        </div>

        {orders.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[var(--border-dim)]">
                  {["Order ID", "Bid ID", "Status", "Price", "Started", "Completed"].map((h) => (
                    <th key={h} className="px-5 py-3 text-label text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {orders.map((order, i) => (
                  <motion.tr key={order.order_id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 + i * 0.05 }}
                    className="border-b border-[var(--border-dim)] hover:bg-[var(--bg-raised)] transition-colors"
                  >
                    <td className="px-5 py-4 font-mono text-xs font-bold text-[var(--gold-300)]">
                      #ORD-{order.order_id}
                    </td>
                    <td className="px-5 py-4 font-mono text-xs text-[var(--text-secondary)]">
                      #{order.bid_id}
                    </td>
                    <td className="px-5 py-4">
                      <span className={STATUS_BADGE[order.order_status] ?? "badge-amber"}>
                        {order.order_status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-5 py-4 font-mono text-sm font-bold text-[var(--text-primary)]">
                      £{order.accepted_price.toLocaleString()}
                    </td>
                    <td className="px-5 py-4 text-caption text-[var(--text-muted)] font-mono">
                      {order.started_date ?? "—"}
                    </td>
                    <td className="px-5 py-4 text-caption text-[var(--text-muted)] font-mono">
                      {order.completed_date ?? "—"}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : !loading ? (
          <div className="py-16 text-center text-[var(--text-ghost)] font-mono text-sm">
            No orders yet for {shopName}.
          </div>
        ) : (
          <div className="py-10 text-center text-caption text-[var(--text-ghost)] font-mono animate-pulse">
            Fetching orders…
          </div>
        )}
      </div>

    </div>
  );
}
