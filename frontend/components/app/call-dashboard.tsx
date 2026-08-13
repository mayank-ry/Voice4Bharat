"use client";
import * as React from "react";
import { PhoneCall, CheckCircle2, XCircle } from "lucide-react";

export const CallDashboard = () => {
  const [stats, setStats] = React.useState({ total: 0, success: 0, failed: 0, recent: [] as any[] });

  const fetchStats = async () => {
    const res = await fetch("/api/call-stats");
    const data = await res.json();
    setStats(data);
  };

  React.useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // auto-refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const rate = stats.total > 0 ? Math.round((stats.success / stats.total) * 100) : 0;

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-12">
      <h2 className="mb-6 text-2xl font-bold text-slate-900">Call Analytics</h2>

      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
          <PhoneCall className="mx-auto mb-2 h-6 w-6 text-blue-700" />
          <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
          <p className="text-xs text-slate-500">Total Calls</p>
        </div>
        <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
          <CheckCircle2 className="mx-auto mb-2 h-6 w-6 text-emerald-600" />
          <p className="text-2xl font-bold text-slate-900">{stats.success}</p>
          <p className="text-xs text-slate-500">Successful</p>
        </div>
        <div className="rounded-2xl border bg-white p-5 text-center shadow-sm">
          <XCircle className="mx-auto mb-2 h-6 w-6 text-red-600" />
          <p className="text-2xl font-bold text-slate-900">{stats.failed}</p>
          <p className="text-xs text-slate-500">Failed</p>
        </div>
      </div>

      <p className="mb-4 text-sm text-slate-500">Success rate: <span className="font-semibold text-slate-900">{rate}%</span></p>

      <h3 className="mb-2 text-sm font-semibold text-slate-700">Recent Calls</h3>
      <div className="flex flex-col gap-2">
        {stats.recent.map((c: any) => (
          <div key={c.call_id} className="flex items-center justify-between rounded-xl border bg-white px-4 py-2 text-sm">
            <span className="text-slate-500">#{c.call_id} · {c.channel}</span>
            <span className={c.outcome === "success" ? "text-emerald-600" : "text-red-600"}>{c.outcome}</span>
          </div>
        ))}
      </div>
    </div>
  );
};