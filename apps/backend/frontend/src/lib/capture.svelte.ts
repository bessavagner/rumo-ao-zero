// Store global da folha de captura. Permite abrir na aba certa de qualquer lugar
// (FAB da navegação e chips do painel) sem prop-drilling pela tabela de rotas.
export type AbaCaptura = "pulso" | "craving" | "slip" | "daily";

export const captura = $state<{ aberta: boolean; aba: AbaCaptura }>({
  aberta: false,
  aba: "pulso",
});

export function abrirCaptura(aba: AbaCaptura = "pulso"): void {
  captura.aba = aba;
  captura.aberta = true;
}

export function fecharCaptura(): void {
  captura.aberta = false;
}
