<script lang="ts">
  import type { HumorPonto } from "../types";

  interface Props { pontos: HumorPonto[]; mini?: boolean; }
  let { pontos, mini = false }: Props = $props();

  const W = 320;
  const H = $derived(mini ? 90 : 140);
  const PAD = $derived(mini ? { top: 8, right: 8, bottom: 16, left: 22 } : { top: 12, right: 12, bottom: 24, left: 28 });

  const innerW = $derived(W - PAD.left - PAD.right);
  const innerH = $derived(H - PAD.top - PAD.bottom);

  const yMin = 0;
  const yMax = 10;

  function xPos(i: number, total: number): number {
    if (total <= 1) return PAD.left + innerW / 2;
    return PAD.left + (i / (total - 1)) * innerW;
  }
  function yPos(v: number): number {
    return PAD.top + innerH - ((v - yMin) / (yMax - yMin)) * innerH;
  }

  const polyline = $derived(
    pontos.length > 0
      ? pontos.map((p, i) => `${xPos(i, pontos.length)},${yPos(p.humor)}`).join(" ")
      : ""
  );
  const yTicks = [0, 2, 4, 6, 8, 10];
  const labelFirst = $derived(pontos.length > 0 ? pontos[0].timestamp.slice(0, 10) : "");
  const labelLast = $derived(pontos.length > 1 ? pontos[pontos.length - 1].timestamp.slice(0, 10) : "");
</script>

<div class="humor-curve" class:mini={mini}>
  <!-- Um card sem rótulo é um card mudo: no painel a curva também se apresenta. -->
  <h3 class="titulo">{mini ? "Humor (7 dias)" : "Humor ao longo do tempo"}</h3>
  {#if pontos.length === 0}
    <p class="vazio">sem dados ainda</p>
  {:else}
    <svg viewBox="0 0 {W} {H}" class="chart-svg" aria-label="Curva de humor">
      {#each yTicks as tick}
        <line class="grid" class:zero={tick === 0} x1={PAD.left} y1={yPos(tick)} x2={PAD.left + innerW} y2={yPos(tick)} />
        <text x={PAD.left - 4} y={yPos(tick)} class="axis-label" class:zero={tick === 0} text-anchor="end" dominant-baseline="middle">{tick}</text>
      {/each}
      <polyline class="linha" points={polyline} fill="none" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
      {#each pontos as p, i}
        <circle class="ponto" cx={xPos(i, pontos.length)} cy={yPos(p.humor)} r="3.5" />
      {/each}
      {#if labelFirst}
        <text x={PAD.left} y={H - 4} class="axis-label" text-anchor="start">{labelFirst}</text>
      {/if}
      {#if labelLast && pontos.length > 1}
        <text x={PAD.left + innerW} y={H - 4} class="axis-label" text-anchor="end">{labelLast}</text>
      {/if}
    </svg>
  {/if}
</div>

<style>
  .humor-curve {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: var(--s-4) var(--s-5);
    margin-bottom: var(--s-3);
    box-shadow: var(--shadow-sm);
  }
  .titulo {
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .08em;
    color: var(--text-muted); margin: 0 0 var(--s-3) 0;
  }
  .vazio { font-size: 13px; color: var(--text-muted); margin: 0; padding-bottom: var(--s-1); }
  .chart-svg { width: 100%; height: auto; display: block; }
  .axis-label { font-size: 9px; fill: var(--text-muted); font-family: inherit; }
  .axis-label.zero { fill: var(--accent); font-weight: 600; }
  .grid { stroke: var(--border); stroke-width: 1; }
  /* A "linha do zero": eixo 0 destacado em sage — a meta, a assinatura do app. */
  .grid.zero { stroke: var(--accent-dim); stroke-width: 1.5; }
  .linha { stroke: var(--accent); }
  /* O contorno do ponto é a cor do card (não a do fundo da página): o card
     agora é mais claro que o papel no tema claro. */
  .ponto { fill: var(--accent); stroke: var(--surface); stroke-width: 1.5; }
</style>
