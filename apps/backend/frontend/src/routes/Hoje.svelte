<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import type { Dashboard } from "../lib/types";

  let dash = $state<Dashboard | null>(null);
  let erro = $state("");

  $effect(() => {
    api.get<Dashboard>("/api/dashboard/")
      .then((d) => (dash = d))
      .catch((e) => (erro = formatApiError(e)));
  });
</script>

<h1>Hoje</h1>
{#if erro}<p class="erro">{erro}</p>{/if}
{#if dash}
  <div class="stat-row">
    <div class="stat"><div class="n">{dash.streaks.alcool.consecutivo}</div><div class="l">s/ álcool</div></div>
    <div class="stat"><div class="n">{dash.streaks.tabaco.consecutivo}</div><div class="l">s/ tabaco</div></div>
  </div>
  <div class="money">
    <div class="n">R$ {dash.dinheiro_economizado.toFixed(0)}</div>
    <div class="l">economizado</div>
  </div>
  {#if dash.dias_ate_dia1 > 0}
    <p class="aviso">Faltam {dash.dias_ate_dia1} dias para a Data Zero.</p>
  {/if}
{:else if !erro}
  <p>Carregando…</p>
{/if}

<style>
  .stat-row { display: flex; gap: 10px; margin-bottom: 10px; }
  .stat, .money { flex: 1; background: #1e1e27; border-radius: 14px; padding: 14px; }
  .n { font-size: 26px; font-weight: 800; color: #5eead4; }
  .money .n { color: #fbbf24; }
  .l { font-size: 11px; opacity: .6; text-transform: uppercase; letter-spacing: .04em; }
  .erro { color: #f87171; } .aviso { opacity: .7; font-size: 14px; }
</style>
