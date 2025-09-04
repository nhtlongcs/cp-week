"use client"

import type { TrainSchedule, ProcessedTrip } from "@/types/schedule"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { AlertTriangle } from "lucide-react"

interface TrainGanttChartProps {
  trains: TrainSchedule[]
  allTrips: ProcessedTrip[]
}

export function TrainGanttChart({ trains, allTrips }: TrainGanttChartProps) {
  // Calculate time range for the chart
  const minTime = Math.min(...allTrips.map((t) => t.departure))
  const maxTime = Math.max(...allTrips.map((t) => t.arrival))
  const timeRange = maxTime - minTime

  const timeGridLines = []
  const timeLabels = []

  for (let time = Math.floor(minTime / 30) * 30; time <= maxTime; time += 30) {
    const hours = Math.floor(time / 60)
    const minutes = time % 60
    const isHourMark = minutes === 0

    timeGridLines.push({
      time,
      isHourMark,
      position: ((time - minTime) / timeRange) * 100,
    })

    if (isHourMark) {
      timeLabels.push({
        time,
        label: `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`,
        position: ((time - minTime) / timeRange) * 100,
      })
    }
  }

  const getPositionAndWidth = (start: number, end: number) => {
    const left = ((start - minTime) / timeRange) * 100
    const width = ((end - start) / timeRange) * 100
    return { left: `${left}%`, width: `${width}%` }
  }

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 80) return "bg-green-500"
    if (utilization >= 60) return "bg-yellow-500"
    if (utilization >= 40) return "bg-orange-500"
    return "bg-red-500"
  }

  const getDriverColor = (driverIndex: number) => {
    const colors = [
      "bg-blue-500",
      "bg-purple-500",
      "bg-pink-500",
      "bg-indigo-500",
      "bg-cyan-500",
      "bg-teal-500",
      "bg-emerald-500",
      "bg-lime-500",
    ]
    return colors[driverIndex % colors.length]
  }

  // Get unique drivers for color mapping
  const uniqueDrivers = Array.from(new Set(allTrips.map((t) => t.driver))).sort()

  return (
    <TooltipProvider>
      <div className="space-y-4 overflow-x-auto">
        {/* Time axis */}
        <div className="relative h-8 border-b border-border min-w-[800px]">
          <div className="absolute inset-0 flex">
            {timeLabels.map((label) => (
              <div
                key={label.time}
                className="absolute text-xs text-muted-foreground"
                style={{ left: `${label.position}%` }}
              >
                {label.label}
              </div>
            ))}
          </div>
        </div>

        {/* Train rows */}
        <div className="space-y-4 min-w-[800px] relative">
          <div className="absolute inset-0 pointer-events-none">
            {timeGridLines.map((gridLine) => (
              <div
                key={gridLine.time}
                className={`absolute top-0 bottom-0 ${
                  gridLine.isHourMark ? "border-l border-border/40" : "border-l border-border/20"
                }`}
                style={{ left: `${gridLine.position}%` }}
              />
            ))}
          </div>

          {trains.map((train) => (
            <div key={train.train} className="flex gap-4 relative">
              {/* Train info panel - moved to left */}
              <div className="w-48 flex-shrink-0 space-y-2">
                <div className="text-sm font-medium">{train.train}</div>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="outline" className="text-xs">
                    {train.utilization}% utilization
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {train.trips.length} trips
                  </Badge>
                  {train.utilization < 50 && (
                    <Tooltip>
                      <TooltipTrigger>
                        <Badge variant="destructive" className="text-xs flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          Low utilization
                        </Badge>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Train utilization below 50% - consider optimization</p>
                      </TooltipContent>
                    </Tooltip>
                  )}
                </div>

                {/* Trip summary moved here */}
                <div className="text-xs text-muted-foreground">
                  {train.trips.length > 0 ? (
                    <>
                      Destinations: {Array.from(new Set(train.trips.map((t) => t.destination))).join(", ")} | Drivers:{" "}
                      {Array.from(new Set(train.trips.map((t) => t.driver))).join(", ")}
                    </>
                  ) : (
                    "No trips scheduled"
                  )}
                </div>
              </div>

              {/* Gantt timeline - expanded */}
              <div className="flex-1 relative h-20 bg-muted/20 rounded">
                {/* Background utilization bar */}
                <div className="absolute top-0 left-0 right-0 h-2 bg-gray-200 dark:bg-gray-700">
                  <div
                    className={`h-full ${getUtilizationColor(train.utilization)} opacity-60`}
                    style={{ width: `${train.utilization}%` }}
                  />
                </div>

                {/* Trip blocks */}
                {train.trips.map((trip) => {
                  const driverIndex = uniqueDrivers.indexOf(trip.driver)
                  return (
                    <Tooltip key={trip.nr}>
                      <TooltipTrigger asChild>
                        <div
                          className={`absolute top-3 h-14 ${getDriverColor(driverIndex)} rounded flex flex-col items-center justify-center text-white text-xs font-medium cursor-pointer hover:opacity-80 transition-opacity`}
                          style={getPositionAndWidth(trip.departure, trip.arrival)}
                        >
                          <div className="font-semibold">#{trip.nr}</div>
                          <div className="text-xs opacity-90">{trip.driver}</div>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <div className="space-y-1">
                          <p className="font-medium">
                            Trip #{trip.nr} - {train.train}
                          </p>
                          <p>Driver: {trip.driver}</p>
                          <p>Destination: {trip.destination}</p>
                          <p>
                            Time: {trip.departureTime} - {trip.arrivalTime}
                          </p>
                          <p>Duration: {trip.duration} minutes</p>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  )
                })}

                {/* Standing time indicators (gaps between trips) */}
                {train.trips.length > 1 &&
                  train.trips
                    .sort((a, b) => a.departure - b.departure)
                    .slice(0, -1)
                    .map((trip, index) => {
                      const nextTrip = train.trips.sort((a, b) => a.departure - b.departure)[index + 1]
                      const gapStart = trip.arrival
                      const gapEnd = nextTrip.departure

                      if (gapEnd > gapStart) {
                        return (
                          <Tooltip key={`gap-${index}`}>
                            <TooltipTrigger asChild>
                              <div
                                className="absolute top-3 h-14 bg-gray-400 dark:bg-gray-600 opacity-50 border-2 border-dashed border-gray-500"
                                style={getPositionAndWidth(gapStart, gapEnd)}
                              />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Standing time: {gapEnd - gapStart} minutes</p>
                              <p>
                                From {trip.arrivalTime} to {nextTrip.departureTime}
                              </p>
                            </TooltipContent>
                          </Tooltip>
                        )
                      }
                      return null
                    })}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="space-y-2 pt-4 border-t border-border">
          <div className="flex items-center gap-6 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="w-4 h-3 bg-blue-500 rounded" />
              <span>Trip Block</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-3 bg-gray-400 opacity-50 border-2 border-dashed border-gray-500 rounded" />
              <span>Standing Time</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-2 bg-green-500" />
              <span>High Utilization (80%+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-2 bg-red-500" />
              <span>Low Utilization (&lt;40%)</span>
            </div>
          </div>

          <div className="text-xs text-muted-foreground">
            <span className="font-medium">Driver Colors:</span>{" "}
            {uniqueDrivers.map((driver, index) => (
              <span key={driver} className="inline-flex items-center gap-1 ml-2">
                <div className={`w-3 h-3 ${getDriverColor(index)} rounded`} />
                {driver}
              </span>
            ))}
          </div>
        </div>
      </div>
    </TooltipProvider>
  )
}
