import { useSolution } from "@/data/solution-context"
import { fetchScheduleData } from "@/data/sample-data"
import { useEffect, useState } from "react"
import type { ScheduleData } from "@/types/schedule"

export function useSolutionData() {
  const { solution } = useSolution()
  const [data, setData] = useState<ScheduleData | null>(null)

  useEffect(() => {
    if (solution) {
      setData(solution)
    } else {
      fetchScheduleData().then(setData).catch(() => setData(null))
    }
  }, [solution])

  return data
}
