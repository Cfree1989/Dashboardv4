import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface ConfirmationPageProps {
  params: Promise<{
    token: string;
  }>;
}

export default async function ConfirmationPage({ params }: ConfirmationPageProps) {
  const { token } = await params;

  // TODO: Validate token with backend API
  // For now, show a placeholder confirmation interface

  return (
    <div className="container mx-auto max-w-2xl p-6 min-h-screen flex items-center justify-center">
      <Card className="w-full">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Confirm Your 3D Print Submission</CardTitle>
          <CardDescription>
            Review and confirm your 3D print job details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <Badge variant="outline" className="text-sm">
              Token: {token.substring(0, 8)}...
            </Badge>
          </div>

          {/* Placeholder for job details - will be populated from API */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium">Student Name</h3>
                <p className="text-muted-foreground">Loading...</p>
              </div>
              <div>
                <h3 className="font-medium">Email</h3>
                <p className="text-muted-foreground">Loading...</p>
              </div>
            </div>

            <div>
              <h3 className="font-medium">Project Title</h3>
              <p className="text-muted-foreground">Loading...</p>
            </div>

            <div>
              <h3 className="font-medium">File Name</h3>
              <p className="text-muted-foreground">Loading...</p>
            </div>

            <div>
              <h3 className="font-medium">Additional Notes</h3>
              <p className="text-muted-foreground">Loading...</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium">Infill Percentage</h3>
                <p className="text-muted-foreground">Loading...</p>
              </div>
              <div>
                <h3 className="font-medium">Layer Height</h3>
                <p className="text-muted-foreground">Loading...</p>
              </div>
            </div>
          </div>

          <div className="border-t pt-6">
            <div className="flex gap-3">
              <Button className="flex-1">
                Confirm Job Submission
              </Button>
              <Button variant="outline">
                Cancel Submission
              </Button>
            </div>
          </div>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              By confirming, you acknowledge the job details are correct and authorize processing.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}