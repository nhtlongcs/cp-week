import React from "react";
import { useSolution } from "@/data/solution-context";
import type { ScheduleData } from "@/types/schedule";

interface SolutionUploadProps {
  onUpload?: () => void;
}

export default function SolutionUpload({ onUpload }: SolutionUploadProps) {
  const { setSolution } = useSolution();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    try {
      const json = JSON.parse(text) as ScheduleData;
      setSolution(json);
      if (onUpload) onUpload();
    } catch {
      alert("Invalid solution file");
    }
  };

  return (
    <div>
      <input type="file" accept="application/json" onChange={handleUpload} />
    </div>
  );
}
