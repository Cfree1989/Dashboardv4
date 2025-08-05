'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface SubmissionFormProps {
  onSubmit?: (data: FormData) => void;
}

export function SubmissionForm({ onSubmit }: SubmissionFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    const formData = new FormData(e.currentTarget);
    
    try {
      if (onSubmit) {
        await onSubmit(formData);
      } else {
        // TODO: Implement API call to backend
        console.log('Form data:', Object.fromEntries(formData));
        alert('Form submitted! (Backend integration needed)');
      }
    } catch (error) {
      console.error('Submission error:', error);
      alert('Submission failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClear = () => {
    const form = document.getElementById('submission-form') as HTMLFormElement;
    form?.reset();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Submission Form</CardTitle>
        <CardDescription>
          Fill out all required fields to submit your 3D print request
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form id="submission-form" onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="studentName">Student Name *</Label>
              <Input
                id="studentName"
                name="studentName"
                placeholder="Enter your full name"
                required
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="studentEmail">Email Address *</Label>
              <Input
                id="studentEmail"
                name="studentEmail"
                type="email"
                placeholder="your.email@university.edu"
                required
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="projectTitle">Project Title *</Label>
            <Input
              id="projectTitle"
              name="projectTitle"
              placeholder="Brief title for your 3D print project"
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="file">3D Model File *</Label>
            <Input
              id="file"
              name="file"
              type="file"
              accept=".stl,.obj,.3mf,.gcode"
              required
              disabled={isSubmitting}
            />
            <p className="text-sm text-muted-foreground">
              Supported formats: STL, OBJ, 3MF, G-code (max 50MB)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea
              id="notes"
              name="notes"
              placeholder="Any special requirements, colors, or instructions..."
              rows={4}
              disabled={isSubmitting}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="infillPercentage">Infill Percentage</Label>
              <Input
                id="infillPercentage"
                name="infillPercentage"
                type="number"
                placeholder="20"
                min="0"
                max="100"
                disabled={isSubmitting}
              />
              <p className="text-sm text-muted-foreground">
                Leave blank for default (20%)
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="layerHeight">Layer Height (mm)</Label>
              <Input
                id="layerHeight"
                name="layerHeight"
                type="number"
                step="0.01"
                placeholder="0.2"
                min="0.1"
                max="0.3"
                disabled={isSubmitting}
              />
              <p className="text-sm text-muted-foreground">
                Leave blank for default (0.2mm)
              </p>
            </div>
          </div>

          <div className="flex gap-3 pt-6">
            <Button 
              type="submit" 
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Print Job'}
            </Button>
            <Button 
              type="button" 
              variant="outline"
              onClick={handleClear}
              disabled={isSubmitting}
            >
              Clear Form
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}