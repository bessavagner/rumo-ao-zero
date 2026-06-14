import { describe, it, expect, vi, beforeEach } from "vitest";
import { api, ApiError } from "./api";

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("api", () => {
  it("manda Authorization quando ha token", async () => {
    localStorage.setItem("token", "abc123");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 })
    );
    vi.stubGlobal("fetch", fetchMock);

    await api.get("/api/dashboard/");

    const headers = fetchMock.mock.calls[0][1].headers;
    expect(headers["Authorization"]).toBe("Token abc123");
  });

  it("lanca ApiError em status >= 400", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "nope" }), { status: 400 })
    ));
    await expect(api.get("/api/x/")).rejects.toBeInstanceOf(ApiError);
  });
});
