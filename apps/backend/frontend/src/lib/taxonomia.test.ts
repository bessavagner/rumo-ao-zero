import { describe, it, expect, vi, beforeEach } from "vitest";

const get = vi.fn();
vi.mock("./api", () => ({ api: { get: (p: string) => get(p) } }));

import { carregarGatilhos, carregarEstados, rotuloDe, resetTaxonomia } from "./taxonomia.svelte";

const GATILHOS = {
  grupos: [
    {
      categoria: "urges_tentacoes",
      rotulo: "Urges e tentações",
      situacoes: [{ codigo: "fim_expediente", rotulo: "Fim de expediente" }],
    },
  ],
  sem_categoria: [{ codigo: "outro", rotulo: "Outro" }],
};

describe("taxonomia", () => {
  beforeEach(() => {
    resetTaxonomia();
    get.mockReset();
    get.mockImplementation(async (path: string) =>
      path.includes("gatilhos") ? GATILHOS : { estados: [{ codigo: "cansaco", rotulo: "Cansaço" }] },
    );
  });

  it("busca a taxonomia uma vez só e reusa (memoizada)", async () => {
    await carregarGatilhos();
    await carregarGatilhos();
    expect(get).toHaveBeenCalledTimes(1);
    expect(get).toHaveBeenCalledWith("/api/taxonomia/gatilhos/");
  });

  it("rotuloDe traduz o código depois de carregar", async () => {
    expect(rotuloDe("fim_expediente")).toBe("fim_expediente"); // antes de carregar: o próprio código
    await carregarGatilhos();
    await carregarEstados();
    expect(rotuloDe("fim_expediente")).toBe("Fim de expediente");
    expect(rotuloDe("outro")).toBe("Outro");
    expect(rotuloDe("cansaco")).toBe("Cansaço");
  });
});
