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

export interface PulsoInput {
  timestamp: string; humor: number; energia: number; craving?: number;
  estados?: number[]; nota?: string;
}
export interface EstadoInterno { id: number; nome: string; }
