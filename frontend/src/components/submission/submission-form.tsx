'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient, ApiClientError } from '@/lib/api-client';

interface SubmissionResponse {
  message: string;
  job: {
    id: string;
    display_name: string;
    status: string;
    created_at: string;
    estimated_cost: string;
  };
}

interface SubmissionFormProps {
  onSuccess?: (jobData: SubmissionResponse['job']) => void;
}

export function SubmissionForm({ onSuccess }: SubmissionFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [printMethod, setPrintMethod] = useState<string>('');
  const [formData, setFormData] = useState({
    student_name: '',
    student_email: '',
    discipline: '',
    class_number: '',
    printer: '',
    color: '',
    material: '',
    acknowledged_minimum_charge: 'false',
  });

  // Color options based on print method
  const filamentColors = [
    'True Red', 'True Orange', 'Light Orange', 'True Yellow', 'Dark Yellow',
    'Lime Green', 'Green', 'Forest Green', 'Blue', 'Electric Blue',
    'Midnight Purple', 'Light Purple', 'Clear', 'True White', 'Gray',
    'True Black', 'Brown', 'Copper', 'Bronze', 'True Silver',
    'True Gold', 'Glow in the Dark', 'Color Changing'
  ];
  
  const resinColors = ['Black', 'White', 'Gray', 'Clear'];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (field === 'material') {
      setPrintMethod(value);
      // Reset color when material changes
      setFormData(prev => ({ ...prev, color: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const submitFormData = new FormData(e.currentTarget);
    
    try {
      const response = await apiClient.upload<SubmissionResponse>('/submit', submitFormData);
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess(response.job);
      }
      
    } catch (error) {
      console.error('Submission error:', error);
      if (error instanceof ApiClientError) {
        setError(error.message);
      } else {
        setError('Submission failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClear = () => {
    const form = document.getElementById('submission-form') as HTMLFormElement;
    form?.reset();
    setFormData({
      student_name: '',
      student_email: '',
      discipline: '',
      class_number: '',
      printer: '',
      color: '',
      material: '',
      acknowledged_minimum_charge: 'false',
    });
    setPrintMethod('');
    setError(null);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit 3D Print Job</CardTitle>
        <CardDescription>
          Fill out all required fields to submit your 3D print request
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Mandatory Warning Text */}
        <Alert className="border-orange-200 bg-orange-50">
          <AlertDescription className="text-sm">
            <strong>Important Notice:</strong> Before submitting your model for 3D printing, please ensure you have thoroughly reviewed our Additive Manufacturing Moodle page, read all the guides, and checked the checklist. If necessary, revisit and fix your model before submission. Your model must be scaled and simplified appropriately, often requiring a second version specifically optimized for 3D printing. We will not print models that are broken, messy, or too large. Your model must follow the rules and constraints of the machine. We will not fix or scale your model as we do not know your specific needs or project requirements. We print exactly what you send us; if the scale is wrong or you are unsatisfied with the product, it is your responsibility. We will gladly print another model for you at an additional cost. We are only responsible for print failures due to issues under our control.
          </AlertDescription>
        </Alert>

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <form id="submission-form" onSubmit={handleSubmit} className="space-y-4">
          {/* Student Information */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="student_name">Student Name *</Label>
              <Input
                id="student_name"
                name="student_name"
                placeholder="Enter your full name"
                value={formData.student_name}
                onChange={(e) => handleInputChange('student_name', e.target.value)}
                required
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="student_email">Email Address *</Label>
              <Input
                id="student_email"
                name="student_email"
                type="email"
                placeholder="your.email@university.edu"
                value={formData.student_email}
                onChange={(e) => handleInputChange('student_email', e.target.value)}
                required
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Academic Information */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="discipline">Discipline *</Label>
              <Select
                name="discipline"
                value={formData.discipline}
                onValueChange={(value) => handleInputChange('discipline', value)}
                disabled={isSubmitting}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your discipline" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Art">Art</SelectItem>
                  <SelectItem value="Architecture">Architecture</SelectItem>
                  <SelectItem value="Landscape Architecture">Landscape Architecture</SelectItem>
                  <SelectItem value="Interior Design">Interior Design</SelectItem>
                  <SelectItem value="Engineering">Engineering</SelectItem>
                  <SelectItem value="Hobby/Personal">Hobby/Personal</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="class_number">Class Number *</Label>
              <Input
                id="class_number"
                name="class_number"
                placeholder="ARCH 4000 or N/A"
                value={formData.class_number}
                onChange={(e) => handleInputChange('class_number', e.target.value)}
                required
                disabled={isSubmitting}
              />
              <p className="text-xs text-muted-foreground">
                Enter course code or "N/A" if not for a class
              </p>
            </div>
          </div>

          {/* Print Method and Material */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="material">Print Method *</Label>
              <Select
                name="material"
                value={formData.material}
                onValueChange={(value) => handleInputChange('material', value)}
                disabled={isSubmitting}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select print method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="filament">
                    <div>
                      <div className="font-medium">Filament</div>
                      <div className="text-xs text-muted-foreground">Good resolution, suitable for simpler models. Fast. Best For: Medium items. Cost: Least expensive.</div>
                    </div>
                  </SelectItem>
                  <SelectItem value="resin">
                    <div>
                      <div className="font-medium">Resin</div>
                      <div className="text-xs text-muted-foreground">Super high resolution and detail. Slow. Best For: Small items. Cost: More expensive.</div>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Color Selection - Dynamic based on material */}
            <div className="space-y-2">
              <Label htmlFor="color">Color Preference *</Label>
              <Select
                name="color"
                value={formData.color}
                onValueChange={(value) => handleInputChange('color', value)}
                disabled={isSubmitting || !printMethod}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder={printMethod ? "Select color" : "Select print method first"} />
                </SelectTrigger>
                <SelectContent>
                  {printMethod === 'filament' && filamentColors.map(color => (
                    <SelectItem key={color} value={color}>{color}</SelectItem>
                  ))}
                  {printMethod === 'resin' && resinColors.map(color => (
                    <SelectItem key={color} value={color}>{color}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Printer Dimensions Information */}
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Printer Dimensions - Will your model fit?</h4>
              <div className="text-sm text-blue-800 space-y-2">
                <p><strong>Filament Printers:</strong></p>
                <ul className="ml-4 space-y-1">
                  <li>• Prusa MK4S: 9.84" × 8.3" × 8.6" (250 × 210 × 220 mm)</li>
                  <li>• Prusa XL: 14.17" × 14.17" × 14.17" (360 × 360 × 360 mm)</li>
                  <li>• Raise3D Pro 2 Plus: 12" × 12" × 23.8" (305 × 305 × 605 mm)</li>
                </ul>
                <p><strong>Resin Printers:</strong></p>
                <ul className="ml-4 space-y-1">
                  <li>• Formlabs Form 3: 5.7" × 5.7" × 7.3" (145 × 145 × 175 mm)</li>
                </ul>
                <p className="text-xs">
                  <strong>Important:</strong> If exporting as .STL or .OBJ you MUST scale it down in millimeters BEFORE exporting. If you do not the scale will not work correctly.
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="printer">Printer Selection *</Label>
              <Select
                name="printer"
                value={formData.printer}
                onValueChange={(value) => handleInputChange('printer', value)}
                disabled={isSubmitting}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Which printer fits your model?" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Prusa MK4S">Prusa MK4S</SelectItem>
                  <SelectItem value="Prusa XL">Prusa XL</SelectItem>
                  <SelectItem value="Raise3D Pro 2 Plus">Raise3D Pro 2 Plus</SelectItem>
                  <SelectItem value="Formlabs Form 3">Formlabs Form 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <Label htmlFor="file">3D Model File *</Label>
            <Input
              id="file"
              name="file"
              type="file"
              accept=".stl,.obj,.3mf"
              required
              disabled={isSubmitting}
            />
            <p className="text-sm text-muted-foreground">
              Supported formats: STL, OBJ, 3MF (max 50MB)
            </p>
          </div>

          {/* Minimum Charge Acknowledgment */}
          <div className="space-y-2">
            <Label htmlFor="acknowledged_minimum_charge">Minimum Charge Consent *</Label>
            <Select
              name="acknowledged_minimum_charge"
              value={formData.acknowledged_minimum_charge}
              onValueChange={(value) => handleInputChange('acknowledged_minimum_charge', value)}
              disabled={isSubmitting}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Select your response" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="true">Yes - I understand there is a minimum $3.00 charge</SelectItem>
                <SelectItem value="false">No - I do not agree to the minimum charge</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              You must acknowledge the minimum $3.00 charge for all print jobs. The final cost may be higher based on material and time.
            </p>
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-3 pt-6">
            <Button 
              type="submit" 
              className="flex-1"
              disabled={isSubmitting || formData.acknowledged_minimum_charge !== 'true'}
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