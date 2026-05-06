import styles from "./FormField.module.scss";
import type { FormFieldProps } from "./types";

export default function FormField({ label, error, children }: FormFieldProps) {
  return (
    <label className={styles.field}>
      <span>{label}</span>
      {children}
      {error && <small>{error}</small>}
    </label>
  );
}
