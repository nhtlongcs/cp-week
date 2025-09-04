"use client"

import type { ProcessedDriver } from "@/types/schedule"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { AlertTriangle } from "lucide-react"

interface DriverGanttChartProps {
  drivers: ProcessedDriver[]
}

export function DriverGanttChart({ drivers }: DriverGanttChartProps) {
  // Calculate time range for the chart (earliest start to latest end)
  const rawMinTime = Math.min(...drivers.map((d) => d.start));
  const rawMaxTime = Math.max(...drivers.map((d) => d.end));
  // Round min/max to nearest 30 for grid consistency
  const minTime = Math.floor(rawMinTime / 30) * 30;
  const maxTime = Math.ceil(rawMaxTime / 30) * 30;
  const timeRange = maxTime - minTime;

  const timeGridLines = [];
  const timeLabels = [];

  for (let time = minTime; time <= maxTime; time += 30) {
    const hours = Math.floor(time / 60);
    const minutes = time % 60;
    const isHourMark = minutes === 0;

    timeGridLines.push({
      time,
      isHourMark,
      position: ((time - minTime) / timeRange) * 100,
    });

    if (isHourMark) {
      timeLabels.push({
        time,
        label: `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`,
        position: ((time - minTime) / timeRange) * 100,
      });
    }
  }

  // Convert minutes to grid position (percentage)
  const getGridPosition = (minute: number) => {
    if (timeRange === 0) return 0;
    // Clamp minute to min/max to avoid negative or >100% positions
    const clamped = Math.max(minTime, Math.min(maxTime, minute));
    return ((clamped - minTime) / timeRange) * 100;
  };

  // Convert a time range to left/width for absolute positioning
  const getPositionAndWidth = (start: number, end: number) => {
    const left = getGridPosition(start);
    const right = getGridPosition(end);
    const width = right - left;
    return { left: `${left}%`, width: `${width}%` };
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <TooltipProvider>
        <div className="space-y-4 overflow-x-auto">
          {/* Time axis */}
          <div className="relative h-8 border-b border-border min-w-[800px] flex">
            {/* Offset for Driver info panel */}
            <div className="w-48 flex-shrink-0" />
            <div className="flex-1 relative">
              <div className="absolute inset-0 flex">
                {timeLabels.map((label) => (
                  <div
                    key={label.time}
                    className="absolute text-xs text-muted-foreground left-0"
                    style={{ left: `${getGridPosition(label.time)}%`, textAlign: "left" }}
                  >
                    {label.label}
                  </div>
                ))}
              </div>
            </div>
          </div>

        {/* Driver rows */}
        <div className="space-y-4 min-w-[800px] relative">
          <div className="absolute inset-0 pointer-events-none">
            {timeGridLines.map((gridLine) => (
              <div
                key={gridLine.time}
                className={`absolute top-0 bottom-0 ${
                  gridLine.isHourMark ? "border-l border-border/40" : "border-l border-border/20"
                }`}
                style={{ left: `${getGridPosition(gridLine.time)}%` }}
              />
            ))}
          </div>

          {drivers.map((driver) => (
            <div key={driver.driver} className="flex gap-4 relative">
              {/* Driver info panel - moved to left */}
              <div className="w-48 flex-shrink-0 space-y-2">
                <div className="text-sm font-medium">{driver.driver}</div>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="outline" className="text-xs">
                    {driver.startTime} - {driver.endTime}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {driver.workingHours.toFixed(1)}h
                  </Badge>
                  {driver.warnings.map((warning, index) => (
                    <Tooltip key={index}>
                      <TooltipTrigger>
                        <Badge variant="destructive" className="text-xs flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          {warning.type}
                        </Badge>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{warning.message}</p>
                      </TooltipContent>
                    </Tooltip>
                  ))}
                </div>

                {/* Trip summary moved here */}
                <div className="text-xs text-muted-foreground">
                  {driver.trips.length > 0 ? (
                    <>
                      {driver.trips.length} trips: {driver.trips.map((t) => `#${t.nr}(${t.train})`).join(", ")}
                    </>
                  ) : (
                    "No trips assigned"
                  )}
                </div>
              </div>

              {/* Gantt timeline - expanded */}
              <div className="flex-1 relative h-16 bg-muted/20 rounded">
                {/* Work period background */}
                <div
                  className="absolute top-0 h-full bg-blue-200 dark:bg-blue-900/50 rounded"
                  style={getPositionAndWidth(driver.start, driver.end)}
                />

                {/* CLOCK ON interval (start to start+15) */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div
                        className="absolute top-0 h-full bg-red-300/80 border-l-2 border-yellow-600 rounded z-10 cursor-pointer"
                        style={getPositionAndWidth(driver.start, driver.start + 15)}
                      />
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>Work Start: {driver.startTime}</span>
                    </TooltipContent>
                  </Tooltip>
                {/* CLOCK OFF interval (end-15 to end) */}
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div
                        className="absolute top-0 h-full bg-red-300/80 border-r-2 border-red-600 rounded z-10 cursor-pointer"
                        style={getPositionAndWidth(driver.end - 15, driver.end)}
                      />
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>Work End: {driver.endTime}</span>
                    </TooltipContent>
                  </Tooltip>

                
                {/* Break periods */}
                {driver.breaks.map((breakPeriod, index) => (
                  <Tooltip key={index}>
                    <TooltipTrigger asChild>
                      <div
                        className={`absolute top-0 h-full ${breakPeriod.duration > 60 ? "bg-yellow-400 dark:bg-yellow-700" : "bg-gray-300 dark:bg-gray-600"}`}
                        style={getPositionAndWidth(breakPeriod.start, breakPeriod.end)}
                        title={breakPeriod.duration > 15 ? "Long Break" : "Break"}
                      />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>
                        Break: {breakPeriod.startTime} - {breakPeriod.endTime}
                      </p>
                      <p>Duration: {breakPeriod.duration} minutes</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
                {/* Break window dotted lines */}
                {/* Break window start annotation */}
                <div
                  className="absolute z-20"
                  style={{ left: `${getGridPosition(driver.breaks_window_start)}%`, top: '-18px' }}
                >
                    <span
                    className="text-xs text-purple-700 bg-white px-1 rounded border border-purple-300"
                    style={{ position: "relative", top: "-6px" }}
                    >
                    Break Window Region
                    </span>
                </div>
                <div
                  className="absolute top-0 h-full border-l-2 border-dotted border-purple-500 z-20"
                  style={{ left: `${getGridPosition(driver.breaks_window_start)}%` }}
                  title="Break Window Start"
                />
                {/* Break window end annotation */}

                <div
                  className="absolute top-0 h-full border-l-2 border-dotted border-purple-500 z-20"
                  style={{ left: `${getGridPosition(driver.breaks_window_end)}%` }}
                  title="Break Window End"
                />
                {/* Trip periods */}
                {driver.trips.map((trip) => (
                  <Tooltip key={trip.nr}>
                    <TooltipTrigger asChild>
                      <div
                        className="absolute top-2 h-12 bg-green-500 dark:bg-green-600 rounded flex items-center justify-center text-white text-xs font-medium cursor-pointer hover:bg-green-600 dark:hover:bg-green-500 transition-colors"
                        style={getPositionAndWidth(trip.departure, trip.arrival)}
                      >
                        {trip.train}
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <div className="space-y-1">
                        <p>
                          Trip #{trip.nr} - {trip.train}
                        </p>
                        <p>Route: {trip.destination}</p>
                        <p>
                          Time: {trip.departureTime} - {trip.arrivalTime}
                        </p>
                        <p>Duration: {trip.duration} minutes</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                ))}

                {/* Warning indicators */}
                {/* {driver.warnings.map((warning, index) => (
                  <div
                    key={index}
                    className={`absolute top-0 w-1 h-full ${getSeverityColor(warning.severity)} opacity-80`}
                    style={{ right: `${index * 4}px` }}
                  />
                ))} */}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 text-xs text-muted-foreground pt-4 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-blue-200 dark:bg-blue-900/50 rounded" />
            <span>Work Period</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-gray-300 dark:bg-gray-600 rounded" />
            <span>Break</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-3 bg-green-500 rounded" />
            <span>Trip</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-3 bg-red-400 border-2 border-red-600" />
            <span>CLOCK ON/CLOCK OFF</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-3 border-l-2 border-dotted border-purple-500" />
            <span>Break Window</span>
          </div>
        </div>
      </div>
    </TooltipProvider>
  )
}
