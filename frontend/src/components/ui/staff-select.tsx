/**
 * Staff Attribution Select Component for 3D Print Management System
 * 
 * Provides staff member selection for action attribution and accountability:
 * - Dropdown list of active staff members
 * - Integration with authentication context
 * - Visual indicators for recently added staff
 * - Form validation and error handling
 * - Consistent styling with shadcn/ui components
 */

'use client'

import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useAuth, type StaffMember } from '@/lib/auth-context';
import { cn } from '@/lib/utils';

// Props for the StaffSelect component
export interface StaffSelectProps {
  value?: number;
  onValueChange?: (staffId: number) => void;
  placeholder?: string;
  includeRole?: boolean;
  showRecentlyAdded?: boolean;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  error?: string;
}

// Props for individual staff item
interface StaffItemProps {
  staff: StaffMember;
  includeRole: boolean;
  showRecentlyAdded: boolean;
}

/**
 * Individual staff item component for the dropdown
 */
function StaffItem({ staff, includeRole, showRecentlyAdded }: StaffItemProps) {
  return (
    <div className="flex items-center justify-between w-full">
      <div className="flex flex-col">
        <span className="font-medium">{staff.name}</span>
        {includeRole && (
          <span className="text-sm text-muted-foreground">{staff.role}</span>
        )}
      </div>
      <div className="flex items-center space-x-1">
        {showRecentlyAdded && staff.is_recently_added && (
          <Badge variant="secondary" className="text-xs">
            New
          </Badge>
        )}
        {!staff.is_active && (
          <Badge variant="destructive" className="text-xs">
            Inactive
          </Badge>
        )}
      </div>
    </div>
  );
}

/**
 * Staff Attribution Select Component
 * 
 * Used for selecting which staff member is performing an action.
 * Integrates with the authentication context to get the staff list.
 */
export function StaffSelect({
  value,
  onValueChange,
  placeholder = "Select staff member",
  includeRole = true,
  showRecentlyAdded = true,
  disabled = false,
  required = false,
  className,
  error,
}: StaffSelectProps) {
  const { staff, selectedStaffId, selectStaff, isLoading } = useAuth();

  // Filter to only show active staff members
  const activeStaff = staff.filter(s => s.is_active);

  // Handle value change
  const handleValueChange = (staffIdString: string) => {
    const staffId = parseInt(staffIdString, 10);
    if (onValueChange) {
      onValueChange(staffId);
    } else {
      // If no external handler, update the auth context
      selectStaff(staffId);
    }
  };

  // Get display value
  const displayValue = value || selectedStaffId;
  const selectedStaff = displayValue ? activeStaff.find(s => s.id === displayValue) : null;

  return (
    <div className={cn("space-y-2", className)}>
      <Select
        value={displayValue?.toString()}
        onValueChange={handleValueChange}
        disabled={disabled || isLoading}
        required={required}
      >
        <SelectTrigger className={cn(
          "w-full",
          error && "border-destructive focus:ring-destructive"
        )}>
          <SelectValue placeholder={isLoading ? "Loading staff..." : placeholder}>
            {selectedStaff && (
              <div className="flex items-center justify-between w-full">
                <span>{selectedStaff.name}</span>
                {includeRole && (
                  <span className="text-sm text-muted-foreground ml-2">
                    {selectedStaff.role}
                  </span>
                )}
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {activeStaff.length === 0 ? (
            <SelectItem value="" disabled>
              No active staff members found
            </SelectItem>
          ) : (
            activeStaff.map((staffMember) => (
              <SelectItem 
                key={staffMember.id} 
                value={staffMember.id.toString()}
                className="py-3"
              >
                <StaffItem
                  staff={staffMember}
                  includeRole={includeRole}
                  showRecentlyAdded={showRecentlyAdded}
                />
              </SelectItem>
            ))
          )}
        </SelectContent>
      </Select>
      
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </div>
  );
}

/**
 * Compact Staff Select for space-constrained areas
 */
export function StaffSelectCompact({
  value,
  onValueChange,
  placeholder = "Staff",
  disabled = false,
  className,
}: Omit<StaffSelectProps, 'includeRole' | 'showRecentlyAdded' | 'required' | 'error'>) {
  return (
    <StaffSelect
      value={value}
      onValueChange={onValueChange}
      placeholder={placeholder}
      includeRole={false}
      showRecentlyAdded={false}
      disabled={disabled}
      className={className}
    />
  );
}

/**
 * Staff Select with current user as default
 */
export function StaffSelectWithDefault(props: Omit<StaffSelectProps, 'value'>) {
  const { selectedStaffId } = useAuth();
  
  return (
    <StaffSelect
      {...props}
      value={selectedStaffId || undefined}
    />
  );
}

/**
 * Hook for getting selected staff info
 */
export function useSelectedStaff(staffId?: number) {
  const { staff, selectedStaffId } = useAuth();
  const targetId = staffId || selectedStaffId;
  
  const selectedStaff = targetId ? staff.find(s => s.id === targetId) : null;
  
  return {
    staff: selectedStaff,
    isSelected: !!selectedStaff,
    name: selectedStaff?.name || null,
    role: selectedStaff?.role || null,
    is_active: selectedStaff?.is_active || false,
    is_recently_added: selectedStaff?.is_recently_added || false,
  };
}

/**
 * Form field wrapper for staff selection
 */
export function StaffSelectField({
  label = "Staff Member",
  description,
  required = true,
  ...props
}: StaffSelectProps & {
  label?: string;
  description?: string;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </label>
      <StaffSelect {...props} required={required} />
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
    </div>
  );
}

/**
 * Staff display component (read-only)
 */
export function StaffDisplay({ 
  staffId, 
  includeRole = true,
  className 
}: { 
  staffId: number; 
  includeRole?: boolean;
  className?: string;
}) {
  const { staff } = useSelectedStaff(staffId);
  
  if (!staff) {
    return (
      <span className={cn("text-muted-foreground", className)}>
        Unknown staff member
      </span>
    );
  }
  
  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <span className="font-medium">{staff.name}</span>
      {includeRole && (
        <Badge variant="outline" className="text-xs">
          {staff.role}
        </Badge>
      )}
      {!staff.is_active && (
        <Badge variant="destructive" className="text-xs">
          Inactive
        </Badge>
      )}
    </div>
  );
}

export default StaffSelect;