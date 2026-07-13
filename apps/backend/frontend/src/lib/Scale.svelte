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
  .lab { display: block; margin: var(--s-3) 0 var(--s-2); }
  .lab > span { display: block; font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--text-muted); margin-bottom: var(--s-2); }
  .val { font-family: var(--display); font-optical-sizing: auto; font-variation-settings: "SOFT" 40;
    font-feature-settings: "tnum" 1; color: var(--accent); font-weight: 500; font-size: 16px; }

  /* Range nativo redesenhado p/ funcionar nas duas bandas: trilho neutro (--surface-3)
     e thumb no acento com anel na cor da superfície — sem o anel, o thumb "flutua"
     sem contraste no papel claro. */
  input[type=range] {
    width: 100%;
    display: block;
    -webkit-appearance: none;
    appearance: none;
    background: transparent;
    cursor: pointer;
  }
  input[type=range]::-webkit-slider-runnable-track {
    height: 4px;
    border-radius: var(--r-pill);
    background: var(--surface-3);
  }
  input[type=range]::-moz-range-track {
    height: 4px;
    border-radius: var(--r-pill);
    background: var(--surface-3);
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    margin-top: -7px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 0 3px var(--surface);
    cursor: pointer;
  }
  input[type=range]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border: none;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 0 3px var(--surface);
    cursor: pointer;
  }
</style>
