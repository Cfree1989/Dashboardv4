import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface JobCardProps {
  id: string;
  studentName: string;
  projectTitle: string;
  status: 'PENDING' | 'APPROVED' | 'PRINTING' | 'COMPLETED' | 'REJECTED';
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
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      case 'APPROVED': return 'bg-green-100 text-green-800';
      case 'PRINTING': return 'bg-blue-100 text-blue-800';
      case 'COMPLETED': return 'bg-purple-100 text-purple-800';
      case 'REJECTED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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
            {status}
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
            {status === 'PENDING' && (
              <>
                <Button size="sm" variant="outline">
                  Review
                </Button>
              </>
            )}
            {status === 'APPROVED' && (
              <Button size="sm">
                Mark Printing
              </Button>
            )}
            {status === 'PRINTING' && (
              <Button size="sm">
                Mark Complete
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}