"use client"

import { useState, useMemo, useCallback } from "react"
import type { ProcessedDriver, TrainSchedule, ProcessedTrip, Warning } from "@/types/schedule"

interface UseDashboardDataProps {
  drivers: ProcessedDriver[]
  trains: TrainSchedule[]
  trips: ProcessedTrip[]
  warnings: Warning[]
}

export function useDashboardData({ drivers, trains, trips, warnings }: UseDashboardDataProps) {
  const [driverFilter, setDriverFilter] = useState<string[]>([])
  const [trainFilter, setTrainFilter] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    let filteredDrivers = drivers
    let filteredTrains = trains
    let filteredTrips = trips

    // Apply driver filter
    if (driverFilter.length > 0) {
      filteredDrivers = drivers.filter((driver) => driverFilter.includes(driver.driver))
      filteredTrips = trips.filter((trip) => driverFilter.includes(trip.driver))
    }

    // Apply train filter
    if (trainFilter.length > 0) {
      filteredTrains = trains.filter((train) => trainFilter.includes(train.train))
      filteredTrips = filteredTrips.filter((trip) => trainFilter.includes(trip.train))
    }

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      filteredDrivers = filteredDrivers.filter(
        (driver) =>
          driver.driver.toLowerCase().includes(searchLower) ||
          driver.trips.some((trip) => trip.destination.toLowerCase().includes(searchLower)),
      )
      filteredTrains = filteredTrains.filter(
        (train) =>
          train.train.toLowerCase().includes(searchLower) ||
          train.trips.some((trip) => trip.destination.toLowerCase().includes(searchLower)),
      )
      filteredTrips = filteredTrips.filter(
        (trip) =>
          trip.driver.toLowerCase().includes(searchLower) ||
          trip.train.toLowerCase().includes(searchLower) ||
          trip.destination.toLowerCase().includes(searchLower),
      )
    }

    // Filter warnings based on filtered drivers
    const filteredDriverNames = new Set(filteredDrivers.map((d) => d.driver))
    const filteredWarnings = warnings.filter((warning) => {
      if (warning.type === "no_driver" || warning.type === "overlap") {
        // Check if warning message contains any of the filtered drivers
        return (
          filteredDriverNames.size === 0 ||
          Array.from(filteredDriverNames).some((driver) => warning.message.includes(driver))
        )
      }
      return true
    })

    return {
      drivers: filteredDrivers,
      trains: filteredTrains,
      trips: filteredTrips,
      warnings: filteredWarnings,
    }
  }, [drivers, trains, trips, warnings, driverFilter, trainFilter, searchTerm])

  // Export functionality
  const exportData = useCallback(() => {
    const exportObj = {
      timestamp: new Date().toISOString(),
      summary: {
        totalDrivers: filteredData.drivers.length,
        totalTrains: filteredData.trains.length,
        totalTrips: filteredData.trips.length,
        totalWarnings: filteredData.warnings.length,
      },
      drivers: filteredData.drivers.map((driver) => ({
        driver: driver.driver,
        workingHours: driver.workingHours,
        trips: driver.trips.length,
        warnings: driver.warnings.length,
        compliance: driver.workingHours <= 9 ? "Compliant" : "Overtime",
      })),
      trains: filteredData.trains.map((train) => ({
        train: train.train,
        utilization: train.utilization,
        trips: train.trips.length,
      })),
      warnings: filteredData.warnings,
    }

    const dataStr = JSON.stringify(exportObj, null, 2)
    const dataBlob = new Blob([dataStr], { type: "application/json" })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement("a")
    link.href = url
    link.download = `train-schedule-report-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }, [filteredData])

  // Refresh functionality
  const refreshData = useCallback(() => {
    setIsLoading(true)
    // Simulate refresh delay
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }, [])

  return {
    filteredData,
    driverFilter,
    trainFilter,
    searchTerm,
    isLoading,
    setDriverFilter,
    setTrainFilter,
    setSearchTerm,
    exportData,
    refreshData,
  }
}
