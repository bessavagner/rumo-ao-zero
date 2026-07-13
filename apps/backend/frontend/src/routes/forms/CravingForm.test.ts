import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";

const get = vi.fn();
const post = vi.fn();
const patch = vi.fn();
const list = vi.fn();
vi.mock("../../lib/api", () => ({
  api: {
    get: (p: string) => get(p),
    post: (p: string, b: unknown) => post(p, b),
    patch: (p: string, b: unknown) => patch(p, b),
    list: (p: string) => list(p),
  },
  ApiError: class extends Error {},
}));

import CravingForm from "./CravingForm.svelte";
import { resetTaxonomia } from "../../lib/taxonomia.svelte";

describe("CravingForm", () => {
  beforeEach(() => {
    resetTaxonomia();
    get.mockReset();
    post.mockReset();
    patch.mockReset();
    list.mockReset();
    get.mockImplementation(async (path: string) => {
      if (path.includes("gatilhos"))
        return {
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
        };
      if (path.includes("substituicoes"))
        return {
          substituicoes: [
            { codigo: "oral", rotulo: "Oral — chá, água, goma, comer algo" },
            { codigo: "movimento", rotulo: "Movimento — andar, correr, alongar, qualquer coisa com o corpo" },
            { codigo: "social", rotulo: "Social — ligar, mandar mensagem, ficar perto de alguém" },
            { codigo: "cognitivo", rotulo: "Cognitivo — escrever, ler, respirar, esperar a onda passar" },
            { codigo: "ambiental", rotulo: "Ambiental — mudar de ambiente, sair da situação" },
          ],
        };
      return { estados: [{ codigo: "cansaco", rotulo: "Cansaço" }] };
    });
    post.mockResolvedValue({ id: 42 });
    patch.mockResolvedValue({ id: 42 });
  });

  it("mostra as situações agrupadas por categoria e nenhum campo de texto livre de gatilho", async () => {
    render(CravingForm, { onDone: () => {} });
    await screen.findByRole("option", { name: "Fim de expediente" });
    const grupo = document.querySelector("optgroup");
    expect(grupo?.getAttribute("label")).toBe("Urges e tentações");
    // O datalist era a interface do problema antigo — não pode mais existir.
    expect(document.querySelector("datalist")).toBeNull();
  });

  it("oferece as 5 categorias de substituição, não um catálogo", async () => {
    render(CravingForm, { onDone: () => {} });
    await screen.findByRole("option", { name: /Movimento/ });
    // O rótulo precisa dizer que corrida cabe — era o bug.
    const movimento = await screen.findByRole("option", { name: /Movimento/ });
    expect(movimento.textContent).toContain("correr");
    // O catálogo antigo não é mais buscado.
    expect(list).not.toHaveBeenCalledWith("/api/baseline/substitutions/");
  });

  it("posta a categoria e o texto livre do que fez", async () => {
    render(CravingForm, { onDone: () => {} });
    await screen.findByRole("option", { name: "Fim de expediente" });

    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "fim_expediente" },
    });
    await fireEvent.change(screen.getByLabelText("O que eu fiz"), {
      target: { value: "movimento" },
    });
    await fireEvent.input(screen.getByLabelText("O que você fez, nas suas palavras"), {
      target: { value: "corri 5k" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar craving" }));

    expect(post).toHaveBeenCalledTimes(1);
    const [, corpo] = post.mock.calls[0];
    expect(corpo.substituicao).toBe("movimento");
    expect(corpo.substituicao_detalhes).toBe("corri 5k");
    expect(corpo.substituicao_usada).toBeUndefined();
  });

  it("depois de salvar, oferece o thought record como passo opcional", async () => {
    const onDone = vi.fn();
    render(CravingForm, { onDone });
    await screen.findByRole("option", { name: "Fim de expediente" });
    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "fim_expediente" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar craving" }));

    // O craving já está gravado; o aprofundamento é oferecido, não exigido.
    expect(onDone).not.toHaveBeenCalled();
    await screen.findByText("Quer aprofundar?");
    await fireEvent.input(screen.getByLabelText("Pensamento automático"), {
      target: { value: "eu preciso disso pra relaxar" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar reflexão" }));

    expect(patch).toHaveBeenCalledWith("/api/log/cravings/42/", {
      pensamento_automatico: "eu preciso disso pra relaxar",
      evidencia_favor: "",
      evidencia_contra: "",
      pensamento_balanceado: "",
    });
    expect(onDone).toHaveBeenCalled();
  });

  it("'Agora não' fecha sem aprofundar — o registro já aconteceu", async () => {
    const onDone = vi.fn();
    render(CravingForm, { onDone });
    await screen.findByRole("option", { name: "Fim de expediente" });
    await fireEvent.change(screen.getByLabelText("Gatilho principal"), {
      target: { value: "fim_expediente" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar craving" }));
    await screen.findByText("Quer aprofundar?");
    await fireEvent.click(screen.getByRole("button", { name: "Agora não" }));

    expect(patch).not.toHaveBeenCalled();
    expect(onDone).toHaveBeenCalled();
  });
});
