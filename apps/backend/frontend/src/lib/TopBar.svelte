<script lang="ts">
  // Barra fina de topo: a marca à esquerda, a banda de cor à direita. É a única
  // chrome persistente acima do conteúdo — o <h1> de cada rota continua sendo o
  // título da tela.
  import { alternarTema, bandaEfetiva, tema } from "./theme.svelte";

  // Lê `tema.banda` para reagir à troca; resolve "sistema" para o que está na tela.
  const escuro = $derived((tema.banda, bandaEfetiva() === "dark"));
</script>

<header class="topbar">
  <span class="marca">Rumo ao Zero</span>
  <button
    class="tema"
    onclick={alternarTema}
    aria-label={escuro ? "Usar tema claro" : "Usar tema escuro"}
    title={escuro ? "Tema claro" : "Tema escuro"}
  >
    {#if escuro}
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6L17 7M7 17l-1.4 1.4" />
      </svg>
    {:else}
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.8 6.8 0 0 0 10.5 10.5z" />
      </svg>
    {/if}
  </button>
</header>

<style>
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    max-width: 480px; margin: 0 auto;
    padding: var(--s-3) var(--s-4) 0;
  }
  .marca {
    font-family: var(--display);
    font-optical-sizing: auto;
    font-variation-settings: "SOFT" 60, "opsz" 14;
    font-size: 13px; font-weight: 500;
    letter-spacing: 0.02em;
    color: var(--text-muted);
  }
  .tema {
    display: grid; place-items: center;
    width: 36px; height: 36px;
    border-radius: var(--r-pill);
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-muted);
    cursor: pointer;
    transition: color var(--dur-fast) var(--ease-out),
                border-color var(--dur-fast) var(--ease-out),
                transform var(--dur-fast) var(--ease-out);
  }
  .tema svg { width: 18px; height: 18px; }
  .tema:hover { color: var(--accent); border-color: var(--accent); }
  .tema:active { transform: scale(0.94); }
</style>
