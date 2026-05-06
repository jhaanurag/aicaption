import { Input } from "rsuite";

import styles from "./TextInput.module.scss";
import type { TextInputProps } from "./types";

export default function TextInput(props: TextInputProps) {
  return <Input {...props} className={`${styles.input} ${props.className || ""}`} />;
}
