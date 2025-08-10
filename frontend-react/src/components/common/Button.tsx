import React from 'react';
import clsx from 'clsx';

interface ButtonProps {
  id?: string;
  variant?: 'primary' | 'secondary' | 'success' | 'error' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export default function Button({ 
  id,
  variant = 'primary', 
  size = 'md', 
  loading, 
  children, 
  className,
  ...props 
}: ButtonProps) {
  const baseClasses = "btn";
  
  const variants = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    success: "btn-success",
    error: "btn-error",
    ghost: "btn-ghost"
  };
  
  const sizes = {
    sm: "px-2 py-1.5 text-xs sm:text-sm",
    md: "px-3 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  return (
    <button 
      id={id}
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        className
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
      )}
      {children}
    </button>
  );
} 