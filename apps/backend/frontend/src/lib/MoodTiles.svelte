<script lang="ts">
  // "Como você está agora?" — a primeira coisa da tela, porque registrar o humor
  // é a ação que você mais repete. Cada carinha abre a captura na aba Pulso já
  // com o humor marcado; ela NÃO salva sozinha (o form continua sendo o lugar
  // onde o registro acontece — energia, craving e nota entram lá).
  //
  // Rostos desenhados em SVG, não emoji: renderizam igual em todo device e
  // seguem o traço do resto do app.
  import { abrirCaptura } from "./capture.svelte";

  const CARINHAS = [
    { humor: 1, label: "difícil", curva: "M8 17 Q12 13.5 16 17" },
    { humor: 3, label: "baixo",   curva: "M8 16.4 Q12 14.6 16 16.4" },
    { humor: 5, label: "neutro",  curva: "M8.5 15.6 H15.5" },
    { humor: 7, label: "bem",     curva: "M8 14.6 Q12 16.6 16 14.6" },
    { humor: 9, label: "ótimo",   curva: "M7.6 14 Q12 17.6 16.4 14" },
  ];
</script>

<section class="humor" aria-labelledby="humor-h">
  <h2 id="humor-h">Como você está agora?</h2>
  <div class="tiles">
    {#each CARINHAS as c}
      <button
        class="tile"
        onclick={() => abrirCaptura("pulso", c.humor)}
        aria-label="Registrar pulso com humor {c.humor} de 10 — {c.label}"
      >
        <span class="rosto" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
            <circle cx="9" cy="10" r="1.05" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="1.05" fill="currentColor" stroke="none" />
            <path d={c.curva} />
          </svg>
        </span>
        <span class="lb">{c.label}</span>
      </button>
    {/each}
  </div>
</section>

<style>
  .humor { margin-bottom: var(--s-6); }
  h2 { font-size: 19px; margin-bottom: var(--s-3); }

  .tiles { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: var(--s-2); }

  .tile {
    display: flex; flex-direction: column; align-items: center; gap: var(--s-2);
    background: none; border: none; padding: 0; cursor: pointer;
    color: var(--text-muted);
    transition: color var(--dur-fast) var(--ease-out);
  }
  .rosto {
    display: grid; place-items: center;
    width: 100%; aspect-ratio: 1; max-width: 60px;
    border-radius: var(--r-pill);
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    box-shadow: var(--shadow-sm);
    transition: transform var(--dur-fast) var(--ease-out),
                background var(--dur-fast) var(--ease-out),
                border-color var(--dur-fast) var(--ease-out),
                color var(--dur-fast) var(--ease-out);
  }
  .rosto svg { width: 62%; height: 62%; }

  .lb { font-size: 11px; font-weight: 600; letter-spacing: 0.02em; }

  /* Estados. O hover é dica; o :active é a confirmação física do toque. */
  .tile:hover .rosto,
  .tile:focus-visible .rosto { background: var(--accent-soft); border-color: var(--accent); }
  .tile:hover, .tile:focus-visible { color: var(--text); }
  .tile:active .rosto { transform: scale(0.94); background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }

  .tile:focus-visible { outline: none; }
  .tile:focus-visible .rosto { outline: 2px solid var(--accent); outline-offset: 2px; }
</style>
