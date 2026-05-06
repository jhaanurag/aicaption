import type { ReactNode } from "react";
import { Nav } from "rsuite";

import type { User } from "../../typings";
import styles from "./AppShell.module.scss";

interface AppShellProps {
  user: User;
  activePage: string;
  onPageChange: (page: string) => void;
  onLogout: () => void;
  children: ReactNode;
}

export default function AppShell({ user, activePage, onPageChange, onLogout, children }: AppShellProps) {
  const adminPages = [
    ["admin-users", "Manage Users"],
    ["admin-approvals", "Approval Requests"]
  ];
  const userPages = [
    ["create-caption", "Create Caption"],
    ["past-requests", "Past Requests"]
  ];
  const pages = user.role === "ADMIN" ? adminPages : userPages;

  return (
    <main className={styles.shell}>
      <aside>
        <h1>CaptionOps</h1>
        <p>{user.email_id}</p>
        <Nav vertical activeKey={activePage} onSelect={(key) => onPageChange(String(key))}>
          {pages.map(([key, label]) => (
            <Nav.Item key={key} eventKey={key}>
              {label}
            </Nav.Item>
          ))}
        </Nav>
        <button onClick={onLogout}>Logout</button>
      </aside>
      <section>{children}</section>
    </main>
  );
}
