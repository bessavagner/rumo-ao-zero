import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";

const get = vi.fn();
vi.mock("./api", () => ({
  api: { get: (p: string) => get(p) },
  ApiError: class extends Error {},
}));

import Harness from "./GatilhoPicker.harness.svelte";
import { resetTaxonomia } from "./taxonomia.svelte";

function estadoAtual() {
  return JSON.parse(screen.getByTestId("estado").textContent ?? "{}") as {
    gatilho: string;
    adicionais: string[];
  };
}

describe("GatilhoPicker", () => {
  beforeEach(() => {
    resetTaxonomia();
    get.mockReset();
    get.mockResolvedValue({
      grupos: [
        {
          categoria: "urges_tentacoes",
          rotulo: "Urges e tentações",
          situacoes: [
            { codigo: "fim_expediente", rotulo: "Fim de expediente" },
            { codigo: "bebendo", rotulo: "Bebendo (gatilho cruzado)" },
          ],
        },
      ],
      sem_categoria: [{ codigo: "outro", rotulo: "Outro" }],
    });
  });

  it("nunca deixa o principal também em adicionais (Minor 4)", async () => {
    render(Harness, {});
    await screen.findByRole("option", { name: "Fim de expediente" });

    // Marca "bebendo" como adicional.
    await fireEvent.click(screen.getByLabelText("Bebendo (gatilho cruzado)"));
    expect(estadoAtual().adicionais).toEqual(["bebendo"]);

    // Troca o gatilho principal para "bebendo" — o chip some da tela (é o mesmo código do
    // principal), mas o código NÃO pode continuar em `adicionais`.
    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "bebendo" },
    });

    const estado = estadoAtual();
    expect(estado.gatilho).toBe("bebendo");
    expect(estado.adicionais).toEqual([]);
  });

  it("mantém os outros adicionais intactos ao remover só o que virou principal", async () => {
    render(Harness, {});
    await screen.findByRole("option", { name: "Fim de expediente" });

    await fireEvent.click(screen.getByLabelText("Bebendo (gatilho cruzado)"));
    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "fim_expediente" },
    });
    // "bebendo" segue como adicional válido enquanto o principal é outro código.
    expect(estadoAtual().adicionais).toEqual(["bebendo"]);

    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "bebendo" },
    });
    // Agora "bebendo" é o principal: não pode sobrar em adicionais.
    expect(estadoAtual().adicionais).toEqual([]);
  });
});
