import { FormEvent, useState } from "react";
import { Message, Panel } from "rsuite";

import Button from "../../atoms/Button/Button";
import TextInput from "../../atoms/TextInput/TextInput";
import FormField from "../../molecules/FormField/FormField";
import { api } from "../../services/api";
import type { User } from "../../typings";
import styles from "./LoginPanel.module.scss";

interface LoginPanelProps {
  onLogin: (token: string, user: User) => void;
}

export default function LoginPanel({ onLogin }: LoginPanelProps) {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitEmail(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      await api.sendOtp(email);
      setOtpSent(true);
      setMessage("OTP sent. Check the user's email.");
    } catch (error) {
      setMessage((error as Error).message);
    }
    setLoading(false);
  }

  async function submitOtp(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const result = await api.verifyOtp(email, otp);
      onLogin(result.token, result.user);
    } catch (error) {
      setMessage((error as Error).message);
    }
    setLoading(false);
  }

  return (
    <main className={styles.page}>
      <section className={styles.copy}>
        <p>AI Caption Generator</p>
        <h1>Generate captions. Route approvals. Keep credits controlled.</h1>
      </section>

      <Panel bordered className={styles.panel}>
        <form onSubmit={otpSent ? submitOtp : submitEmail}>
          <h2>Sign in</h2>

          <FormField label="Email">
            <TextInput value={email} onChange={setEmail} type="email" required />
          </FormField>

          {otpSent && (
            <FormField label="6-digit OTP">
              <TextInput value={otp} onChange={setOtp} maxLength={6} required />
            </FormField>
          )}

          {message && <Message type={message.includes("sent") ? "success" : "error"}>{message}</Message>}

          <Button appearance="primary" type="submit" loading={loading} block>
            {otpSent ? "Verify OTP" : "Send OTP"}
          </Button>
        </form>
      </Panel>
    </main>
  );
}
