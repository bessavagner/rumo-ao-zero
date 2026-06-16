import { logout } from "./auth.svelte";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(`API ${status}`);
    this.status = status;
    this.body = body;
  }
}

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Token ${token}`;
  return h;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const resp = await fetch(path, {
    method,
    headers: authHeaders(),
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await resp.text();
  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text; // corpo não-JSON (ex.: página de erro HTML quando DEBUG=True)
    }
  }
  if (resp.status === 401) logout(); // token inválido/expirado: volta pro login
  if (resp.status >= 400) throw new ApiError(resp.status, parsed);
  return parsed as T;
}

// Valor de parâmetro de querystring (filtros/ordering/page). undefined/null são ignorados.
export type QueryParams = Record<string, string | number | boolean | undefined | null>;

function withQuery(path: string, params?: QueryParams): string {
  if (!params) return path;
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") qs.append(k, String(v));
  }
  const s = qs.toString();
  return s ? `${path}?${s}` : path;
}

// Resposta paginada padrão do DRF (PageNumberPagination).
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body: unknown) => request<T>("PATCH", path, body),
  del: <T = void>(path: string) => request<T>("DELETE", path),
  // Lista com filtros/ordering/page → monta ?ordering=-timestamp&page=1
  list: <T>(path: string, params?: QueryParams) =>
    request<Paginated<T>>("GET", withQuery(path, params)),
};
