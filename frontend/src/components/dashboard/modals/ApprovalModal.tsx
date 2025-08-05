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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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

interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job | null;
  onApprove: (data: {
    weight_g: number;
    time_hours: number;
    authoritative_file: string;
  }) => Promise<void>;
}

export function ApprovalModal({ isOpen, onClose, job, onApprove }: ApprovalModalProps) {
  const { staffName } = useAuthStatus();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [weight, setWeight] = useState('');
  const [timeHours, setTimeHours] = useState('');
  const [authoritativeFile, setAuthoritativeFile] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!job || !staffName) return;
    
    // Validate form
    const weightNum = parseFloat(weight);
    const timeNum = parseFloat(timeHours);
    
    if (isNaN(weightNum) || weightNum <= 0) {
      setError('Weight must be a positive number');
      return;
    }
    
    if (isNaN(timeNum) || timeNum <= 0) {
      setError('Time must be a positive number');
      return;
    }
    
    if (!authoritativeFile.trim()) {
      setError('Authoritative file is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await onApprove({
        weight_g: weightNum,
        time_hours: timeNum,
        authoritative_file: authoritativeFile.trim(),
      });
      
      // Reset form
      setWeight('');
      setTimeHours('');
      setAuthoritativeFile('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve job');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setWeight('');
      setTimeHours('');
      setAuthoritativeFile('');
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Approve Job for Printing</DialogTitle>
          <DialogDescription>
            Review and approve this job with printing specifications.
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

            {/* Approval Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="weight">Weight (grams)</Label>
                  <Input
                    id="weight"
                    type="number"
                    step="0.1"
                    min="0"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="0.0"
                    disabled={loading}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="time">Print Time (hours)</Label>
                  <Input
                    id="time"
                    type="number"
                    step="0.25"
                    min="0"
                    value={timeHours}
                    onChange={(e) => setTimeHours(e.target.value)}
                    placeholder="0.0"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="authoritative-file">Authoritative File</Label>
                <Input
                  id="authoritative-file"
                  value={authoritativeFile}
                  onChange={(e) => setAuthoritativeFile(e.target.value)}
                  placeholder="e.g., file_v2_optimized.stl"
                  disabled={loading}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">
                  The final file version that will be printed
                </p>
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
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Approve Job
                </Button>
              </DialogFooter>
            </form>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}