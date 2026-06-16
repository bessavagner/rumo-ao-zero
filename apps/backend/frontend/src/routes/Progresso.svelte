<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import type { Dashboard, HumorSeries } from "../lib/types";
  import HumorCurve from "../lib/charts/HumorCurve.svelte";
  import FreqBars from "../lib/charts/FreqBars.svelte";

  let periodo = $state(30);
  let serie = $state<HumorSeries | null>(null);
  let dash = $state<Dashboard | null>(null);
  let erro = $state("");

  $effect(() => {
    // Reading `periodo` inside the effect so it tracks changes
    const dias = periodo;
    erro = "";
    Promise.all([
      api.get<HumorSeries>(`/api/series/humor/?dias=${dias}`),
      api.get<Dashboard>("/api/dashboard/"),
    ])
      .then(([s, d]) => {
        serie = s;
        dash = d;
      })
      .catch((e) => {
        erro = formatApiError(e);
      });
  });
</script>

<div class="progresso">
  <h1>Progresso</h1>

  <!-- Period selector -->
  <div class="periodo-sel">
    {#each [7, 30, 90] as p}
      <button
        class="p-btn"
        class:active={periodo === p}
        onclick={() => (periodo = p)}
      >{p}d</button>
    {/each}
  </div>

  {#if erro}
    <p class="erro">{erro}</p>
  {/if}

  <!-- Humor curve -->
  <HumorCurve pontos={serie?.pontos ?? []} />

  <!-- Frequency bars -->
  <FreqBars
    titulo="Gatilhos"
    itens={(dash?.triggers_frequencia ?? []).map(t => ({ label: t.gatilho, valor: t.ocorrencias }))}
  />
  <FreqBars
    titulo="Estados"
    itens={(dash?.estados_frequencia ?? []).map(e => ({ label: e.estado, valor: e.ocorrencias }))}
  />
  <FreqBars
    titulo="Substituições (taxa)"
    itens={(dash?.substituicoes_eficacia ?? []).map(s => ({ label: s.substituicao, valor: Math.round(s.taxa_resolucao * 100) }))}
  />
</div>

<style>
  .progresso {
    padding: 16px 16px 90px;
    max-width: 480px;
    margin: 0 auto;
  }
  h1 {
    font-size: 22px;
    font-weight: 800;
    color: #e8e8ee;
    margin: 0 0 16px 0;
  }
  .periodo-sel {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }
  .p-btn {
    flex: 1;
    background: #1e1e27;
    border: 1.5px solid #2a2a38;
    color: #a5b4fc;
    border-radius: 10px;
    padding: 8px 0;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
  }
  .p-btn.active {
    background: #6366f1;
    border-color: #6366f1;
    color: #fff;
  }
  .erro {
    color: #f87171;
    font-size: 14px;
    margin: 0 0 12px 0;
  }
</style>
