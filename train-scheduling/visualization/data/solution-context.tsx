import React, { createContext, useContext, useState, ReactNode } from "react";
import type { ScheduleData } from "@/types/schedule";

interface SolutionContextType {
  solution: ScheduleData | null;
  setSolution: (data: ScheduleData | null) => void;
}

const SolutionContext = createContext<SolutionContextType | undefined>(undefined);

export function SolutionProvider({ children }: { children: ReactNode }) {
  const [solution, setSolution] = useState<ScheduleData | null>(null);

  return (
    <SolutionContext.Provider value={{ solution, setSolution }}>
      {children}
    </SolutionContext.Provider>
  );
}

export function useSolution() {
  const context = useContext(SolutionContext);
  if (!context) throw new Error("useSolution must be used within SolutionProvider");
  return context;
}
