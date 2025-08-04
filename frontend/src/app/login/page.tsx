import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function LoginPage() {
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
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="workstationId">Workstation ID</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select workstation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="workstation-1">Workstation 1</SelectItem>
                  <SelectItem value="workstation-2">Workstation 2</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Workstation Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter workstation password"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="staffName">Your Name</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select your name" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="alice-johnson">Alice Johnson</SelectItem>
                  <SelectItem value="bob-smith">Bob Smith</SelectItem>
                  <SelectItem value="carol-davis">Carol Davis</SelectItem>
                  <SelectItem value="admin-user">Admin User</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                This will be used for action attribution and audit trails
              </p>
            </div>

            <Button type="submit" className="w-full">
              Login to Dashboard
            </Button>
          </form>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Session will expire after 12 hours of inactivity
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}