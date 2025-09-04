import type {
  Trip,
  Driver,
  ProcessedTrip,
  ProcessedDriver,
  BreakPeriod,
  Warning,
  TrainSchedule,
  ScheduleData,
} from "@/types/schedule"

// Convert minutes from midnight to HH:MM format
export function minutesToTime(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}`
}

// Convert HH:MM to minutes from midnight
export function timeToMinutes(time: string): number {
  const [hours, minutes] = time.split(":").map(Number)
  return hours * 60 + minutes
}

// Process trips data
export function processTrips(trips: Trip[]): ProcessedTrip[] {
  return trips.map((trip) => ({
    ...trip,
    departureTime: minutesToTime(trip.departure),
    arrivalTime: minutesToTime(trip.arrival),
    duration: trip.arrival - trip.departure,
  }))
}

// Calculate break periods for a driver
function calculateBreaks(driver: Driver, trips: ProcessedTrip[]): BreakPeriod[] {
  const driverTrips = trips.filter((trip) => trip.driver === driver.driver).sort((a, b) => a.departure - b.departure)

  const breaks: BreakPeriod[] = []

  // Break before first trip
  if (driverTrips.length > 0 && driverTrips[0].departure > driver.start) {
    breaks.push({
      start: driver.start,
      end: driverTrips[0].departure,
      startTime: minutesToTime(driver.start),
      endTime: minutesToTime(driverTrips[0].departure),
      duration: driverTrips[0].departure - driver.start,
    })
  }

  // Breaks between trips
  for (let i = 0; i < driverTrips.length - 1; i++) {
    const currentTrip = driverTrips[i]
    const nextTrip = driverTrips[i + 1]

    if (nextTrip.departure > currentTrip.arrival) {
      breaks.push({
        start: currentTrip.arrival,
        end: nextTrip.departure,
        startTime: minutesToTime(currentTrip.arrival),
        endTime: minutesToTime(nextTrip.departure),
        duration: nextTrip.departure - currentTrip.arrival,
      })
    }
  }

  // Break after last trip
  const lastTrip = driverTrips[driverTrips.length - 1]
  if (lastTrip && lastTrip.arrival < driver.end) {
    breaks.push({
      start: lastTrip.arrival,
      end: driver.end,
      startTime: minutesToTime(lastTrip.arrival),
      endTime: minutesToTime(driver.end),
      duration: driver.end - lastTrip.arrival,
    })
  }

  return breaks
}

// Generate warnings for a driver
function generateDriverWarnings(driver: ProcessedDriver): Warning[] {
  const warnings: Warning[] = []

  // ---- constants (minutes unless noted) ----
  const MAX_SHIFT_HOURS = 9
  const LONG_SHIFT_MIN = 6 * 60
  const MAX_CONTINUOUS_WORK_MIN = 6 * 60
  const EARLY_BREAK_MIN = 3 * 60
  const MIN_PROPER_BREAK_MIN = 30

  // ---- overtime (in hours) ----
  if (driver.workingHours > MAX_SHIFT_HOURS) {
    warnings.push({
      type: "overtime",
      message: `Exceeds ${MAX_SHIFT_HOURS}-hour limit (${driver.workingHours.toFixed(1)}h)`,
      severity: "high",
    })
  }

  const workStart = driver.start
  const workEnd = driver.end

  // Warn if start work before 5:00 AM
  const START_WORK_EARLY_MIN = 5 * 60;
  if (workStart < START_WORK_EARLY_MIN) {
    warnings.push({
      type: "working_too_early",
      message: `Starts work too early (${minutesToTime(workStart)}), before 05:00`,
      severity: "high",
    });
  }

  // Guard: empty shift or inverted times
  if (workEnd <= workStart) return warnings

  // Normalize + sort breaks within [workStart, workEnd]
  const breaks = (driver.breaks ?? [])
    .map(b => {
      const start = Math.max(workStart, b.start)
      const end = Math.min(workEnd, b.end)
      return end > start
        ? { start, end, duration: Math.max(0, b.duration ?? end - start) }
        : null
    })
    .filter((b): b is {start:number; end:number; duration:number} => !!b)
    .sort((a, b) => a.start - b.start)

  // Trackers
  let hasProperBreak = false
  let lastAnyBreakEnd = workStart         // for continuous-work gaps
  let lastProperBreakEnd = workStart      // for early/late rules
  let longestGapWithoutBreak = 0
  let longestGapStart = workStart

  // Iterate all breaks to compute gaps and rules
  for (const br of breaks) {
    // 1) Continuous-work gap up to this break (ANY break ends a gap)
    const gap = Math.max(0, br.start - lastAnyBreakEnd)
    if (gap > longestGapWithoutBreak) {
      longestGapWithoutBreak = gap
      longestGapStart = lastAnyBreakEnd
    }
    // move the "any break" pointer
    lastAnyBreakEnd = Math.max(lastAnyBreakEnd, br.end)

    // 2) Early/Late/Short rules are relative to the last PROPER break
    const sinceProper = Math.max(0, br.start - lastProperBreakEnd)

    // If we haven't had a proper break yet and it's been > 6h: "late_break"
    if (!hasProperBreak && sinceProper > MAX_CONTINUOUS_WORK_MIN) {
      warnings.push({
        type: "late_break",
        message: `Break too late (${Math.floor(sinceProper / 60)}h ${sinceProper % 60}min since start)`,
        severity: "high",
      })
    }

    // If this break counts as proper (>=30 min)…
    if (br.duration >= MIN_PROPER_BREAK_MIN) {
      // First proper break must be between 3h and 6h from start
      if (!hasProperBreak && driver.workingHours > 6) {
        const timeFromStart = br.start - workStart;
        if (timeFromStart < EARLY_BREAK_MIN) {
          warnings.push({
            type: "early_break",
            message: `Break too early (only ${Math.floor(timeFromStart / 60)}h ${timeFromStart % 60}min since start)`,
            severity: "medium",
          })
        } else if (timeFromStart > MAX_CONTINUOUS_WORK_MIN) {
          warnings.push({
            type: "late_break",
            message: `Break too late (${Math.floor(timeFromStart / 60)}h ${timeFromStart % 60}min since start)`,
            severity: "high",
          })
        }
      }
      hasProperBreak = true
      lastProperBreakEnd = Math.max(lastProperBreakEnd, br.end)

    } 
  }
  // for (const br of breaks)
  // {
  //   // Short break (if long shift and we still haven't had a proper one)
  //   if (driver.workingHours > 6 && !hasProperBreak) {
  //     warnings.push({
  //       type: "short_break",
  //       message: `Break too short (${br.duration}min, minimum ${MIN_PROPER_BREAK_MIN}min required)`,
  //       severity: "medium",
  //     })
  //   }
  // }
  // Final continuous-work gap after the last break → end
  const finalGap = Math.max(0, workEnd - lastAnyBreakEnd)
  if (finalGap > longestGapWithoutBreak) {
    longestGapWithoutBreak = finalGap
    longestGapStart = lastAnyBreakEnd
  }

  // No proper break at all on a long shift
  if (!hasProperBreak && driver.workingHours > 6) {
    warnings.push({
      type: "no_break",
      message: "No proper break (30+ min) during long shift",
      severity: "high",
    })
  }

  // Single warning for the longest continuous-work segment
  if (longestGapWithoutBreak > MAX_CONTINUOUS_WORK_MIN) {
    const from = minutesToTime(longestGapStart)
    const to = minutesToTime(longestGapStart + longestGapWithoutBreak)
    warnings.push({
      type: "continuous_work",
      message: `Continuous work period too long (${Math.floor(longestGapWithoutBreak / 60)}h ${longestGapWithoutBreak % 60}min without break) - from ${from} to ${to}`,
      severity: "high",
    })
  }

  return warnings
}

// Process drivers data
export function processDrivers(drivers: Driver[], processedTrips: ProcessedTrip[]): ProcessedDriver[] {
  return drivers.map((driver) => {
    const driverTrips = processedTrips.filter((trip) => trip.driver === driver.driver)
    const breaks = calculateBreaks(driver, processedTrips)
    const workingHours = (driver.end - driver.start) / 60

    const processedDriver: ProcessedDriver = {
      ...driver,
      startTime: minutesToTime(driver.start),
      endTime: minutesToTime(driver.end),
      breaks_window_start: driver.breaks_window_start,
      breaks_window_end: driver.breaks_window_end,
      workingHours,
      trips: driverTrips,
      breaks,
      warnings: [],
    }

    processedDriver.warnings = generateDriverWarnings(processedDriver)

    return processedDriver
  })
}

// Check for overlapping trips and missing drivers
export function validateSchedule(trips: ProcessedTrip[], drivers: ProcessedDriver[]): Warning[] {
  const warnings: Warning[] = []
  const driverNames = new Set(drivers.map((d) => d.driver))

  // Check for trips without drivers
  trips.forEach((trip) => {
    if (!driverNames.has(trip.driver)) {
      warnings.push({
        type: "no_driver",
        message: `Trip ${trip.nr} (${trip.train}) has no assigned driver: ${trip.driver}`,
        severity: "high",
      })
    }
  })

  // Check for overlapping trips per driver with detailed timing
  drivers.forEach((driver) => {
    const sortedTrips = driver.trips.sort((a, b) => a.departure - b.departure)

    for (let i = 0; i < sortedTrips.length - 1; i++) {
      const current = sortedTrips[i]
      const next = sortedTrips[i + 1]

      if (current.arrival > next.departure) {
        const overlapMinutes = current.arrival - next.departure
        warnings.push({
          type: "overlap",
          message: `Driver ${driver.driver}: Trip ${current.nr} overlaps with Trip ${next.nr} by ${overlapMinutes}min`,
          severity: "high",
        })
      }

      // Check for insufficient turnaround time (less than 15 minutes between trips)
      else if (next.departure - current.arrival < 5) {
        const turnaroundTime = next.departure - current.arrival
        warnings.push({
          type: "tight_schedule",
          message: `Driver ${driver.driver}: Only ${turnaroundTime}min between Trip ${current.nr} and ${next.nr}`,
          severity: "medium",
        })
      }
    }
  })

  // Check for duplicate trip assignments (same trip assigned to multiple drivers)
  const tripAssignments = new Map<number, string[]>()
  trips.forEach((trip) => {
    if (!tripAssignments.has(trip.nr)) {
      tripAssignments.set(trip.nr, [])
    }
    tripAssignments.get(trip.nr)!.push(trip.driver)
  })

  tripAssignments.forEach((drivers, tripNr) => {
    if (drivers.length > 1) {
      warnings.push({
        type: "duplicate_assignment",
        message: `Trip ${tripNr} assigned to multiple drivers: ${drivers.join(", ")}`,
        severity: "high",
      })
    }
  })

  return warnings
}

// Process train schedules
export function processTrainSchedules(trips: ProcessedTrip[]): TrainSchedule[] {
  const trainMap = new Map<string, ProcessedTrip[]>()

  trips.forEach((trip) => {
    if (!trainMap.has(trip.train)) {
      trainMap.set(trip.train, [])
    }
    trainMap.get(trip.train)!.push(trip)
  })

  return Array.from(trainMap.entries()).map(([train, trainTrips]) => {
    const sortedTrips = trainTrips.sort((a, b) => a.departure - b.departure)

    // Calculate utilization (running time vs total time span)
    if (sortedTrips.length === 0) {
      return { train, trips: [], utilization: 0 }
    }

    const totalRunningTime = sortedTrips.reduce((sum, trip) => sum + trip.duration, 0)
    const firstDeparture = sortedTrips[0].departure
    const lastArrival = sortedTrips[sortedTrips.length - 1].arrival
    const totalTimeSpan = lastArrival - firstDeparture

    const utilization = totalTimeSpan > 0 ? (totalRunningTime / totalTimeSpan) * 100 : 0

    return {
      train,
      trips: sortedTrips,
      utilization: Math.round(utilization),
    }
  })
}

// Main processing function
export function processScheduleData(data: ScheduleData) {
  // console log number of drivers 
  console.log(`[processScheduleData] Processing schedule with ${data.drivers.length} drivers and ${data.trips.length} trips`)
  const processedTrips = processTrips(data.trips)
  const processedDrivers = processDrivers(data.drivers, processedTrips)
  const trainSchedules = processTrainSchedules(processedTrips)
  const globalWarnings = validateSchedule(processedTrips, processedDrivers)

  return {
    trips: processedTrips,
    drivers: processedDrivers,
    trains: trainSchedules,
    warnings: globalWarnings,
  }
}
