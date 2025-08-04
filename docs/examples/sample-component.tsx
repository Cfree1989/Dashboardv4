// Sample React Component - Job Approval Modal
/**
 * This example demonstrates standard patterns for React components in the 3D Print Management System.
 * Key patterns: TypeScript interfaces, shadcn/ui components, form validation, API integration, loading states.
 */

import React, { useState, useEffect } from 'react';
import { Job, ApprovalParams, Staff } from '@/types/job';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle } from 'lucide-react';
import { approveJob, getCandidateFiles, getStaffList } from '@/lib/api';
import { z } from 'zod';

// TypeScript interfaces for props and form data
interface ApprovalModalProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (updatedJob: Job) => void;
}

interface FormData {
  weight_g: string;
  time_hours: string;
  staff_name: string;
  authoritative_file: string;
}

interface ValidationErrors {
  [key: string]: string[];
}

// Zod schema for form validation
const approvalSchema = z.object({
  weight_g: z.number().min(0.1, "Weight must be at least 0.1g").max(1000, "Weight cannot exceed 1000g"),
  time_hours: z.number().min(0.1, "Time must be at least 0.1 hours").max(100, "Time cannot exceed 100 hours"),
  staff_name: z.string().min(1, "Staff member selection is required"),
  authoritative_file: z.string().min(1, "File selection is required")
});

export function ApprovalModal({ job, isOpen, onClose, onSuccess }: ApprovalModalProps) {
  // State management with meaningful variable names
  const [formData, setFormData] = useState<FormData>({
    weight_g: '',
    time_hours: '',
    staff_name: '',
    authoritative_file: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [candidateFiles, setCandidateFiles] = useState<string[]>([]);
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [calculatedCost, setCalculatedCost] = useState<number>(0);

  // Load candidate files and staff list when modal opens
  useEffect(() => {
    if (isOpen && job) {
      loadModalData();
    }
  }, [isOpen, job]);

  // Calculate cost when weight or material changes
  useEffect(() => {
    if (formData.weight_g && job) {
      const weight = parseFloat(formData.weight_g);
      if (!isNaN(weight)) {
        const baseCost = job.material === 'filament' ? weight * 0.10 : weight * 0.20;
        setCalculatedCost(Math.max(baseCost, 3.00));
      }
    }
  }, [formData.weight_g, job?.material]);

  const loadModalData = async () => {
    if (!job) return;
    
    setIsLoadingFiles(true);
    try {
      // Load candidate files and staff list in parallel
      const [filesResponse, staffResponse] = await Promise.all([
        getCandidateFiles(job.id),
        getStaffList()
      ]);
      
      setCandidateFiles(filesResponse.files);
      setStaffList(staffResponse.staff);
      
      // Pre-select the most recent non-original file if available
      const nonOriginalFiles = filesResponse.files.filter(
        file => file !== job.original_filename
      );
      if (nonOriginalFiles.length > 0) {
        setFormData(prev => ({
          ...prev,
          authoritative_file: nonOriginalFiles[0]
        }));
      }
    } catch (error) {
      console.error('Failed to load modal data:', error);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  const handleInputChange = (field: keyof FormData) => (value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({
        ...prev,
        [field]: []
      }));
    }
  };

  const validateForm = (): boolean => {
    try {
      // Parse form data for validation
      const parsedData = {
        weight_g: parseFloat(formData.weight_g),
        time_hours: parseFloat(formData.time_hours),
        staff_name: formData.staff_name,
        authoritative_file: formData.authoritative_file
      };

      // Validate with Zod schema
      approvalSchema.parse(parsedData);
      setValidationErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors: ValidationErrors = {};
        error.errors.forEach(err => {
          const field = err.path[0] as string;
          if (!errors[field]) errors[field] = [];
          errors[field].push(err.message);
        });
        setValidationErrors(errors);
      }
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!job || !validateForm()) {
      // Scroll to first error
      const firstErrorField = Object.keys(validationErrors)[0];
      if (firstErrorField) {
        const element = document.querySelector(`[name="${firstErrorField}"]`);
        element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    setIsSubmitting(true);
    try {
      const approvalParams: ApprovalParams = {
        weight_g: parseFloat(formData.weight_g),
        time_hours: parseFloat(formData.time_hours),
        staff_name: formData.staff_name,
        authoritative_file: formData.authoritative_file
      };

      const updatedJob = await approveJob(job.id, approvalParams);
      onSuccess(updatedJob);
      onClose();
      
      // Reset form for next use
      setFormData({
        weight_g: '',
        time_hours: '',
        staff_name: '',
        authoritative_file: ''
      });
    } catch (error: any) {
      // Handle API errors
      if (error.status === 400 && error.data?.details) {
        setValidationErrors(error.data.details);
      } else {
        // Show generic error
        setValidationErrors({
          submit: [error.message || 'An unexpected error occurred']
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      weight_g: '',
      time_hours: '',
      staff_name: '',
      authoritative_file: ''
    });
    setValidationErrors({});
    onClose();
  };

  if (!job) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleCancel}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Approve Print Job</DialogTitle>
        </DialogHeader>

        {/* Loading state for file data */}
        {isLoadingFiles && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            <span>Loading job files...</span>
          </div>
        )}

        {/* Form content */}
        {!isLoadingFiles && (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Job info display */}
            <div className="bg-gray-50 p-3 rounded-md">
              <p className="text-sm font-medium">{job.display_name}</p>
              <p className="text-sm text-gray-600">
                {job.student_name} • {job.material} • {job.color}
              </p>
            </div>

            {/* Authoritative file selection */}
            <div className="space-y-2">
              <Label htmlFor="file-selection">Select File to Print</Label>
              <RadioGroup
                value={formData.authoritative_file}
                onValueChange={handleInputChange('authoritative_file')}
              >
                {candidateFiles.map((file) => (
                  <div key={file} className="flex items-center space-x-2">
                    <RadioGroupItem value={file} id={file} />
                    <Label htmlFor={file} className="text-sm">
                      {file}
                      {file === job.original_filename && (
                        <span className="text-gray-500 ml-1">(original)</span>
                      )}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
              {validationErrors.authoritative_file && (
                <p className="text-sm text-red-600">{validationErrors.authoritative_file[0]}</p>
              )}
            </div>

            {/* Weight input */}
            <div className="space-y-2">
              <Label htmlFor="weight">Weight (grams)</Label>
              <Input
                id="weight"
                name="weight_g"
                type="number"
                step="0.1"
                min="0.1"
                max="1000"
                value={formData.weight_g}
                onChange={(e) => handleInputChange('weight_g')(e.target.value)}
                className={validationErrors.weight_g ? 'border-red-500' : ''}
              />
              {validationErrors.weight_g && (
                <p className="text-sm text-red-600">{validationErrors.weight_g[0]}</p>
              )}
            </div>

            {/* Time input */}
            <div className="space-y-2">
              <Label htmlFor="time">Print Time (hours)</Label>
              <Input
                id="time"
                name="time_hours"
                type="number"
                step="0.1"
                min="0.1"
                max="100"
                value={formData.time_hours}
                onChange={(e) => handleInputChange('time_hours')(e.target.value)}
                className={validationErrors.time_hours ? 'border-red-500' : ''}
              />
              {validationErrors.time_hours && (
                <p className="text-sm text-red-600">{validationErrors.time_hours[0]}</p>
              )}
            </div>

            {/* Staff attribution */}
            <div className="space-y-2">
              <Label htmlFor="staff">Performing Action As</Label>
              <Select
                value={formData.staff_name}
                onValueChange={handleInputChange('staff_name')}
              >
                <SelectTrigger className={validationErrors.staff_name ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Select staff member" />
                </SelectTrigger>
                <SelectContent>
                  {staffList.map((staff) => (
                    <SelectItem key={staff.name} value={staff.name}>
                      {staff.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {validationErrors.staff_name && (
                <p className="text-sm text-red-600">{validationErrors.staff_name[0]}</p>
              )}
            </div>

            {/* Calculated cost display */}
            {calculatedCost > 0 && (
              <div className="bg-blue-50 p-3 rounded-md">
                <p className="text-sm font-medium">
                  Calculated Cost: ${calculatedCost.toFixed(2)}
                  {calculatedCost === 3.00 && (
                    <span className="text-gray-600 ml-1">(minimum charge)</span>
                  )}
                </p>
              </div>
            )}

            {/* General error display */}
            {validationErrors.submit && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{validationErrors.submit[0]}</AlertDescription>
              </Alert>
            )}
          </form>
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            onClick={handleSubmit}
            disabled={isSubmitting || isLoadingFiles || !formData.staff_name}
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Approve Job
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}