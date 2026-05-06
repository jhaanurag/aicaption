import { useEffect, useState } from "react";

import AppShell from "./organisms/AppShell/AppShell";
import LoginPanel from "./organisms/LoginPanel/LoginPanel";
import { routes } from "./routes";
import { api } from "./services/api";
import type { User } from "./typings";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [activePage, setActivePage] = useState("create-caption");

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (!savedToken) return;

    api
      .me()
      .then((me) => {
        setUser(me);
        setActivePage(me.role === "ADMIN" ? "admin-users" : "create-caption");
      })
      .catch(() => localStorage.removeItem("token"));
  }, []);

  function login(token: string, nextUser: User) {
    localStorage.setItem("token", token);
    setUser(nextUser);
    setActivePage(nextUser.role === "ADMIN" ? "admin-users" : "create-caption");
  }

  function logout() {
    localStorage.removeItem("token");
    setUser(null);
  }

  if (!user) {
    return <LoginPanel onLogin={login} />;
  }

  const Page = routes[activePage as keyof typeof routes];

  return (
    <AppShell user={user} activePage={activePage} onPageChange={setActivePage} onLogout={logout}>
      <Page />
    </AppShell>
  );
}
