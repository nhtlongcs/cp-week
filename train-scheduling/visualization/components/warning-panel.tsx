
"use client"
import React from "react"

import type { Warning } from "@/types/schedule"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, Clock, Users, XCircle } from "lucide-react"
import { ChevronDown, ChevronRight } from "lucide-react"

interface WarningPanelProps {
  warnings: Warning[]
  driverWarnings: { driver: string; warnings: Warning[] }[]
}

export function WarningPanel({ warnings, driverWarnings }: WarningPanelProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "high":
        return <XCircle className="w-4 h-4 text-red-500" />
      case "medium":
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case "low":
        return <Clock className="w-4 h-4 text-blue-500" />
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-500" />
    }
  }

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

  const allWarnings = [
    ...warnings,
    ...driverWarnings.flatMap((dw) => dw.warnings.map((w) => ({ ...w, driver: dw.driver }))),
  ]

  const warningsByType = allWarnings.reduce(
    (acc, warning) => {
      if (!acc[warning.type]) acc[warning.type] = []
      acc[warning.type].push(warning)
      return acc
    },
    {} as Record<string, any[]>,
  )

  const criticalWarnings = allWarnings.filter((w) => w.severity === "high")

  if (allWarnings.length === 0) {
    return (
      <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-sm font-medium">All systems operational - No warnings detected</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  // State for expanded summary cards
  const [expanded, setExpanded] = React.useState<{ [key: string]: boolean }>({})

  // Helper to toggle expand/collapse
  const toggleExpand = (key: string) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  // Helper to render chevron icon
  const ChevronIcon = ({ open }: { open: boolean }) => (
    open ? <ChevronDown className="w-4 h-4 transition-transform" /> : <ChevronRight className="w-4 h-4 transition-transform" />
  )

  return (
    <div className="space-y-4">
      {/* Critical Warnings Alert */}
      {criticalWarnings.length > 0 && (
        <Alert className="border-red-500 bg-red-50 dark:bg-red-950/20">
          <XCircle className="h-4 w-4 text-red-500" />
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-medium text-red-700 dark:text-red-300">
                {criticalWarnings.length} Critical Warning{criticalWarnings.length > 1 ? "s" : ""} Detected
              </p>
              <div className="space-y-1">
                {criticalWarnings.slice(0, 3).map((warning, index) => (
                  <p key={index} className="text-sm text-red-600 dark:text-red-400">
                    • {warning.message}
                    {"driver" in warning && ` (Driver: ${warning.driver})`}
                  </p>
                ))}
                {criticalWarnings.length > 3 && (
                  <p className="text-sm text-red-600 dark:text-red-400">
                    ... and {criticalWarnings.length - 3} more critical warnings
                  </p>
                )}
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Expandable Warning Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Overtime Violations Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"> 
            <div className="flex items-center gap-2">
              <CardTitle className="text-sm font-medium">Overtime Violations</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{warningsByType.overtime?.length || 0}</div>
            <p className="text-xs text-muted-foreground">Drivers exceeding 9-hour limit</p>
          </CardContent>
        </Card>

        {/* Break Violations Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"> 
            <div className="flex items-center gap-2">
              <CardTitle className="text-sm font-medium">Break Violations</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {(warningsByType.no_break?.length || 0) + (warningsByType.late_break?.length || 0)}
            </div>
            <p className="text-xs text-muted-foreground">Missing or late breaks</p>
          </CardContent>
        </Card>

        {/* Schedule Conflicts Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"> 
            <div className="flex items-center gap-2">
              <CardTitle className="text-sm font-medium">Schedule Conflicts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {(warningsByType.overlap?.length || 0) + (warningsByType.no_driver?.length || 0)}
            </div>
            <p className="text-xs text-muted-foreground">Overlaps and missing drivers</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Warning List */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 cursor-pointer" onClick={() => toggleExpand("details")}> 
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Warning Details
            </CardTitle>
            <button
              type="button"
              aria-label={expanded["details"] ? "Collapse details" : "Expand details"}
              className="ml-2 focus:outline-none"
              onClick={e => { e.stopPropagation(); toggleExpand("details") }}
            >
              <ChevronIcon open={!!expanded["details"]} />
            </button>
          </CardHeader>
          <CardContent>
            {expanded["details"] && (
              <div className="space-y-3">
                {Object.entries(warningsByType).map(([type, typeWarnings]) => (
                  <div key={type} className="space-y-2">
                    <div
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => toggleExpand(`type-${type}`)}
                    >
                      <h4 className="font-medium text-sm capitalize flex items-center gap-2">
                        {getSeverityIcon(typeWarnings[0].severity)}
                        {type.replace("_", " ")} ({typeWarnings.length})
                      </h4>
                      <ChevronIcon open={!!expanded[`type-${type}`]} />
                    </div>
                    {expanded[`type-${type}`] && (
                      <div className="space-y-1 ml-6 mt-2">
                        {typeWarnings.map((warning, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">
                              {warning.message}
                              {"driver" in warning && ` (${warning.driver})`}
                            </span>
                            <Badge variant={getSeverityColor(warning.severity)} className="text-xs">
                              {warning.severity}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
    </div>
  )
}
