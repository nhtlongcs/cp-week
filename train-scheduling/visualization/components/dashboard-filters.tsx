"use client"

import { useState } from "react"
import SolutionUpload from '@/components/solution-upload'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Search, Filter, RefreshCw, Download, X } from "lucide-react"

interface DashboardFiltersProps {
  drivers: string[]
  trains: string[]
  onDriverFilter: (drivers: string[]) => void
  onTrainFilter: (trains: string[]) => void
  onSearchChange: (search: string) => void
  onRefresh: () => void
  onExport: () => void
  isLoading?: boolean
}

export function DashboardFilters({
  drivers,
  trains,
  onDriverFilter,
  onTrainFilter,
  onSearchChange,
  onRefresh,
  onExport,
  isLoading = false,
}: DashboardFiltersProps) {
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])
  const [selectedTrains, setSelectedTrains] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [showFilters, setShowFilters] = useState(false)

  const handleDriverSelect = (driver: string) => {
    const newSelection = selectedDrivers.includes(driver)
      ? selectedDrivers.filter((d) => d !== driver)
      : [...selectedDrivers, driver]
    setSelectedDrivers(newSelection)
    onDriverFilter(newSelection)
  }

  const handleTrainSelect = (train: string) => {
    const newSelection = selectedTrains.includes(train)
      ? selectedTrains.filter((t) => t !== train)
      : [...selectedTrains, train]
    setSelectedTrains(newSelection)
    onTrainFilter(newSelection)
  }

  const clearAllFilters = () => {
    setSelectedDrivers([])
    setSelectedTrains([])
    setSearchTerm("")
    onDriverFilter([])
    onTrainFilter([])
    onSearchChange("")
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    onSearchChange(value)
  }

  const activeFiltersCount = selectedDrivers.length + selectedTrains.length + (searchTerm ? 1 : 0)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Filters & Controls</CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Filters
              {activeFiltersCount > 0 && (
                <Badge variant="secondary" className="ml-1">
                  {activeFiltersCount}
                </Badge>
              )}
            </Button>
            <Button variant="outline" size="sm" onClick={onRefresh} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
            <Button variant="outline" size="sm" onClick={onExport}>
              <Download className="w-4 h-4" />
            </Button>
            {/* Solution Upload */}
            <div className="ml-2">
              <SolutionUpload onUpload={onRefresh} />
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search drivers, trains, or destinations..."
            value={searchTerm}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Expandable Filters */}
        {showFilters && (
          <div className="space-y-4 animate-in slide-in-from-top-2 duration-200">
            {/* Driver Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Filter by Drivers:</label>
              <div className="flex flex-wrap gap-2">
                {drivers.map((driver) => (
                  <Badge
                    key={driver}
                    variant={selectedDrivers.includes(driver) ? "default" : "outline"}
                    className="cursor-pointer hover:bg-primary/80 transition-colors"
                    onClick={() => handleDriverSelect(driver)}
                  >
                    {driver}
                    {selectedDrivers.includes(driver) && <X className="w-3 h-3 ml-1" />}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Train Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Filter by Trains:</label>
              <div className="flex flex-wrap gap-2">
                {trains.map((train) => (
                  <Badge
                    key={train}
                    variant={selectedTrains.includes(train) ? "default" : "outline"}
                    className="cursor-pointer hover:bg-primary/80 transition-colors"
                    onClick={() => handleTrainSelect(train)}
                  >
                    {train}
                    {selectedTrains.includes(train) && <X className="w-3 h-3 ml-1" />}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Clear Filters */}
            {activeFiltersCount > 0 && (
              <Button variant="outline" size="sm" onClick={clearAllFilters} className="w-full bg-transparent">
                Clear All Filters ({activeFiltersCount})
              </Button>
            )}
          </div>
        )}

        {/* Active Filters Summary */}
        {activeFiltersCount > 0 && !showFilters && (
          <div className="flex flex-wrap gap-2">
            {searchTerm && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Search: "{searchTerm}"
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleSearchChange("")} />
              </Badge>
            )}
            {selectedDrivers.map((driver) => (
              <Badge key={driver} variant="secondary" className="flex items-center gap-1">
                Driver: {driver}
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleDriverSelect(driver)} />
              </Badge>
            ))}
            {selectedTrains.map((train) => (
              <Badge key={train} variant="secondary" className="flex items-center gap-1">
                Train: {train}
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleTrainSelect(train)} />
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
