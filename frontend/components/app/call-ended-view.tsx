import * as React from "react";
import { Scale, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CallEndedViewProps {
  onStartAgain: () => void;
  onDismiss: () => void;
}

export const CallEndedView = ({
  onStartAgain,
  onDismiss,
  ...props
}: React.ComponentProps<"div"> & CallEndedViewProps) => {
  return (
    <div
      {...props}
      className="flex min-h-screen items-center justify-center bg-slate-50 px-6"
    >
      <div className="w-full max-w-md rounded-3xl border bg-white p-10 shadow-lg text-center">
        <div className="mb-4 mx-auto flex h-20 w-20 items-center justify-center">
  <img src="/nyaai-logo.svg" alt="NyaAI" className="h-20 w-20" />
</div>

        <h1 className="text-2xl font-bold text-slate-900">
          Conversation Ended
        </h1>
        <Button
  size="lg"
  onClick={onStartAgain}
  className="mt-8 w-full rounded-full bg-blue-700 text-white hover:bg-blue-800"
>
  <RotateCcw className="mr-2 h-4 w-4" />
  Start Again
</Button>

<Button
  variant="ghost"
  size="lg"
  onClick={onDismiss}
  className="mt-3 w-full rounded-full text-slate-800 hover:text-slate-1000"
>
  No thanks
</Button>
      </div>
    </div>
  );
};