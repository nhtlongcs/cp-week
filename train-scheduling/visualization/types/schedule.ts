export interface Trip {
  nr: number
  train: string
  driver: string
  departure: number // minutes from midnight
  arrival: number // minutes from midnight
  destination: string
}

export interface Driver {
  driver: string
  start: number // minutes from midnight
  breaks_window_start: number // minutes from midnight
  breaks_window_end: number // minutes from midnight
  end: number // minutes from midnight
}

export interface ScheduleData {
  trips: Trip[]
  drivers: Driver[]
}

export interface ProcessedTrip extends Trip {
  departureTime: string // HH:MM format
  arrivalTime: string // HH:MM format
  duration: number // minutes
}

export interface ProcessedDriver extends Driver {
  startTime: string // HH:MM format
  endTime: string // HH:MM format
  breaks_window_start: number
  breaks_window_end: number
  workingHours: number // total hours
  trips: ProcessedTrip[]
  breaks: BreakPeriod[]
  warnings: Warning[]
}

export interface BreakPeriod {
  start: number
  end: number
  startTime: string
  endTime: string
  duration: number
}

export interface Warning {
  type:
    | "overtime"
    | "no_break"
    | "late_break"
    | "overlap"
    | "no_driver"
    | "early_break"
    | "short_break"
    | "continuous_work"
    | "tight_schedule"
    | "duplicate_assignment"
    | "working_too_early"
    | "work_out_of_time"
  message: string
  severity: "low" | "medium" | "high"
}

export interface TrainSchedule {
  train: string
  trips: ProcessedTrip[]
  utilization: number // percentage
}
