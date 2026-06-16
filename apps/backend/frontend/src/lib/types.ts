export interface Streak { consecutivo: number; ano: number; }
export interface Dashboard {
  dias_ate_dia1: number;
  streaks: { alcool: Streak; tabaco: Streak };
  dinheiro_economizado: number;
  estados_frequencia: { estado: string; ocorrencias: number }[];
  triggers_frequencia: { gatilho: string; ocorrencias: number }[];
  substituicoes_eficacia: {
    substituicao: string; usos: number; taxa_resolucao: number; tempo_medio_min: number | null;
  }[];
}
export interface HumorPonto {
  tipo: "pulso" | "daily"; timestamp: string; humor: number; energia: number; craving: number;
}
export interface HumorSeries { dias: number; pontos: HumorPonto[]; }

export interface EstadoInterno { id: number; nome: string; }

export type Substancia3 = "alcool" | "tabaco" | "ambos";
export type Substancia2 = "alcool" | "tabaco";

// ── Pulso ────────────────────────────────────────────────────────────────
export interface PulsoInput {
  timestamp: string; humor: number; energia: number; craving?: number;
  estados?: number[]; nota?: string;
}
export interface Pulso {
  id: number;
  timestamp: string;
  humor: number;
  energia: number;
  craving: number;
  estados: number[];
  nota: string;
  created_at: string;
}

// ── DailyEntry ───────────────────────────────────────────────────────────
export interface DailyEntryInput {
  data: string;
  humor: number;
  energia: number;
  sono_h: number;
  sono_q: number;
  craving_pico?: number;
  coisa_boa?: string;
  coisa_dificil?: string;
}
export interface DailyEntry {
  id: number;
  data: string;
  humor: number;
  energia: number;
  sono_h: string; // DecimalField → string no JSON do DRF
  sono_q: number;
  craving_pico: number;
  estados: number[];
  substituicoes: number[];
  linha_1: string;
  linha_2: string;
  linha_3: string;
  algo_do_corpo: string;
  coisa_boa: string;
  coisa_dificil: string;
  estado_checado: boolean;
  cravings_logados: boolean;
  publicable: boolean;
  publicable_notes: string;
  created_at: string;
  updated_at: string;
}

// ── CravingEvent ─────────────────────────────────────────────────────────
export interface CravingInput {
  timestamp: string;
  substancia: Substancia3;
  intensidade_pico: number;
  gatilho_texto: string;
  duracao_min?: number;
  intensidade_final?: number;
  aprendizado?: string;
}
export interface CravingEvent {
  id: number;
  timestamp: string;
  substancia: Substancia3;
  intensidade_pico: number;
  duracao_min: number;
  intensidade_final: number;
  tempo_para_baixar_3: number | null;
  gatilho_texto: string;
  trigger: number | null;
  estados: number[];
  pensamento_automatico: string;
  evidencia_favor: string;
  evidencia_contra: string;
  pensamento_balanceado: string;
  substituicao_usada: number | null;
  aprendizado: string;
  if_then_gerado: number | null;
  publicable: boolean;
  created_at: string;
}

// ── Slip ─────────────────────────────────────────────────────────────────
export interface SlipInput {
  timestamp: string;
  substancia: Substancia2;
  quantidade?: string;
  gatilho_texto?: string;
  contexto?: string;
  reset_streak_alcool: boolean;
  reset_streak_tabaco: boolean;
}
export interface Slip {
  id: number;
  timestamp: string;
  substancia: Substancia2;
  quantidade: string;
  contexto: string;
  gatilho_texto: string;
  trigger: number | null;
  aprendizado: string;
  reset_streak_alcool: boolean;
  reset_streak_tabaco: boolean;
  cooldown_publicacao_ate: string | null;
  created_at: string;
}
