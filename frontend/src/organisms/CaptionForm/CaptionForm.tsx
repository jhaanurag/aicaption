import { useEffect, useState } from "react";
import { Input, Message, Panel } from "rsuite";

import Button from "../../atoms/Button/Button";
import SelectPicker from "../../atoms/SelectPicker/SelectPicker";
import FormField from "../../molecules/FormField/FormField";
import { api } from "../../services/api";
import styles from "./CaptionForm.module.scss";

const tones = ["Professional", "Quirky", "Urgent", "Educational"].map((tone) => ({
  label: tone,
  value: tone
}));

export default function CaptionForm() {
  const [credits, setCredits] = useState(0);
  const [description, setDescription] = useState("");
  const [tone, setTone] = useState("Professional");
  const [caption, setCaption] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadCredits() {
    const result = await api.credits();
    setCredits(result.max_ai_credits);
  }

  useEffect(() => {
    loadCredits().catch((error) => setMessage(error.message));
  }, []);

  async function generate() {
    setLoading(true);
    setMessage("");
    try {
      const result = await api.generateCaption(description, tone);
      setCaption(result.generated_caption);
      await loadCredits();
    } catch (error) {
      setMessage((error as Error).message);
    }
    setLoading(false);
  }

  async function submitForApproval() {
    setMessage("");
    try {
      await api.submitRequest({
        product_description: description,
        campaign_tone: tone,
        generated_caption: caption
      });
      setMessage("Submitted for approval.");
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  return (
    <div className={styles.layout}>
      <header>
        <h2>Create New Caption</h2>
        <strong>{credits} credits</strong>
      </header>

      <Panel bordered className={styles.panel}>
        <FormField label="Product Description">
          <Input as="textarea" rows={5} value={description} onChange={setDescription} />
        </FormField>

        <FormField label="Campaign Tone">
          <SelectPicker data={tones} value={tone} onChange={(value) => setTone(value || "Professional")} />
        </FormField>

        {message && <Message type={message.includes("Submitted") ? "success" : "error"}>{message}</Message>}

        <Button appearance="primary" loading={loading} disabled={!description || credits < 1} onClick={generate}>
          Generate Caption
        </Button>
      </Panel>

      {caption && (
        <Panel bordered className={styles.caption}>
          <h3>Generated Caption</h3>
          <p>{caption}</p>
          <Button appearance="primary" color="green" onClick={submitForApproval}>
            Submit for Approval
          </Button>
        </Panel>
      )}
    </div>
  );
}
