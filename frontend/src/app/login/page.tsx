'use client'

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

// Workstation options (these would typically come from environment config)
const WORKSTATIONS = [
  { id: 'workstation-1', name: 'Workstation 1' },
  { id: 'workstation-2', name: 'Workstation 2' },
  { id: 'workstation-3', name: 'Workstation 3' },
  { id: 'admin-station', name: 'Admin Station' },
];

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isAuthenticated, isLoading, staff, error, clearError } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    workstationId: '',
    password: '',
    staffId: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Get return URL from query params
  const returnUrl = searchParams.get('returnUrl') || '/dashboard';

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push(returnUrl);
    }
  }, [isAuthenticated, isLoading, router, returnUrl]);

  // Clear error when user starts typing
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => clearError(), 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  // Handle form input changes
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific errors
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }));
    }
    
    // Clear general error
    if (error) {
      clearError();
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.workstationId) {
      errors.workstationId = 'Please select a workstation';
    }

    if (!formData.password) {
      errors.password = 'Please enter the workstation password';
    }

    if (!formData.staffId) {
      errors.staffId = 'Please select your name';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const success = await login(
        formData.workstationId,
        formData.password,
        parseInt(formData.staffId, 10)
      );

      if (success) {
        // Redirect will happen automatically via useEffect
        console.log('Login successful, redirecting to:', returnUrl);
      }
    } catch (err) {
      console.error('Login submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-md p-6 min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Don't render login form if already authenticated
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="container mx-auto max-w-md p-6 min-h-screen flex items-center justify-center">
      <Card className="w-full">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Workstation Login</CardTitle>
          <CardDescription>
            Staff authentication for 3D print management
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Workstation Selection */}
            <div className="space-y-2">
              <Label htmlFor="workstationId">
                Workstation ID <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.workstationId}
                onValueChange={(value) => handleInputChange('workstationId', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger className={formErrors.workstationId ? 'border-destructive' : ''}>
                  <SelectValue placeholder="Select workstation" />
                </SelectTrigger>
                <SelectContent>
                  {WORKSTATIONS.map((workstation) => (
                    <SelectItem key={workstation.id} value={workstation.id}>
                      {workstation.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {formErrors.workstationId && (
                <p className="text-sm text-destructive">{formErrors.workstationId}</p>
              )}
            </div>

            {/* Password Input */}
            <div className="space-y-2">
              <Label htmlFor="password">
                Workstation Password <span className="text-destructive">*</span>
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter workstation password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                disabled={isSubmitting}
                className={formErrors.password ? 'border-destructive' : ''}
                required
              />
              {formErrors.password && (
                <p className="text-sm text-destructive">{formErrors.password}</p>
              )}
            </div>

            {/* Staff Selection */}
            <div className="space-y-2">
              <Label htmlFor="staffName">
                Your Name <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.staffId}
                onValueChange={(value) => handleInputChange('staffId', value)}
                disabled={isSubmitting || staff.length === 0}
              >
                <SelectTrigger className={formErrors.staffId ? 'border-destructive' : ''}>
                  <SelectValue placeholder={
                    staff.length === 0 ? "Loading staff..." : "Select your name"
                  } />
                </SelectTrigger>
                <SelectContent>
                  {staff.filter(s => s.is_active).map((staffMember) => (
                    <SelectItem key={staffMember.id} value={staffMember.id.toString()}>
                      <div className="flex flex-col">
                        <span className="font-medium">{staffMember.name}</span>
                        <span className="text-sm text-muted-foreground">{staffMember.role}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {formErrors.staffId && (
                <p className="text-sm text-destructive">{formErrors.staffId}</p>
              )}
              <p className="text-sm text-muted-foreground">
                This will be used for action attribution and audit trails
              </p>
            </div>

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Logging in...
                </>
              ) : (
                'Login to Dashboard'
              )}
            </Button>
          </form>

          {/* Session Info */}
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Session will expire after 12 hours of inactivity
            </p>
          </div>

          {/* Return URL Info */}
          {returnUrl !== '/dashboard' && (
            <div className="text-center">
              <p className="text-xs text-muted-foreground">
                You will be redirected to: {returnUrl}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto max-w-md p-6 min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}