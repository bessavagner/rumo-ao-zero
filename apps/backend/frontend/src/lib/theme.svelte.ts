// Banda de cor: clara por padrão, escura por escolha, "sistema" se você nunca
// escolheu. O valor vive em <html data-theme> — os tokens (light-dark()) leem
// dali via color-scheme. Persistido em localStorage sob a mesma chave que o
// script anti-flash do index.html lê antes da primeira pintura.
export type Banda = "light" | "dark" | "sistema";

const CHAVE = "rz-tema";

function inicial(): Banda {
  const salvo = localStorage.getItem(CHAVE);
  return salvo === "light" || salvo === "dark" ? salvo : "sistema";
}

export const tema = $state<{ banda: Banda }>({ banda: inicial() });

/** Espelha a banda no <html> e no localStorage. */
function aplicar(banda: Banda): void {
  if (banda === "sistema") {
    delete document.documentElement.dataset.theme;
    localStorage.removeItem(CHAVE);
  } else {
    document.documentElement.dataset.theme = banda;
    localStorage.setItem(CHAVE, banda);
  }
}

/** A banda que está de fato na tela agora (resolve "sistema"). */
export function bandaEfetiva(): "light" | "dark" {
  if (tema.banda !== "sistema") return tema.banda;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/** Alterna claro ↔ escuro. Sai de "sistema" fixando o oposto do que está na tela. */
export function alternarTema(): void {
  const proxima: Banda = bandaEfetiva() === "dark" ? "light" : "dark";
  tema.banda = proxima;
  aplicar(proxima);
}
