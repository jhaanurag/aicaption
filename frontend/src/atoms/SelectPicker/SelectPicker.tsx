import { SelectPicker as RsuiteSelectPicker } from "rsuite";

import styles from "./SelectPicker.module.scss";
import type { SelectPickerProps } from "./types";

export default function SelectPicker(props: SelectPickerProps) {
  return (
    <RsuiteSelectPicker
      {...props}
      block
      searchable={false}
      className={`${styles.select} ${props.className || ""}`}
    />
  );
}
