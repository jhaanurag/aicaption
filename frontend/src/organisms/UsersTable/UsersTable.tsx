import { useEffect, useState } from "react";
import { Checkbox, Input, InputNumber, Message, SelectPicker, Table } from "rsuite";

import Button from "../../atoms/Button/Button";
import { api } from "../../services/api";
import type { User } from "../../typings";
import styles from "./UsersTable.module.scss";

const { Column, HeaderCell, Cell } = Table;

export default function UsersTable() {
  const [users, setUsers] = useState<User[]>([]);
  const [activeFilter, setActiveFilter] = useState("");
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    email_id: "",
    first_name: "",
    last_name: "",
    role: "USER",
    max_ai_credits: 5,
    is_active: true
  });

  async function load() {
    const result = await api.users(activeFilter);
    setUsers(result.users);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, [activeFilter]);

  async function addUser() {
    setMessage("");
    try {
      await api.createUser(form);
      setForm({ ...form, email_id: "", first_name: "", last_name: "" });
      await load();
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  async function updateCredits(user: User, credits: number) {
    await api.updateUser(user.email_id, { email_id: user.email_id, max_ai_credits: credits });
    await load();
  }

  async function deactivate(user: User) {
    await api.deactivateUser(user.email_id);
    await load();
  }

  return (
    <div className={styles.layout}>
      <div className={styles.form}>
        <Input placeholder="Email" value={form.email_id} onChange={(email_id) => setForm({ ...form, email_id })} />
        <Input placeholder="First name" value={form.first_name} onChange={(first_name) => setForm({ ...form, first_name })} />
        <Input placeholder="Last name" value={form.last_name} onChange={(last_name) => setForm({ ...form, last_name })} />
        <InputNumber value={form.max_ai_credits} min={0} onChange={(value) => setForm({ ...form, max_ai_credits: Number(value || 0) })} />
        <Checkbox checked={form.is_active} onChange={(_, checked) => setForm({ ...form, is_active: checked })}>
          Active
        </Checkbox>
        <Button appearance="primary" onClick={addUser}>
          Add User
        </Button>
      </div>

      <div className="toolbar">
        <SelectPicker
          placeholder="Active filter"
          searchable={false}
          data={[
            { label: "All", value: "" },
            { label: "Active", value: "true" },
            { label: "Inactive", value: "false" }
          ]}
          value={activeFilter}
          onChange={(value) => setActiveFilter(value || "")}
        />
      </div>

      {message && <Message type="error">{message}</Message>}

      <Table autoHeight data={users} bordered cellBordered>
        <Column flexGrow={1.2}>
          <HeaderCell>Email</HeaderCell>
          <Cell dataKey="email_id" />
        </Column>
        <Column flexGrow={1}>
          <HeaderCell>Name</HeaderCell>
          <Cell>{(row) => `${row.first_name} ${row.last_name}`}</Cell>
        </Column>
        <Column width={100}>
          <HeaderCell>Role</HeaderCell>
          <Cell dataKey="role" />
        </Column>
        <Column width={150}>
          <HeaderCell>Credits</HeaderCell>
          <Cell>
            {(row) => (
              <InputNumber
                min={0}
                value={row.max_ai_credits}
                onChange={(value) => updateCredits(row, Number(value || 0))}
              />
            )}
          </Cell>
        </Column>
        <Column width={110}>
          <HeaderCell>Active</HeaderCell>
          <Cell>{(row) => (row.is_active ? "Yes" : "No")}</Cell>
        </Column>
        <Column width={130}>
          <HeaderCell>Action</HeaderCell>
          <Cell>
            {(row) => (
              <Button size="xs" appearance="ghost" color="red" disabled={!row.is_active} onClick={() => deactivate(row)}>
                Deactivate
              </Button>
            )}
          </Cell>
        </Column>
      </Table>
    </div>
  );
}
