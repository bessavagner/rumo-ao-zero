import { ApiError } from "./api";

// Rótulos amigáveis para nomes de campo do DRF nas mensagens de erro.
const FIELD_LABELS: Record<string, string> = {
  humor: "humor",
  energia: "energia",
  sono_h: "horas de sono",
  sono_q: "qualidade do sono",
  craving: "craving",
  craving_pico: "craving pico",
  intensidade_pico: "intensidade pico",
  intensidade_final: "intensidade final",
  duracao_min: "duração",
  gatilho_texto: "gatilho",
  substancia: "substância",
  data: "data",
  timestamp: "horário",
  quantidade: "quantidade",
  contexto: "contexto",
  nota: "nota",
  non_field_errors: "",
  detail: "",
};

function labelFor(campo: string): string {
  return FIELD_LABELS[campo] ?? campo;
}

/**
 * Extrai uma mensagem legível de um erro de API.
 *
 * - `ApiError` com `body.detail` (string) → a própria string.
 * - `ApiError` com `{campo: ["msg", ...]}` (validação DRF) → "campo: msg".
 * - Erro de rede (fetch rejeita → TypeError, sem `body`) → mensagem de conexão.
 * - Qualquer outro caso → mensagem genérica.
 */
export function formatApiError(e: unknown): string {
  if (e instanceof ApiError) {
    const body = e.body;
    if (typeof body === "string" && body.trim()) {
      return body.length > 200 ? `Erro ${e.status}.` : body;
    }
    if (body && typeof body === "object") {
      const obj = body as Record<string, unknown>;
      if (typeof obj.detail === "string") return obj.detail;
      const partes: string[] = [];
      for (const [campo, valor] of Object.entries(obj)) {
        const msgs = Array.isArray(valor) ? valor.map(String) : [String(valor)];
        const texto = msgs.join(" ");
        const rotulo = labelFor(campo);
        partes.push(rotulo ? `${rotulo}: ${texto}` : texto);
      }
      if (partes.length) return partes.join("\n");
    }
    return `Erro ${e.status}.`;
  }
  // fetch rejeita a promise (rede offline, DNS, CORS) com TypeError — sem ApiError.
  if (e instanceof TypeError) {
    return "Sem conexão. Verifique a internet e tente de novo.";
  }
  if (e instanceof Error && e.message) return e.message;
  return "Algo deu errado. Tente novamente.";
}
