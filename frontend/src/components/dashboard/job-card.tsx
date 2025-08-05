import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ApprovalModal, RejectionModal, StatusUpdateModal } from './modals';
import { useAuthStatus } from '@/lib/auth-middleware';
import { apiClient } from '@/lib/api-client';

interface JobCardProps {
  id: string;
  studentName: string;
  projectTitle: string;
  status: 'UPLOADED' | 'PENDING' | 'READYTOPRINT' | 'PRINTING' | 'COMPLETED' | 'PAIDPICKEDUP' | 'REJECTED' | 'ARCHIVED';
  fileName: string;
  submittedAt: string;
  estimatedCost?: number;
  onRefresh?: () => void;
}

export function JobCard({ 
  id, 
  studentName, 
  projectTitle, 
  status, 
  fileName, 
  submittedAt,
  estimatedCost,
  onRefresh
}: JobCardProps) {
  const { staffName } = useAuthStatus();
  
  // Modal state
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [rejectionModalOpen, setRejectionModalOpen] = useState(false);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [statusAction, setStatusAction] = useState<'printing' | 'complete' | 'picked-up'>('printing');

  // Job data for modals
  const jobData = {
    id,
    studentName,
    projectTitle,
    status,
    fileName,
    submittedAt,
    estimatedCost
  };

  // API handlers
  const handleApprove = async (data: {
    weight_g: number;
    time_hours: number;
    authoritative_file: string;
  }) => {
    if (!staffName) throw new Error('Staff name is required');
    
    await apiClient.approveJob(id, {
      ...data,
      staff_name: staffName
    });
    
    onRefresh?.();
  };

  const handleReject = async (data: {
    reasons: string[];
    custom_reason?: string;
  }) => {
    if (!staffName) throw new Error('Staff name is required');
    
    await apiClient.rejectJob(id, {
      ...data,
      staff_name: staffName
    });
    
    onRefresh?.();
  };

  const handleStatusUpdate = async (data: any) => {
    if (!staffName) throw new Error('Staff name is required');
    
    const statusData = {
      ...data,
      staff_name: staffName
    };

    switch (statusAction) {
      case 'printing':
        await apiClient.markJobPrinting(id, statusData);
        break;
      case 'complete':
        await apiClient.markJobComplete(id, statusData);
        break;
      case 'picked-up':
        await apiClient.markJobPickedUp(id, statusData);
        break;
    }
    
    onRefresh?.();
  };

  // Button handlers
  const handleReviewClick = () => {
    // For UPLOADED jobs, show both approve and reject options
    setApprovalModalOpen(true);
  };

  const handleMarkPrintingClick = () => {
    setStatusAction('printing');
    setStatusModalOpen(true);
  };

  const handleMarkCompleteClick = () => {
    setStatusAction('complete');
    setStatusModalOpen(true);
  };

  const handleMarkPickedUpClick = () => {
    setStatusAction('picked-up');
    setStatusModalOpen(true);
  };

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
              <>
                <Button size="sm" variant="outline" onClick={handleReviewClick}>
                  Review
                </Button>
                <Button 
                  size="sm" 
                  variant="destructive" 
                  onClick={() => setRejectionModalOpen(true)}
                >
                  Reject
                </Button>
              </>
            )}
            {status === 'READYTOPRINT' && (
              <Button size="sm" onClick={handleMarkPrintingClick}>
                Mark Printing
              </Button>
            )}
            {status === 'PRINTING' && (
              <Button size="sm" onClick={handleMarkCompleteClick}>
                Mark Complete
              </Button>
            )}
            {status === 'COMPLETED' && (
              <Button size="sm" variant="outline" onClick={handleMarkPickedUpClick}>
                Mark Picked Up
              </Button>
            )}
          </div>
        </div>
      </CardContent>

      {/* Modals */}
      <ApprovalModal
        isOpen={approvalModalOpen}
        onClose={() => setApprovalModalOpen(false)}
        job={jobData}
        onApprove={handleApprove}
      />

      <RejectionModal
        isOpen={rejectionModalOpen}
        onClose={() => setRejectionModalOpen(false)}
        job={jobData}
        onReject={handleReject}
      />

      <StatusUpdateModal
        isOpen={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        job={jobData}
        action={statusAction}
        onUpdate={handleStatusUpdate}
      />
    </Card>
  );
}