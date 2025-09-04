"use client"

import React from "react"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Clock, Users, Train } from "lucide-react"
import { processScheduleData } from "@/lib/schedule-utils"
import { useSolutionData } from "./solution-data"
import { DriverGanttChart } from "@/components/driver-gantt-chart"
import { TrainGanttChart } from "@/components/train-gantt-chart"
import { WarningPanel } from "@/components/warning-panel"
import { KPIDashboard } from "@/components/kpi-dashboard"
import { DashboardFilters } from "@/components/dashboard-filters"
import { useDashboardData } from "@/hooks/use-dashboard-data"

export default function TrainScheduleDashboard() {

  const solutionData = useSolutionData() || { drivers: [], trains: [], trips: [] }
  const scheduleData = processScheduleData(solutionData)

  const {
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
  } = useDashboardData(scheduleData)

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive"
      case "medium":
        return "secondary"
      case "low":
        return "outline"
      default:
        return "outline"
    }
  }

  const totalWorkingHours = filteredData.drivers.reduce((sum, driver) => sum + driver.workingHours, 0)
  const averageUtilization =
    filteredData.trains.length > 0
      ? filteredData.trains.reduce((sum, train) => sum + train.utilization, 0) / filteredData.trains.length
      : 0

  const driverWarnings = filteredData.drivers
    .filter((driver) => driver.warnings.length > 0)
    .map((driver) => ({ driver: driver.driver, warnings: driver.warnings }))

  // Get unique drivers and trains for filter options
  const allDrivers = Array.from(new Set(scheduleData.drivers?.map((d) => d.driver) ?? [])).sort()
  const allTrains = Array.from(new Set(scheduleData.trains?.map((t) => t.train) ?? [])).sort()

  return (
    <div className="min-h-screen bg-background p-4 md:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Train Schedule Dashboard</h1>
            <p className="text-muted-foreground">Monitor driver schedules, train operations, and compliance</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              Live Data
            </Badge>
            {(driverFilter.length > 0 || trainFilter.length > 0 || searchTerm) && (
              <Badge variant="secondary">
                Filtered ({filteredData.drivers.length}/{scheduleData.drivers.length} drivers)
              </Badge>
            )}
          </div>
        </div>

        {/* Interactive Filters */}
        <DashboardFilters
          drivers={allDrivers}
          trains={allTrains}
          onDriverFilter={setDriverFilter}
          onTrainFilter={setTrainFilter}
          onSearchChange={setSearchTerm}
          onRefresh={refreshData}
          onExport={exportData}
          isLoading={isLoading}
        />

        {/* Enhanced Warning Panel */}
        <div className="animate-in fade-in-50 duration-500">
          <WarningPanel warnings={filteredData.warnings} driverWarnings={driverWarnings} />
        </div>

        {/* KPI Cards with loading states */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Drivers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? <div className="h-8 w-16 bg-muted animate-pulse rounded" /> : filteredData.drivers.length}
              </div>
              <p className="text-xs text-muted-foreground">
                {filteredData.drivers.filter((d) => d.warnings.length > 0).length} with warnings
              </p>
            </CardContent>
          </Card>

          <Card className="transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Working Hours</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? (
                  <div className="h-8 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${totalWorkingHours.toFixed(1)}h`
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                Avg:{" "}
                {filteredData.drivers.length > 0 ? (totalWorkingHours / filteredData.drivers.length).toFixed(1) : 0}h
                per driver
              </p>
            </CardContent>
          </Card>

          <Card className="transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Train Utilization</CardTitle>
              <Train className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? (
                  <div className="h-8 w-16 bg-muted animate-pulse rounded" />
                ) : (
                  `${averageUtilization.toFixed(0)}%`
                )}
              </div>
              <p className="text-xs text-muted-foreground">Average across {filteredData.trains.length} trains</p>
            </CardContent>
          </Card>

          <Card className="transition-all duration-200 hover:shadow-md">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Trips</CardTitle>
              <Train className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? <div className="h-8 w-16 bg-muted animate-pulse rounded" /> : filteredData.trips.length}
              </div>
              <p className="text-xs text-muted-foreground">Across {filteredData.trains.length} trains</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="drivers" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="drivers" className="transition-all duration-200">
              Driver View
            </TabsTrigger>
            <TabsTrigger value="trains" className="transition-all duration-200">
              Train View
            </TabsTrigger>
            <TabsTrigger value="analysis" className="transition-all duration-200">
              Analysis & KPIs
            </TabsTrigger>
          </TabsList>

          <TabsContent value="drivers" className="space-y-4 animate-in fade-in-50 duration-300">
            <Card>
              <CardHeader>
                <CardTitle>Driver Schedules</CardTitle>
                <CardDescription>
                  Gantt chart view showing work periods, breaks, and trips for each driver
                  {filteredData.drivers.length !== scheduleData.drivers.length && (
                    <span className="text-primary">
                      {" "}
                      • Showing {filteredData.drivers.length} of {scheduleData.drivers.length} drivers
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-16 bg-muted animate-pulse rounded" />
                    ))}
                  </div>
                ) : (
                  <DriverGanttChart drivers={filteredData.drivers} />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trains" className="space-y-4 animate-in fade-in-50 duration-300">
            <Card>
              <CardHeader>
                <CardTitle>Train Schedules</CardTitle>
                <CardDescription>
                  Gantt chart view showing train operations, driver assignments, and utilization
                  {filteredData.trains.length !== scheduleData.trains.length && (
                    <span className="text-primary">
                      {" "}
                      • Showing {filteredData.trains.length} of {scheduleData.trains.length} trains
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="h-20 bg-muted animate-pulse rounded" />
                    ))}
                  </div>
                ) : (
                  <TrainGanttChart trains={filteredData.trains} allTrips={filteredData.trips} />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-4 animate-in fade-in-50 duration-300">
            {isLoading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <Card key={i}>
                    <CardHeader>
                      <div className="h-6 w-32 bg-muted animate-pulse rounded" />
                    </CardHeader>
                    <CardContent>
                      <div className="h-64 bg-muted animate-pulse rounded" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <KPIDashboard drivers={filteredData.drivers} trains={filteredData.trains} trips={filteredData.trips} />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
