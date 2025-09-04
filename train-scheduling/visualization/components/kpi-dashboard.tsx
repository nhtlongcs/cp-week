"use client"

import type { ProcessedDriver, TrainSchedule, ProcessedTrip } from "@/types/schedule"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Line,
} from "recharts"
import { Clock, Users, Train, AlertTriangle, TrendingUp, TrendingDown } from "lucide-react"

interface KPIDashboardProps {
  drivers: ProcessedDriver[]
  trains: TrainSchedule[]
  trips: ProcessedTrip[]
}

export function KPIDashboard({ drivers, trains, trips }: KPIDashboardProps) {
  // Driver working hours analysis
  const driverHoursData = drivers
    .map((driver) => ({
      driver: driver.driver,
      hours: driver.workingHours,
  trips: driver.trips ? driver.trips.length : 0,
      compliance: driver.workingHours <= 9 ? "Compliant" : "Overtime",
      utilizationRate:
        driver.trips && driver.trips.length > 0
          ? (driver.trips.reduce((sum, trip) => sum + trip.duration, 0) / (driver.workingHours * 60)) * 100
          : 0,
    }))
    .sort((a, b) => b.hours - a.hours)

  // Break duration analysis
  const breakAnalysis = drivers.map((driver) => {
    const totalBreakTime = driver.breaks.reduce((sum, breakPeriod) => sum + breakPeriod.duration, 0)
    const properBreaks = driver.breaks.filter((b) => b.duration >= 30).length
    const averageBreakDuration = driver.breaks.length > 0 ? totalBreakTime / driver.breaks.length : 0

    return {
      driver: driver.driver,
      totalBreakTime,
      properBreaks,
      averageBreakDuration,
      breakCompliance: driver.workingHours > 6 ? (properBreaks > 0 ? "Compliant" : "Non-Compliant") : "Not Required",
    }
  })

  // Trip distribution analysis
  const tripDistribution = drivers.map((driver) => ({
    driver: driver.driver,
  trips: driver.trips ? driver.trips.length : 0,
  totalDuration: driver.trips ? driver.trips.reduce((sum, trip) => sum + trip.duration, 0) : 0,
  }))

  const avgTripsPerDriver = tripDistribution.reduce((sum, d) => sum + d.trips, 0) / drivers.length
  const tripVariance =
    tripDistribution.reduce((sum, d) => sum + Math.pow(d.trips - avgTripsPerDriver, 2), 0) / drivers.length
  const isBalanced = tripVariance < 2 // Low variance indicates balanced distribution

  // Train utilization analysis
  const trainUtilizationData = trains
    .map((train) => {
  const totalRunningTime = train.trips ? train.trips.reduce((sum, trip) => sum + trip.duration, 0) : 0
      const totalTimeSpan =
        train.trips && train.trips.length > 0
          ? Math.max(...train.trips.map((t) => t.arrival)) - Math.min(...train.trips.map((t) => t.departure))
          : 0
      const standingTime = totalTimeSpan - totalRunningTime

      return {
        train: train.train,
        utilization: train.utilization,
        runningTime: totalRunningTime,
        standingTime: Math.max(0, standingTime),
  trips: train.trips ? train.trips.length : 0,
        efficiency: totalTimeSpan > 0 ? (totalRunningTime / totalTimeSpan) * 100 : 0,
      }
    })
    .sort((a, b) => b.utilization - a.utilization)

  // Overall metrics
  const totalDriverHours = drivers.reduce((sum, driver) => sum + driver.workingHours, 0)
  const overtimeDrivers = drivers.filter((d) => d.workingHours > 9).length
  const complianceRate = ((drivers.length - overtimeDrivers) / drivers.length) * 100
  const avgUtilization = trains.reduce((sum, train) => sum + train.utilization, 0) / trains.length

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"]

  return (
    <div className="space-y-6">
      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {drivers.length - overtimeDrivers}/{drivers.length} drivers compliant
            </p>
            <Progress value={complianceRate} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Train Utilization</CardTitle>
            <Train className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgUtilization.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Across {trains.length} trains</p>
            <Progress value={avgUtilization} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trip Distribution</CardTitle>
            {isBalanced ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isBalanced ? "Balanced" : "Unbalanced"}</div>
            <p className="text-xs text-muted-foreground">Avg: {avgTripsPerDriver.toFixed(1)} trips/driver</p>
            <Badge variant={isBalanced ? "default" : "destructive"} className="mt-2">
              Variance: {tripVariance.toFixed(1)}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Hours</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDriverHours.toFixed(1)}h</div>
            <p className="text-xs text-muted-foreground">{overtimeDrivers} overtime violations</p>
            {overtimeDrivers > 0 && (
              <Badge variant="destructive" className="mt-2">
                <AlertTriangle className="w-3 h-3 mr-1" />
                Overtime Alert
              </Badge>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Driver Working Hours Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Driver Working Hours vs 9h Limit</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={driverHoursData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="driver" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                  name === "hours" ? `${Number(value).toFixed(1)}h` : value,
                  name === "hours" ? "Working Hours" : "Trips",
                  ]}
                />
                <Bar dataKey="hours" fill="#8884d8" />
                {/* Reference line for 9h limit */}
                <Line type="monotone" dataKey={() => 9} stroke="#ff0000" strokeDasharray="5 5" />
                </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Train Utilization Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Train Utilization Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={trainUtilizationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ train, utilization }) => `${train}: ${utilization}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="utilization"
                >
                  {trainUtilizationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, "Utilization"]} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Trip Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Driving Duration by Driver vs 7h Limit </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tripDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="driver" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    name === "totalDuration" ? `${value}min` : value,
                    name === "totalDuration" ? "Total Duration" : "Number of Trips",
                  ]}
                />
                <Bar dataKey="totalDuration" fill="#ff7300" />
                <Line type="monotone" dataKey={() => 9*60} stroke="#ff0000" strokeDasharray="5 5" />

              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Trip Distribution by Driver</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tripDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="driver" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    name === "totalDuration" ? `${value}min` : value,
                    name === "totalDuration" ? "Total Duration" : "Number of Trips",
                  ]}
                />
                <Bar dataKey="trips" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Break Compliance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Long Break Compliance Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={breakAnalysis}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="driver" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    `${value}${name === "totalBreakTime" || name === "averageBreakDuration" ? "min" : ""}`,
                    name === "totalBreakTime"
                      ? "Total Break Time"
                      : name === "properBreaks"
                        ? "Proper Breaks (30+ min)"
                        : "Average Break Duration",
                  ]}
                />
                <Bar dataKey="properBreaks" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>      
      <Card>
          <CardHeader>
            <CardTitle>Total Break Compliance Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={breakAnalysis}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="driver" />
                <YAxis />
                <Tooltip
                  formatter={(value, name) => [
                    `${value}${name === "totalBreakTime" || name === "averageBreakDuration" ? "min" : ""}`,
                    name === "totalBreakTime"
                      ? "Total Break Time"
                      : name === "properBreaks"
                        ? "Proper Breaks (30+ min)"
                        : "Average Break Duration",
                  ]}
                />
                <Bar dataKey="totalBreakTime" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Driver Performance Table */}
        <Card>
          <CardHeader>
            <CardTitle>Driver Performance Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {driverHoursData.map((driver) => (
                <div key={driver.driver} className="flex items-center justify-between p-3 border rounded">
                  <div>
                    <div className="font-medium">{driver.driver}</div>
                    <div className="text-sm text-muted-foreground">
                      {driver.trips} trips • {driver.utilizationRate.toFixed(1)}% utilization
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{driver.hours.toFixed(1)}h</div>
                    <Badge variant={driver.compliance === "Compliant" ? "default" : "destructive"}>
                      {driver.compliance}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Train Efficiency Table */}
        <Card>
          <CardHeader>
            <CardTitle>Train Efficiency Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {trainUtilizationData.map((train) => (
                <div key={train.train} className="flex items-center justify-between p-3 border rounded">
                  <div>
                    <div className="font-medium">{train.train}</div>
                    <div className="text-sm text-muted-foreground">
                      {train.trips} trips • {train.runningTime}min running • {train.standingTime}min standing
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{train.utilization}%</div>
                    <Badge
                      variant={
                        train.utilization >= 70 ? "default" : train.utilization >= 50 ? "secondary" : "destructive"
                      }
                    >
                      {train.utilization >= 70 ? "Efficient" : train.utilization >= 50 ? "Moderate" : "Low"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
