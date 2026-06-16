import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import CaptureSheet from "./CaptureSheet.svelte";
import { abrirCaptura, fecharCaptura } from "./capture.svelte";

describe("CaptureSheet", () => {
  it("mostra as 4 abas e abre no Pulso por padrão", () => {
    fecharCaptura();
    abrirCaptura("pulso");
    render(CaptureSheet, { onClose: () => {} });
    for (const t of ["Pulso", "Craving", "Slip", "Daily"]) {
      expect(screen.getByRole("tab", { name: t })).toBeTruthy();
    }
    expect(screen.getByRole("heading", { name: "Pulso" })).toBeTruthy();
  });

  it("respeita a aba inicial do store", () => {
    abrirCaptura("slip");
    render(CaptureSheet, { onClose: () => {} });
    expect(screen.getByRole("heading", { name: "Slip" })).toBeTruthy();
  });

  it("troca de aba ao clicar", async () => {
    abrirCaptura("pulso");
    render(CaptureSheet, { onClose: () => {} });
    await fireEvent.click(screen.getByRole("tab", { name: "Daily" }));
    expect(screen.getByRole("heading", { name: "Daily" })).toBeTruthy();
  });
});
