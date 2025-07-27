import React from 'react';
import clsx from 'clsx';

interface CardProps {
  id?: string;
  children: React.ReactNode;
  className?: string;
}

export default function Card({ id, children, className }: CardProps) {
  return (
    <div id={id} className={clsx('card', className)}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  id?: string;
  children: React.ReactNode;
  className?: string;
}

export function CardHeader({ id, children, className }: CardHeaderProps) {
  return (
    <div id={id} className={clsx('card-header', className)}>
      {children}
    </div>
  );
}

interface CardBodyProps {
  id?: string;
  children: React.ReactNode;
  className?: string;
}

export function CardBody({ id, children, className }: CardBodyProps) {
  return (
    <div id={id} className={clsx('card-body', className)}>
      {children}
    </div>
  );
} 