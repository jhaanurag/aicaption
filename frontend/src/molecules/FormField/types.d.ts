import type { ReactNode } from "react";

export interface FormFieldProps {
  label: string;
  error?: string;
  children: ReactNode;
}
