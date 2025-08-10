import React from 'react';
import clsx from 'clsx';

interface InputWithIconProps {
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
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export default function InputWithIcon({
  id,
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled,
  required,
  className,
  icon,
  iconPosition = 'left',
  ...props
}: InputWithIconProps) {
  return (
    <div className="relative">
      {icon && iconPosition === 'left' && (
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <div className="text-gray-400">
            {icon}
          </div>
        </div>
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={clsx(
          'input',
          icon && iconPosition === 'left' && 'pl-10',
          icon && iconPosition === 'right' && 'pr-10',
          className
        )}
        {...props}
      />
      {icon && iconPosition === 'right' && (
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <div className="text-gray-400">
            {icon}
          </div>
        </div>
      )}
    </div>
  );
} 