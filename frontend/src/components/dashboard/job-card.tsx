import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface JobCardProps {
  id: string;
  studentName: string;
  projectTitle: string;
  status: 'UPLOADED' | 'PENDING' | 'READYTOPRINT' | 'PRINTING' | 'COMPLETED' | 'PAIDPICKEDUP' | 'REJECTED' | 'ARCHIVED';
  fileName: string;
  submittedAt: string;
  estimatedCost?: number;
}

export function JobCard({ 
  id, 
  studentName, 
  projectTitle, 
  status, 
  fileName, 
  submittedAt,
  estimatedCost 
}: JobCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'UPLOADED': return 'bg-blue-100 text-blue-800';
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'READYTOPRINT': return 'bg-green-100 text-green-800';
      case 'PRINTING': return 'bg-purple-100 text-purple-800';
      case 'COMPLETED': return 'bg-indigo-100 text-indigo-800';
      case 'PAIDPICKEDUP': return 'bg-emerald-100 text-emerald-800';
      case 'REJECTED': return 'bg-red-100 text-red-800';
      case 'ARCHIVED': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'UPLOADED': return 'New Upload';
      case 'PENDING': return 'Pending Approval';
      case 'READYTOPRINT': return 'Ready to Print';
      case 'PRINTING': return 'Printing';
      case 'COMPLETED': return 'Completed';
      case 'PAIDPICKEDUP': return 'Picked Up';
      case 'REJECTED': return 'Rejected';
      case 'ARCHIVED': return 'Archived';
      default: return status;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{projectTitle}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              by {studentName} • {fileName}
            </p>
          </div>
          <Badge className={getStatusColor(status)}>
            {getStatusDisplay(status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            <p>Job ID: {id}</p>
            <p>Submitted: {submittedAt}</p>
            {estimatedCost && (
              <p>Estimated Cost: ${estimatedCost.toFixed(2)}</p>
            )}
          </div>
          <div className="flex gap-2">
            {status === 'UPLOADED' && (
              <Button size="sm" variant="outline">
                Review
              </Button>
            )}
            {status === 'READYTOPRINT' && (
              <Button size="sm">
                Mark Printing
              </Button>
            )}
            {status === 'PRINTING' && (
              <Button size="sm">
                Mark Complete
              </Button>
            )}
            {status === 'COMPLETED' && (
              <Button size="sm" variant="outline">
                Mark Picked Up
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}