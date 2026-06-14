// Estado de sessão (Svelte 5 runes). Single-user; token em localStorage.
export const auth = $state({
  token: localStorage.getItem("token"),
});

export async function login(username: string, password: string): Promise<void> {
  const resp = await fetch("/api/auth/token/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) throw new Error("login falhou");
  const { token } = await resp.json();
  localStorage.setItem("token", token);
  auth.token = token;
}

export function logout(): void {
  localStorage.removeItem("token");
  auth.token = null;
}
