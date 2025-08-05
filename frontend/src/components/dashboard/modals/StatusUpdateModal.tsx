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
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
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

type StatusAction = 'printing' | 'complete' | 'picked-up';

interface StatusUpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job | null;
  action: StatusAction;
  onUpdate: (data: any) => Promise<void>;
}

// Available printers for marking as printing
const AVAILABLE_PRINTERS = [
  'Ultimaker S3',
  'Prusa i3 MK3S+',
  'Bambu Lab X1-Carbon',
  'Formlabs Form 3',
  'Ender 3 V2',
];

export function StatusUpdateModal({ isOpen, onClose, job, action, onUpdate }: StatusUpdateModalProps) {
  const { staffName } = useAuthStatus();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [printer, setPrinter] = useState('');
  const [notes, setNotes] = useState('');

  const getModalConfig = () => {
    switch (action) {
      case 'printing':
        return {
          title: 'Mark Job as Printing',
          description: 'Select the printer and start the printing process.',
          buttonText: 'Start Printing',
          buttonColor: 'bg-purple-600 hover:bg-purple-700',
        };
      case 'complete':
        return {
          title: 'Mark Job as Completed',
          description: 'Confirm that the print job has been completed successfully.',
          buttonText: 'Mark Complete',
          buttonColor: 'bg-blue-600 hover:bg-blue-700',
        };
      case 'picked-up':
        return {
          title: 'Mark Job as Picked Up',
          description: 'Confirm that the student has picked up their completed print.',
          buttonText: 'Mark Picked Up',
          buttonColor: 'bg-green-600 hover:bg-green-700',
        };
      default:
        return {
          title: 'Update Job Status',
          description: 'Update the job status.',
          buttonText: 'Update',
          buttonColor: 'bg-gray-600 hover:bg-gray-700',
        };
    }
  };

  const config = getModalConfig();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!job || !staffName) return;
    
    // Validate printer selection for printing action
    if (action === 'printing' && !printer) {
      setError('Please select a printer');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const data: any = {};
      
      if (action === 'printing') {
        data.printer = printer;
      }
      
      if (action === 'complete' && notes.trim()) {
        data.completion_notes = notes.trim();
      }
      
      await onUpdate(data);
      
      // Reset form
      setPrinter('');
      setNotes('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update job status');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setPrinter('');
      setNotes('');
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{config.title}</DialogTitle>
          <DialogDescription>
            {config.description}
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
                <p><strong>Current Status:</strong> {job.status}</p>
              </div>
            </div>

            {/* Update Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {action === 'printing' && (
                <div>
                  <Label htmlFor="printer">Select Printer</Label>
                  <Select value={printer} onValueChange={setPrinter} disabled={loading}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a printer..." />
                    </SelectTrigger>
                    <SelectContent>
                      {AVAILABLE_PRINTERS.map((printerName) => (
                        <SelectItem key={printerName} value={printerName}>
                          {printerName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {action === 'complete' && (
                <div>
                  <Label htmlFor="completion-notes">Completion Notes (Optional)</Label>
                  <Textarea
                    id="completion-notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Any notes about the completed print..."
                    disabled={loading}
                    rows={3}
                  />
                </div>
              )}

              {action === 'picked-up' && (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Please verify:</strong> The student has picked up their completed print 
                    and any payment has been processed if required.
                  </p>
                </div>
              )}

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
                  className={config.buttonColor}
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {config.buttonText}
                </Button>
              </DialogFooter>
            </form>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}