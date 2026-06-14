<script lang="ts">
  import type { HumorPonto } from "../types";

  interface Props { pontos: HumorPonto[]; }
  let { pontos }: Props = $props();

  // SVG dimensions
  const W = 320;
  const H = 140;
  const PAD = { top: 12, right: 12, bottom: 24, left: 28 };

  const innerW = $derived(W - PAD.left - PAD.right);
  const innerH = $derived(H - PAD.top - PAD.bottom);

  // Y: humor scale 1–5
  const yMin = 1;
  const yMax = 5;

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

  // Y-axis ticks: 1, 2, 3, 4, 5
  const yTicks = [1, 2, 3, 4, 5];

  // X-axis: show first and last label
  const labelFirst = $derived(pontos.length > 0 ? pontos[0].timestamp.slice(0, 10) : "");
  const labelLast = $derived(pontos.length > 1 ? pontos[pontos.length - 1].timestamp.slice(0, 10) : "");
</script>

<div class="humor-curve">
  <h3 class="titulo">Humor ao longo do tempo</h3>
  {#if pontos.length === 0}
    <p class="vazio">sem dados ainda</p>
  {:else}
    <svg viewBox="0 0 {W} {H}" class="chart-svg" aria-label="Curva de humor">
      <!-- Y grid lines + labels -->
      {#each yTicks as tick}
        <line
          x1={PAD.left} y1={yPos(tick)}
          x2={PAD.left + innerW} y2={yPos(tick)}
          stroke="#2a2a38" stroke-width="1"
        />
        <text x={PAD.left - 4} y={yPos(tick)} class="axis-label" text-anchor="end" dominant-baseline="middle">{tick}</text>
      {/each}

      <!-- Humor polyline -->
      <polyline
        points={polyline}
        fill="none"
        stroke="#6366f1"
        stroke-width="2.5"
        stroke-linejoin="round"
        stroke-linecap="round"
      />

      <!-- Data points -->
      {#each pontos as p, i}
        <circle
          cx={xPos(i, pontos.length)}
          cy={yPos(p.humor)}
          r="3.5"
          fill="#6366f1"
          stroke="#12121a"
          stroke-width="1.5"
        />
      {/each}

      <!-- X-axis labels -->
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
    background: #1e1e27;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
  }
  .titulo {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #a5b4fc;
    margin: 0 0 10px 0;
  }
  .vazio {
    font-size: 13px;
    color: #6b6b80;
    margin: 0;
    padding-bottom: 4px;
  }
  .chart-svg {
    width: 100%;
    height: auto;
    display: block;
  }
  .axis-label {
    font-size: 9px;
    fill: #6b6b80;
    font-family: inherit;
  }
</style>
