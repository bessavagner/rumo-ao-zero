export interface Streak { consecutivo: number; ano: number; }
export interface SituacaoFreq { situacao: string; rotulo: string; ocorrencias: number; }
export interface CategoriaFreq { categoria: string; rotulo: string; ocorrencias: number; }
export interface Coocorrencia {
  situacao: string; rotulo: string; adicional: string; rotulo_adicional: string; ocorrencias: number;
}
export interface TriggersFrequencia {
  por_situacao: SituacaoFreq[];
  por_categoria: CategoriaFreq[];
  coocorrencia: Coocorrencia[];
}
export interface Dashboard {
  dias: number;
  dias_ate_dia1: number;
  streaks: { alcool: Streak; tabaco: Streak };
  dinheiro_economizado: number;
  estados_frequencia: { estado: string; rotulo: string; ocorrencias: number }[];
  triggers_frequencia: TriggersFrequencia;
  substituicoes_eficacia: {
    substituicao: string; rotulo: string; usos: number; taxa_resolucao: number;
    tempo_medio_min: number | null;
  }[];
}
export interface HumorPonto {
  tipo: "pulso" | "daily"; timestamp: string; humor: number; energia: number; craving: number;
}
export interface HumorSeries { dias: number; pontos: HumorPonto[]; }

export type Substancia3 = "alcool" | "tabaco" | "ambos";
export type Substancia2 = "alcool" | "tabaco";

// ── Pulso ────────────────────────────────────────────────────────────────
export interface PulsoInput {
  timestamp: string; humor: number; energia: number; craving?: number;
  estados?: string[]; nota?: string;
}
export interface Pulso {
  id: number;
  timestamp: string;
  humor: number;
  energia: number;
  craving: number;
  estados: string[];
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
  estados: string[];
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
  gatilho: string;
  gatilhos_adicionais?: string[];
  detalhes?: string;
  estados?: string[];
  duracao_min?: number;
  intensidade_final?: number;
  tempo_para_baixar_3?: number | null;
  substituicao?: string;
  substituicao_detalhes?: string;
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
  gatilho: string;
  gatilhos_adicionais: string[];
  detalhes: string;
  categoria: string | null;
  estados: string[];
  pensamento_automatico: string;
  evidencia_favor: string;
  evidencia_contra: string;
  pensamento_balanceado: string;
  substituicao: string;
  substituicao_detalhes: string;
  aprendizado: string;
  if_then_gerado: number | null;
  publicable: boolean;
  created_at: string;
}

// ── Slip ─────────────────────────────────────────────────────────────────
export interface SlipInput {
  timestamp: string;
  substancia: Substancia2;
  gatilho: string;
  gatilhos_adicionais?: string[];
  detalhes?: string;
  quantidade?: string;
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
  gatilho: string;
  gatilhos_adicionais: string[];
  detalhes: string;
  categoria: string | null;
  estados: string[];
  aprendizado: string;
  reset_streak_alcool: boolean;
  reset_streak_tabaco: boolean;
  cooldown_publicacao_ate: string | null;
  created_at: string;
}
