import type { ScheduleData } from "@/types/schedule"

// Fetch sample data from public folder
export async function fetchScheduleData(): Promise<ScheduleData> {
  const response = await fetch("/solution.json")
  if (!response.ok) throw new Error("Failed to fetch schedule data")
  return await response.json()
}

