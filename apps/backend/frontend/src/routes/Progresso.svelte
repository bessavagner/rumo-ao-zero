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
      api.get<Dashboard>(`/api/dashboard/?dias=${dias}`),
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
    titulo={`Gatilhos — situações (${periodo}d)`}
    itens={(dash?.triggers_frequencia.por_situacao ?? []).map(t => ({ label: t.rotulo, valor: t.ocorrencias }))}
  />
  <FreqBars
    titulo="Gatilhos — categorias clínicas"
    itens={(dash?.triggers_frequencia.por_categoria ?? []).map(c => ({ label: c.rotulo, valor: c.ocorrencias }))}
  />
  <FreqBars
    titulo="Estados"
    itens={(dash?.estados_frequencia ?? []).map(e => ({ label: e.rotulo, valor: e.ocorrencias }))}
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
  .periodo-sel {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }
  .p-btn {
    flex: 1;
    background: var(--surface);
    border: 1.5px solid var(--border-2);
    color: var(--indigo-soft);
    border-radius: var(--r-sm);
    padding: 8px 0;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
  }
  .p-btn.active {
    background: var(--indigo);
    border-color: var(--indigo);
    color: #fff;
  }
  .erro {
    color: var(--danger);
    font-size: 14px;
    margin: 0 0 12px 0;
  }
</style>
