import React from "react";
import { useSolution } from "@/data/solution-context";
import type { ScheduleData } from "@/types/schedule";

interface SolutionUploadProps {
  onUpload?: () => void;
  icon?: React.ReactNode;
  renderStatus?: (fileChosen: boolean) => React.ReactNode;
}

export default function SolutionUpload({ onUpload, icon, renderStatus }: SolutionUploadProps) {
  const { setSolution } = useSolution();
  const [fileChosen, setFileChosen] = React.useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setFileChosen(!!file);
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
    <div className="flex items-center gap-2">
      <label className="flex items-center cursor-pointer gap-2">
        {icon}
        <input type="file" accept="application/json" onChange={handleUpload} style={{ display: 'none' }} />
        <span className="text-sm">Upload Solution</span>
      </label>
      {renderStatus && renderStatus(fileChosen)}
    </div>
  );
}
