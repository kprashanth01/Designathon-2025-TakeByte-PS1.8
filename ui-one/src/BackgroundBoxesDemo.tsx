"use client";
import React from "react";
import { Boxes } from "@/components/ui/background-boxes";
import { cn } from "@/lib/utils";
import { ChatComponent2 } from "./ChatComponent2";

export function BackgroundBoxesDemo() {
  return (
    <div className="relative w-full h-full overflow-hidden bg-slate-900 flex flex-col items-center justify-center rounded-lg">
      <div className="absolute inset-0 w-full h-full bg-slate-900 z-0 [mask-image:radial-gradient(transparent,white)] pointer-events-none" />

      <Boxes />
      <ChatComponent2 setRecentSearches={() => {}} recentSearches={[]} />
    </div>
  );
} 