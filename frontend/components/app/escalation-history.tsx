"use client";
import * as React from "react";
import { motion, AnimatePresence } from "motion/react";
import { AlertTriangle, ShieldAlert, HelpCircle, Globe, PhoneCall, Clock3, RefreshCw } from "lucide-react";

type Escalation = {
  id: number;
  user_id: string;
  reason: string;
  summary: string;
  urgency: string;
  language: string;
  follow_up: string;
  status: string;
  created_at: string;
};

const URGENCY_STYLES: Record<string, { border: string; badge: string; icon: string }> = {
  emergency: { border: "border-l-red-600", badge: "bg-red-100 text-red-700", icon: "bg-red-100 text-red-600" },
  high: { border: "border-l-orange-500", badge: "bg-orange-100 text-orange-700", icon: "bg-orange-100 text-orange-600" },
  medium: { border: "border-l-amber-400", badge: "bg-amber-100 text-amber-700", icon: "bg-amber-100 text-amber-600" },
  low: { border: "border-l-slate-300", badge: "bg-slate-100 text-slate-600", icon: "bg-slate-100 text-slate-500" },
};

const STATUS_STYLES: Record<string, string> = {
  open: "bg-red-50 text-red-600 border border-red-200",
  responded: "bg-blue-50 text-blue-600 border border-blue-200",
  solved: "bg-emerald-50 text-emerald-600 border border-emerald-200",
};

const REASON_LABEL: Record<string, string> = {
  emergency_safety: "Emergency / Safety Concern",
  agent_uncertain: "Needs Expert Confirmation",
};

export const EscalationHistory = () => {
  const [escalations, setEscalations] = React.useState<Escalation[]>([]);
  const [loading, setLoading] = React.useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/escalations");
      const data = await res.json();
      setEscalations(data.escalations || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  React.useEffect(() => {
    fetchData();
  }, []);

  const updateStatus = async (id: number, status: string) => {
    setEscalations((prev) => prev.map((e) => (e.id === id ? { ...e, status } : e)));
    await fetch(`/api/escalations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
  };

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold text-slate-900">
            <ShieldAlert className="h-6 w-6 text-amber-600" />
            Escalation History
          </h2>
          <p className="mt-1 text-sm text-slate-500">Human help requests raised by NyaAI callers</p>
        </div>
        <button
          onClick={fetchData}
          className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 transition-transform hover:rotate-90 hover:text-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {loading && <p className="text-sm text-slate-500">Loading escalations...</p>}
      {!loading && escalations.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-200 bg-white py-16 text-center text-sm text-slate-400">
          No escalations yet. NyaAI will list requests here when a caller needs human help.
        </div>
      )}

      <div className="flex flex-col gap-4">
        <AnimatePresence initial={false}>
          {escalations.map((e) => {
            const urgencyStyle = URGENCY_STYLES[e.urgency] || URGENCY_STYLES.low;
            return (
              <motion.div
                key={e.id}
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className={`overflow-hidden rounded-2xl border border-l-4 bg-white shadow-sm ${urgencyStyle.border}`}
              >
                <div className="flex gap-4 p-5">
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${urgencyStyle.icon}`}>
                    {e.reason === "emergency_safety" ? <AlertTriangle className="h-5 w-5" /> : <HelpCircle className="h-5 w-5" />}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-mono font-semibold text-slate-500">
                          ESC-{e.id}
                        </span>
                        <span className="ml-2 text-sm font-semibold text-slate-900">
                          {REASON_LABEL[e.reason] || e.reason}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium uppercase ${urgencyStyle.badge}`}>
                          {e.urgency}
                        </span>
                        <motion.span
                          key={e.status}
                          initial={{ scale: 0.8, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className={`rounded-full px-2.5 py-0.5 text-xs font-medium uppercase ${STATUS_STYLES[e.status] || ""}`}
                        >
                          {e.status}
                        </motion.span>
                      </div>
                    </div>

                    <p className="mb-3 text-sm text-slate-600">{e.summary}</p>

                    <div className="mb-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
                      <span className="flex items-center gap-1"><Globe className="h-3.5 w-3.5" /> {e.language}</span>
                      <span className="flex items-center gap-1"><PhoneCall className="h-3.5 w-3.5" /> {e.follow_up}</span>
                      <span className="flex items-center gap-1"><Clock3 className="h-3.5 w-3.5" /> {new Date(e.created_at).toLocaleString()}</span>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => updateStatus(e.id, "responded")}
                        className={`rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${
                          e.status === "responded"
                            ? "bg-blue-700 text-white"
                            : "border border-slate-200 text-slate-600 hover:bg-blue-50 hover:text-blue-700"
                        }`}
                      >
                        Responded
                      </button>
                      <button
                        onClick={() => updateStatus(e.id, "solved")}
                        className={`rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${
                          e.status === "solved"
                            ? "bg-emerald-600 text-white"
                            : "border border-slate-200 text-slate-600 hover:bg-emerald-50 hover:text-emerald-700"
                        }`}
                      >
                        Solved
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};