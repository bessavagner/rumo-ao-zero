import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";

vi.mock("../lib/api", () => ({
  api: {
    get: vi.fn(async (path: string) => {
      if (path.startsWith("/api/series/humor")) return { dias: 7, pontos: [] };
      return {
        dias: 7,
        dias_ate_dia1: 0,
        streaks: { alcool: { consecutivo: 12, ano: 12 }, tabaco: { consecutivo: 12, ano: 12 } },
        dinheiro_economizado: 340,
        estados_frequencia: [],
        triggers_frequencia: {
          por_situacao: [
            { situacao: "fim_expediente", rotulo: "Fim de expediente", ocorrencias: 3 },
          ],
          por_categoria: [
            { categoria: "urges_tentacoes", rotulo: "Urges e tentações", ocorrencias: 3 },
          ],
          coocorrencia: [],
        },
        substituicoes_eficacia: [],
      };
    }),
  },
}));

import Hoje from "./Hoje.svelte";
import { captura, fecharCaptura } from "../lib/capture.svelte";

describe("Início (Hoje)", () => {
  beforeEach(() => fecharCaptura());

  it("chip 'Craving' abre a captura na aba craving", async () => {
    render(Hoje);
    const chip = await screen.findByRole("button", { name: "Craving" });
    await fireEvent.click(chip);
    expect(captura.aberta).toBe(true);
    expect(captura.aba).toBe("craving");
  });

  // As carinhas são um atalho, não um registro: abrem o Pulso com o humor já
  // marcado e deixam o form salvar (energia, craving e nota entram lá).
  it("carinha abre o Pulso com o humor pré-marcado, sem salvar sozinha", async () => {
    render(Hoje);
    const carinha = await screen.findByRole("button", { name: /humor 9 de 10/ });
    await fireEvent.click(carinha);
    expect(captura.aberta).toBe(true);
    expect(captura.aba).toBe("pulso");
    expect(captura.humorInicial).toBe(9);
  });

  it("pede a janela de 7 dias e anuncia a janela que pediu", async () => {
    const { api } = await import("../lib/api");
    render(Hoje);
    await screen.findByText("Gatilhos (7 dias)");
    expect(api.get).toHaveBeenCalledWith("/api/dashboard/?dias=7");
    await screen.findByText("Fim de expediente");
  });
});
