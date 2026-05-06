import { Button as RsuiteButton } from "rsuite";

import styles from "./Button.module.scss";
import type { ButtonProps } from "./types";

export default function Button(props: ButtonProps) {
  return <RsuiteButton {...props} className={`${styles.button} ${props.className || ""}`} />;
}
