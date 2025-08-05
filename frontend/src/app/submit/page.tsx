'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { SubmissionForm } from '@/components/submission/submission-form';
import { Button } from '@/components/ui/button';
import { CheckCircle } from 'lucide-react';

interface JobData {
  id: string;
  display_name: string;
  status: string;
  created_at: string;
  estimated_cost: string;
}

export default function SubmitPage() {
  const [submittedJob, setSubmittedJob] = useState<JobData | null>(null);

  const handleSubmissionSuccess = (jobData: JobData) => {
    setSubmittedJob(jobData);
  };

  const handleSubmitAnother = () => {
    setSubmittedJob(null);
  };

  if (submittedJob) {
    return (
      <div className="container mx-auto max-w-2xl p-6">
        <div className="mb-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold tracking-tight text-green-600">Submission Successful!</h1>
          <p className="text-muted-foreground">
            Your 3D print job has been submitted successfully
          </p>
        </div>

        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="text-center">
                <h2 className="text-xl font-semibold mb-2">Job Details</h2>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p><strong>Job ID:</strong> {submittedJob.id}</p>
                  <p><strong>File Name:</strong> {submittedJob.display_name}</p>
                  <p><strong>Status:</strong> {submittedJob.status}</p>
                  <p><strong>Estimated Cost:</strong> {submittedJob.estimated_cost}</p>
                  <p><strong>Submitted:</strong> {new Date(submittedJob.created_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="text-sm text-muted-foreground space-y-2">
                <p><strong>What happens next:</strong></p>
                <ol className="list-decimal list-inside space-y-1 ml-4">
                  <li>Staff will review your submission within 24-48 hours</li>
                  <li>If approved, you'll receive an email with cost details and confirmation link</li>
                  <li>Click the confirmation link to proceed with printing</li>
                  <li>You'll be notified when your print is complete and ready for pickup</li>
                  <li>Payment is due upon pickup of completed print</li>
                </ol>
              </div>

              <div className="flex justify-center pt-4">
                <Button onClick={handleSubmitAnother}>
                  Submit Another Job
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-2xl p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Submit 3D Print Job</h1>
        <p className="text-muted-foreground">
          Upload your 3D model and provide job details
        </p>
      </div>

      <SubmissionForm onSuccess={handleSubmissionSuccess} />

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