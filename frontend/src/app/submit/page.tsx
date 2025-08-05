import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export default function SubmitPage() {
  return (
    <div className="container mx-auto max-w-2xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Submit 3D Print Job</h1>
        <p className="text-muted-foreground">
          Upload your 3D model and provide job details
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Job Submission Form</CardTitle>
          <CardDescription>
            Fill out all required fields to submit your 3D print request
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <form className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="studentName">Student Name *</Label>
                <Input
                  id="studentName"
                  placeholder="Enter your full name"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="studentEmail">Email Address *</Label>
                <Input
                  id="studentEmail"
                  type="email"
                  placeholder="your.email@university.edu"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="projectTitle">Project Title *</Label>
              <Input
                id="projectTitle"
                placeholder="Brief title for your 3D print project"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="file">3D Model File *</Label>
              <Input
                id="file"
                type="file"
                accept=".stl,.obj,.3mf,.gcode"
                required
              />
              <p className="text-sm text-muted-foreground">
                Supported formats: STL, OBJ, 3MF, G-code (max 50MB)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                placeholder="Any special requirements, colors, or instructions..."
                rows={4}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="infillPercentage">Infill Percentage</Label>
                <Input
                  id="infillPercentage"
                  type="number"
                  placeholder="20"
                  min="0"
                  max="100"
                />
                <p className="text-sm text-muted-foreground">
                  Leave blank for default (20%)
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="layerHeight">Layer Height (mm)</Label>
                <Input
                  id="layerHeight"
                  type="number"
                  step="0.01"
                  placeholder="0.2"
                  min="0.1"
                  max="0.3"
                />
                <p className="text-sm text-muted-foreground">
                  Leave blank for default (0.2mm)
                </p>
              </div>
            </div>

            <div className="flex gap-3 pt-6">
              <Button type="submit" className="flex-1">
                Submit Print Job
              </Button>
              <Button type="button" variant="outline">
                Clear Form
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardContent className="pt-6">
          <div className="text-sm text-muted-foreground space-y-2">
            <p><strong>Next Steps:</strong></p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>You&apos;ll receive an email confirmation with your job details</li>
              <li>Staff will review your submission within 24-48 hours</li>
              <li>If approved, you&apos;ll get a cost estimate and pickup time</li>
              <li>Payment is due upon pickup of completed print</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}