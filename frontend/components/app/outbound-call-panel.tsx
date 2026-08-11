"use client";
import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

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
      setStatus(res.ok ? "Call triggered! Check the SIP device." : `Error: ${data.error}`);
    } catch (e) {
      setStatus("Failed to trigger call.");
    }
  };

  const handleClick = () => {
    if (!sipAddress) {
      setStatus("Enter a SIP address first.");
      return;
    }
    const mins = parseFloat(delayMin);
    if (mins > 0) {
      setStatus(`Call scheduled in ${mins} min (keep this tab open).`);
      setTimeout(triggerCall, mins * 60 * 1000);
    } else {
      triggerCall();
    }
  };

  return (
    <div className="w-full max-w-sm rounded-2xl border bg-white p-6 shadow-sm">
      <h3 className="mb-3 font-semibold text-slate-900">Outbound Call</h3>
      <Input
        placeholder="username@sip-domain.com"
        value={sipAddress}
        onChange={(e) => setSipAddress(e.target.value)}
        className="mb-2"
      />
      <Input
        type="number"
        placeholder="Delay in minutes (optional)"
        value={delayMin}
        onChange={(e) => setDelayMin(e.target.value)}
        className="mb-3"
      />
      <Button onClick={handleClick} className="w-full rounded-full bg-blue-700 text-white hover:bg-blue-800">
        Trigger Call
      </Button>
      {status && <p className="mt-2 text-sm text-slate-500">{status}</p>}
    </div>
  );
};