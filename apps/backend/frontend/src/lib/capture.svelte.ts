// Store global da folha de captura. Permite abrir na aba certa de qualquer lugar
// (＋ da navegação, chips e carinhas do painel) sem prop-drilling pela tabela de
// rotas.
export type AbaCaptura = "pulso" | "craving" | "slip" | "daily";

export const captura = $state<{ aberta: boolean; aba: AbaCaptura; humorInicial?: number }>({
  aberta: false,
  aba: "pulso",
});

/** `humor` pré-seleciona a escala de humor do Pulso (as carinhas do Início).
    Não salva nada sozinho: só abre o form já com o valor marcado. */
export function abrirCaptura(aba: AbaCaptura = "pulso", humor?: number): void {
  captura.aba = aba;
  captura.humorInicial = humor;
  captura.aberta = true;
}

export function fecharCaptura(): void {
  captura.aberta = false;
  captura.humorInicial = undefined;
}
