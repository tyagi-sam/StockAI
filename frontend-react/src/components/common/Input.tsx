import React from 'react';
import clsx from 'clsx';

interface InputProps {
  id?: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  autoComplete?: string;
  maxLength?: number;
}

export default function Input({
  id,
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled,
  required,
  className,
  ...props
}: InputProps) {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      required={required}
      className={clsx('input', className)}
      {...props}
    />
  );
} 