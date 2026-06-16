import { describe, it, expect, beforeEach } from "vitest";
import { captura, abrirCaptura, fecharCaptura } from "./capture.svelte";

describe("store de captura", () => {
  beforeEach(() => fecharCaptura());

  it("começa fechado na aba pulso", () => {
    expect(captura.aberta).toBe(false);
    expect(captura.aba).toBe("pulso");
  });

  it("abrirCaptura abre na aba pedida", () => {
    abrirCaptura("craving");
    expect(captura.aberta).toBe(true);
    expect(captura.aba).toBe("craving");
  });

  it("abrirCaptura sem argumento usa pulso", () => {
    abrirCaptura();
    expect(captura.aba).toBe("pulso");
  });

  it("fecharCaptura fecha", () => {
    abrirCaptura("slip");
    fecharCaptura();
    expect(captura.aberta).toBe(false);
  });
});
