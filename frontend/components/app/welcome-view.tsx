import * as React from "react";
import { Scale, ShieldCheck, Landmark, FileText, Gavel } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

const quickTopics = [
  {
    icon: Scale,
    title: "Know Your Rights",
  },
  {
    icon: ShieldCheck,
    title: "FIR & Police",
  },
  {
    icon: Landmark,
    title: "Consumer Rights",
  },
  {
    icon: FileText,
    title: "Property",
  },
  {
    icon: Gavel,
    title: "Cyber Crime",
  },
];

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ...props
}: React.ComponentProps<"div"> & WelcomeViewProps) => {
  return (
    <div
      {...props}
      className="flex min-h-screen items-center justify-center bg-slate-50 px-6"
    >
      <div className="w-full max-w-2xl rounded-3xl border bg-white p-10 shadow-lg">
        <div className="flex flex-col items-center text-center">
          <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-blue-100">
            <Scale className="h-10 w-10 text-blue-700" />
          </div>

          <h1 className="text-4xl font-bold text-slate-900">
            NyaAI
          </h1>

          <p className="mt-2 text-lg font-medium text-slate-700">
            AI Legal Literacy Assistant
          </p>

          <p className="mt-3 max-w-lg text-sm leading-6 text-slate-500">
            Know your rights. Understand Indian law.
            <br />
            Voice-first legal guidance for every citizen.
          </p>

          <Button
            size="lg"
            onClick={onStartCall}
            className="mt-8 w-64 rounded-full bg-blue-700 text-white hover:bg-blue-800"
          >
            {startButtonText}
          </Button>
        </div>

        <div className="mt-10">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Popular Topics
          </h2>

          <div className="grid grid-cols-2 gap-3">
            {quickTopics.map((topic) => (
              <div
                key={topic.title}
                className="flex items-center gap-3 rounded-xl border bg-slate-50 p-4"
              >
                <topic.icon className="h-5 w-5 text-blue-700" />
                <span className="text-sm font-medium text-slate-700">
                  {topic.title}
                </span>
              </div>
            ))}
          </div>
        </div>

        <p className="mt-8 text-center text-xs text-slate-500">
          NyaAI provides legal information only and is not a substitute for a lawyer.
        </p>
      </div>
    </div>
  );
};