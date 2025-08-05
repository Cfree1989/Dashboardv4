import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { useAuthStatus } from '@/lib/auth-middleware';

interface Job {
  id: string;
  studentName: string;
  projectTitle: string;
  status: string;
  fileName: string;
  submittedAt: string;
  estimatedCost?: number;
}

interface RejectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job | null;
  onReject: (data: {
    reasons: string[];
    custom_reason?: string;
  }) => Promise<void>;
}

// Common rejection reasons
const REJECTION_REASONS = [
  'File is not printable (geometry issues)',
  'Insufficient support material',
  'Print too large for available printers', 
  'Inappropriate material choice',
  'File resolution too low',
  'Missing required information',
  'Violates safety guidelines',
  'Copyright or licensing concerns',
  'Exceeds project complexity limits',
  'Student needs to revise design'
];

export function RejectionModal({ isOpen, onClose, job, onReject }: RejectionModalProps) {
  const { staffName } = useAuthStatus();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [selectedReasons, setSelectedReasons] = useState<string[]>([]);
  const [customReason, setCustomReason] = useState('');

  const handleReasonToggle = (reason: string) => {
    setSelectedReasons(prev => 
      prev.includes(reason) 
        ? prev.filter(r => r !== reason)
        : [...prev, reason]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!job || !staffName) return;
    
    // Validate form
    if (selectedReasons.length === 0 && !customReason.trim()) {
      setError('At least one rejection reason is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await onReject({
        reasons: selectedReasons,
        custom_reason: customReason.trim() || undefined,
      });
      
      // Reset form
      setSelectedReasons([]);
      setCustomReason('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject job');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setSelectedReasons([]);
      setCustomReason('');
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Reject Job Submission</DialogTitle>
          <DialogDescription>
            Select rejection reasons to provide feedback to the student.
          </DialogDescription>
        </DialogHeader>

        {job && (
          <div className="space-y-4">
            {/* Job Details */}
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <h4 className="font-semibold text-sm">Job Details</h4>
              <div className="text-sm space-y-1">
                <p><strong>Student:</strong> {job.studentName}</p>
                <p><strong>Project:</strong> {job.projectTitle}</p>
                <p><strong>File:</strong> {job.fileName}</p>
                <p><strong>Submitted:</strong> {job.submittedAt}</p>
              </div>
            </div>

            {/* Rejection Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Common Rejection Reasons</Label>
                <div className="mt-2 space-y-2 max-h-48 overflow-y-auto">
                  {REJECTION_REASONS.map((reason) => (
                    <label
                      key={reason}
                      className="flex items-center space-x-2 cursor-pointer p-2 hover:bg-gray-50 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedReasons.includes(reason)}
                        onChange={() => handleReasonToggle(reason)}
                        disabled={loading}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">{reason}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <Label htmlFor="custom-reason">Additional Comments (Optional)</Label>
                <Textarea
                  id="custom-reason"
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  placeholder="Provide specific feedback or additional details..."
                  disabled={loading}
                  rows={3}
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleClose}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={loading}
                  variant="destructive"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Reject Job
                </Button>
              </DialogFooter>
            </form>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}