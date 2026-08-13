"use client";
import * as React from "react";
import { Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export const OutboundCallPanel = () => {
  const [sipAddress, setSipAddress] = React.useState("");
  const [delayMin, setDelayMin] = React.useState("");
  const [status, setStatus] = React.useState("");

  const triggerCall = async () => {
    setStatus("Calling...");
    try {
      const res = await fetch("/api/trigger-call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sipAddress }),
      });
      const data = await res.json();
      setStatus(res.ok ? "Call triggered!" : `Error: ${data.error}`);
    } catch {
      setStatus("Failed to trigger call.");
    }
  };

  const handleClick = () => {
    if (!sipAddress) { setStatus("Enter a SIP address first."); return; }
    const mins = parseFloat(delayMin);
    if (mins > 0) {
      setStatus(`Scheduled in ${mins} min (keep tab open).`);
      setTimeout(triggerCall, mins * 60 * 1000);
    } else {
      triggerCall();
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="flex h-9 w-9 items-center justify-center rounded-full border text-slate-600 hover:bg-slate-100">
          <Phone className="h-4 w-4" />
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-72">
        <h3 className="mb-3 text-sm font-semibold text-slate-900">Manual Outbound Call</h3>
        <Input placeholder="username@sip-domain.com" value={sipAddress} onChange={(e) => setSipAddress(e.target.value)} className="mb-2" />
        <Input type="number" placeholder="Delay in minutes (optional)" value={delayMin} onChange={(e) => setDelayMin(e.target.value)} className="mb-3" />
        <Button onClick={handleClick} className="w-full rounded-full bg-blue-700 text-white hover:bg-blue-800">Trigger Call</Button>
        {status && <p className="mt-2 text-xs text-slate-500">{status}</p>}
      </PopoverContent>
    </Popover>
  );
};