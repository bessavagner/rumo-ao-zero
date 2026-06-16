<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import { abrirCaptura } from "../lib/capture.svelte";
  import type { Dashboard, HumorSeries } from "../lib/types";
  import HumorCurve from "../lib/charts/HumorCurve.svelte";
  import FreqBars from "../lib/charts/FreqBars.svelte";

  let dash = $state<Dashboard | null>(null);
  let serie = $state<HumorSeries | null>(null);
  let erro = $state("");

  $effect(() => {
    Promise.all([
      api.get<Dashboard>("/api/dashboard/"),
      api.get<HumorSeries>("/api/series/humor/?dias=7"),
    ])
      .then(([d, s]) => { dash = d; serie = s; })
      .catch((e) => (erro = formatApiError(e)));
  });

  const gatilhos = $derived(
    (dash?.triggers_frequencia ?? []).map((t) => ({ label: t.gatilho, valor: t.ocorrencias }))
  );
</script>

<h1>Início</h1>
{#if erro}<p class="erro">{erro}</p>{/if}
{#if dash}
  <div class="stat-row">
    <div class="stat"><div class="n">{dash.streaks.alcool.consecutivo}</div><div class="l">s/ álcool</div></div>
    <div class="stat"><div class="n">{dash.streaks.tabaco.consecutivo}</div><div class="l">s/ tabaco</div></div>
    <div class="stat money"><div class="n">R$ {dash.dinheiro_economizado.toFixed(0)}</div><div class="l">economizado</div></div>
  </div>
  {#if dash.dias_ate_dia1 > 0}
    <p class="aviso">Faltam {dash.dias_ate_dia1} dias para a Data Zero.</p>
  {/if}

  <HumorCurve pontos={serie?.pontos ?? []} mini />
  <FreqBars titulo="Gatilhos da semana" itens={gatilhos} compacto />

  <div class="chips">
    <button class="chip" onclick={() => abrirCaptura("pulso")}>+ Pulso</button>
    <button class="chip" onclick={() => abrirCaptura("craving")}>+ Craving</button>
    <button class="chip" onclick={() => abrirCaptura("slip")}>+ Slip</button>
  </div>
{:else if !erro}
  <p>Carregando…</p>
{/if}

<style>
  .stat-row { display: flex; gap: 10px; margin-bottom: 10px; }
  .stat { flex: 1; background: var(--surface); border-radius: var(--r-lg); padding: 14px; }
  .n { font-size: 22px; font-weight: 800; color: var(--accent); }
  .stat.money .n { color: var(--warn); font-size: 18px; }
  .l { font-size: 11px; opacity: .6; text-transform: uppercase; letter-spacing: .04em; }
  .erro { color: var(--danger); } .aviso { opacity: .7; font-size: 14px; margin-bottom: 10px; }
  .chips { display: flex; gap: 8px; margin-top: 4px; }
  .chip { flex: 1; background: var(--surface-3); border: 1px solid var(--border-2); color: var(--accent);
    border-radius: 999px; padding: 10px 8px; font-size: 13px; font-weight: 600; }
</style>
