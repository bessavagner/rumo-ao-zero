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
    itens={(dash?.substituicoes_eficacia ?? []).map(s => ({ label: s.rotulo, valor: Math.round(s.taxa_resolucao * 100) }))}
  />
</div>

<style>
  .progresso {
    padding: var(--s-4) var(--s-4) 90px;
    max-width: 480px;
    margin: 0 auto;
  }
  /* Seletor de período — mesmo padrão de segmented control das abas do CaptureSheet:
     trilho tingido (surface-3) com a pílula ativa em accent. */
  .periodo-sel {
    display: flex;
    gap: var(--s-1);
    margin-bottom: var(--s-4);
    background: var(--surface-3);
    padding: var(--s-1);
    border-radius: var(--r-pill);
  }
  .p-btn {
    flex: 1;
    background: none;
    border: none;
    color: var(--text-muted);
    border-radius: var(--r-pill);
    padding: var(--s-2) 0;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background var(--dur-fast) var(--ease-out),
                color var(--dur-fast) var(--ease-out),
                transform var(--dur-fast) var(--ease-out);
  }
  .p-btn:hover {
    color: var(--text);
  }
  .p-btn:active {
    transform: scale(0.97);
  }
  .p-btn.active {
    background: var(--accent);
    color: var(--accent-ink);
    box-shadow: var(--shadow-sm);
  }
  .erro {
    color: var(--danger);
    font-size: 14px;
    margin: 0 0 var(--s-3) 0;
  }
</style>
