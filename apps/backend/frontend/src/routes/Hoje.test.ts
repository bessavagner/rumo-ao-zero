import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";

vi.mock("../lib/api", () => ({
  api: {
    get: vi.fn(async (path: string) => {
      if (path.startsWith("/api/series/humor")) return { dias: 7, pontos: [] };
      return {
        dias_ate_dia1: 0,
        streaks: { alcool: { consecutivo: 12, ano: 12 }, tabaco: { consecutivo: 12, ano: 12 } },
        dinheiro_economizado: 340,
        estados_frequencia: [],
        triggers_frequencia: [{ gatilho: "fim de tarde", ocorrencias: 3 }],
        substituicoes_eficacia: [],
      };
    }),
  },
}));

import Hoje from "./Hoje.svelte";
import { captura, fecharCaptura } from "../lib/capture.svelte";

describe("Início (Hoje)", () => {
  beforeEach(() => fecharCaptura());

  it("chip '+ Craving' abre a captura na aba craving", async () => {
    render(Hoje);
    const chip = await screen.findByRole("button", { name: "+ Craving" });
    await fireEvent.click(chip);
    expect(captura.aberta).toBe(true);
    expect(captura.aba).toBe("craving");
  });
});
