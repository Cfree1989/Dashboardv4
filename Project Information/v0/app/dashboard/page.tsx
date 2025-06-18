"use client"

import { useState } from "react"
import { Dashboard } from "@/components/dashboard/dashboard"
import { DashboardProvider } from "@/components/dashboard/dashboard-context"
import type { JobStatus } from "@/types/job"

export default function DashboardPage() {
  const [currentStatus, setCurrentStatus] = useState<JobStatus>("UPLOADED")

  return (
    <DashboardProvider>
      <div className="min-h-screen bg-gray-50">
        <Dashboard currentStatus={currentStatus} onStatusChange={setCurrentStatus} />
      </div>
    </DashboardProvider>
  )
}
