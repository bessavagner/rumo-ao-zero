<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import { abrirCaptura } from "../lib/capture.svelte";
  import type { Dashboard, HumorSeries } from "../lib/types";
  import HumorCurve from "../lib/charts/HumorCurve.svelte";
  import FreqBars from "../lib/charts/FreqBars.svelte";
  import MoodTiles from "../lib/MoodTiles.svelte";

  let dash = $state<Dashboard | null>(null);
  let serie = $state<HumorSeries | null>(null);
  let erro = $state("");

  const DIAS = 7; // a tela do Início fala da semana — então é a semana que ela pede.

  const hoje = new Intl.DateTimeFormat("pt-BR", {
    weekday: "long", day: "numeric", month: "long",
  }).format(new Date());

  $effect(() => {
    Promise.all([
      api.get<Dashboard>(`/api/dashboard/?dias=${DIAS}`),
      api.get<HumorSeries>(`/api/series/humor/?dias=${DIAS}`),
    ])
      .then(([d, s]) => { dash = d; serie = s; })
      .catch((e) => (erro = formatApiError(e)));
  });

  const gatilhos = $derived(
    (dash?.triggers_frequencia.por_situacao ?? []).map((t) => ({
      label: t.rotulo,
      valor: t.ocorrencias,
    }))
  );
</script>

<h1>Início</h1>
<p class="data">{hoje}</p>

{#if erro}<p class="erro">{erro}</p>{/if}

{#if dash}
  {#if dash.dias_ate_dia1 > 0}
    <p class="aviso">Faltam {dash.dias_ate_dia1} dias para a Data Zero.</p>
  {/if}

  <MoodTiles />

  <!-- Voz 1 — card preenchido: a sequência é o que o app existe para mostrar.
       Um preenchido por tela; tudo abaixo dele é mais quieto. -->
  <section class="streaks">
    <p class="eyebrow sobre-acento">Sequência</p>
    <div class="dupla">
      <div class="streak">
        <span class="n">{dash.streaks.alcool.consecutivo}</span>
        <span class="l">dias sem álcool</span>
      </div>
      <div class="streak">
        <span class="n">{dash.streaks.tabaco.consecutivo}</span>
        <span class="l">dias sem tabaco</span>
      </div>
    </div>
  </section>

  <!-- Voz 2 — card tingido: o dinheiro é consequência, não a meta. -->
  <section class="dinheiro">
    <div>
      <p class="eyebrow">Economizado</p>
      <span class="n">R$ {dash.dinheiro_economizado.toFixed(0)}</span>
    </div>
    <span class="moeda" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="8.5" />
        <path d="M12 7.5v9M14.5 9.6c-.6-.7-1.5-1-2.5-1-1.4 0-2.4.7-2.4 1.8 0 2.6 5 1.2 5 3.8 0 1.2-1.1 1.9-2.6 1.9-1.1 0-2-.4-2.6-1.1" />
      </svg>
    </span>
  </section>

  <!-- Voz 3 — cards planos: os dados que você lê, não celebra. -->
  <HumorCurve pontos={serie?.pontos ?? []} mini />
  <FreqBars titulo={`Gatilhos (${dash.dias} dias)`} itens={gatilhos} compacto />

  <p class="eyebrow rotulo-chips">Registrar</p>
  <div class="chips">
    <button class="chip" onclick={() => abrirCaptura("craving")}>Craving</button>
    <button class="chip" onclick={() => abrirCaptura("slip")}>Slip</button>
    <button class="chip" onclick={() => abrirCaptura("daily")}>Daily</button>
  </div>
{:else if !erro}
  <p class="carregando">Carregando…</p>
{/if}

<style>
  .data {
    color: var(--text-muted); font-size: 13px;
    margin: calc(-1 * var(--s-3)) 0 var(--s-5);
    text-transform: lowercase;
  }
  .erro { color: var(--danger); }
  .aviso {
    background: var(--blush); color: var(--blush-ink);
    border-radius: var(--r-md); padding: var(--s-3) var(--s-4);
    font-size: 14px; margin-bottom: var(--s-5);
  }

  /* Card preenchido — a sequência. */
  .streaks {
    background: var(--accent); color: var(--accent-ink);
    border-radius: var(--r-xl); padding: var(--s-5);
    margin-bottom: var(--s-3);
    box-shadow: var(--shadow-md);
  }
  .sobre-acento { color: var(--accent-ink); opacity: 0.72; margin-bottom: var(--s-3); }
  /* Duas colunas iguais; o fio divisor é a borda da segunda (um ::before em
     grid disputa a auto-colocação e desalinhava os números). */
  .dupla { display: grid; grid-template-columns: 1fr 1fr; }
  .streak { min-width: 0; }
  .streak + .streak {
    padding-left: var(--s-4);
    margin-left: var(--s-4);
    border-left: 1px solid currentColor;
    border-color: color-mix(in oklab, currentColor 22%, transparent);
  }
  .streak .n {
    display: block;
    font-family: var(--display); font-optical-sizing: auto; font-weight: 500;
    font-variation-settings: "SOFT" 40, "opsz" 40;
    font-feature-settings: "tnum" 1;
    font-size: 44px; line-height: 1; letter-spacing: -1px;
  }
  .streak .l {
    display: block; margin-top: var(--s-2);
    font-size: 12px; font-weight: 600; opacity: 0.78;
    overflow-wrap: anywhere;
  }

  /* Card tingido — o dinheiro. */
  .dinheiro {
    display: flex; align-items: center; justify-content: space-between; gap: var(--s-4);
    background: var(--sand-soft);
    border-radius: var(--r-lg); padding: var(--s-4) var(--s-5);
    margin-bottom: var(--s-3);
  }
  .dinheiro .eyebrow { color: var(--sand); opacity: 0.9; margin-bottom: var(--s-1); }
  .dinheiro .n {
    font-family: var(--display); font-optical-sizing: auto; font-weight: 500;
    font-variation-settings: "SOFT" 40, "opsz" 32;
    font-feature-settings: "tnum" 1;
    font-size: 28px; line-height: 1.1; letter-spacing: -0.5px;
    color: var(--sand);
  }
  .moeda { display: grid; place-items: center; color: var(--sand); opacity: 0.5; flex-shrink: 0; }
  .moeda svg { width: 30px; height: 30px; }

  .rotulo-chips { display: block; margin: var(--s-6) 0 var(--s-3); }
  .chips { display: flex; gap: var(--s-2); }
  .chip {
    flex: 1;
    background: var(--surface); border: 1px solid var(--border-2); color: var(--text);
    border-radius: var(--r-pill); padding: var(--s-3) var(--s-2);
    font-size: 13px; font-weight: 600; cursor: pointer;
    box-shadow: var(--shadow-sm);
    transition: background var(--dur-fast) var(--ease-out),
                border-color var(--dur-fast) var(--ease-out),
                transform var(--dur-fast) var(--ease-out);
  }
  .chip:hover { background: var(--accent-soft); border-color: var(--accent); }
  .chip:active { transform: scale(0.97); }

  .carregando { color: var(--text-muted); }
</style>
