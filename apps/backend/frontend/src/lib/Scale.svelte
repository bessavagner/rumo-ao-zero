<script lang="ts">
  // Escala subjetiva 0–10 (humor/energia/sono_q/craving). Slider + badge com o valor.
  // Unifica todos os campos numéricos do app numa faixa/visual só (decisão: escala 0–10).
  interface Props { label: string; value: number; }
  let { label, value = $bindable() }: Props = $props();
</script>

<label class="lab">
  <span>{label}: <span class="val">{value}</span></span>
  <input type="range" min="0" max="10" step="1" aria-label={label} bind:value />
</label>

<style>
  .lab { display: block; margin: 12px 0 6px; }
  .lab > span { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin-bottom: 6px; }
  .val { color: var(--accent); font-weight: 700; font-size: 13px; }
  input[type=range] { width: 100%; display: block; }
</style>
