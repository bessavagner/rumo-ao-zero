<script lang="ts">
  import { route, go } from "./router.svelte";
  import { abrirCaptura } from "./capture.svelte";

  // `ic` é a chave do ícone SVG desenhado no template (nada de emoji: rende
  // igual em todo device e combina com o resto da identidade).
  const ITENS = [
    { path: "/hoje", label: "Início", ic: "home" },
    { path: "/progresso", label: "Progresso", ic: "trend" },
    { path: "/registros", label: "Registros", ic: "list" },
  ];
</script>

<nav class="tabbar">
  {#each ITENS as it}
    <button class="it" class:active={route.path === it.path} onclick={() => go(it.path)}>
      <span class="ic" aria-hidden="true">
        {#if it.ic === "home"}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 11.5 12 5l8 6.5" /><path d="M6 10.5V19h12v-8.5" />
          </svg>
        {:else if it.ic === "trend"}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="4,8 9,13 13,10 20,16" /><line x1="4" y1="19" x2="20" y2="19" opacity="0.45" />
          </svg>
        {:else}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <line x1="9" y1="7" x2="19" y2="7" /><line x1="9" y1="12" x2="19" y2="12" /><line x1="9" y1="17" x2="19" y2="17" />
            <circle cx="5" cy="7" r="1" fill="currentColor" stroke="none" /><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none" /><circle cx="5" cy="17" r="1" fill="currentColor" stroke="none" />
          </svg>
        {/if}
      </span>
      <span class="lb">{it.label}</span>
    </button>
  {/each}
  <button class="plus" onclick={() => abrirCaptura()} aria-label="Registrar">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="12" y1="6" x2="12" y2="18" /><line x1="6" y1="12" x2="18" y2="12" /></svg>
  </button>
</nav>

<style>
  .tabbar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; align-items: center;
    justify-content: space-around; gap: var(--s-1); background: var(--surface-nav);
    border-top: 1px solid var(--border);
    padding: var(--s-2) var(--s-3) calc(var(--s-3) + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; }
  .it { background: none; border: none; color: var(--text-muted); display: flex; flex-direction: column;
    align-items: center; gap: 3px; font-size: 11px; font-weight: 600; padding: var(--s-1) var(--s-2);
    cursor: pointer; border-radius: var(--r-sm);
    transition: color var(--dur-fast) var(--ease-out); }
  .it .ic { display: grid; place-items: center; }
  .it .ic svg { width: 22px; height: 22px; }
  .it:hover { color: var(--text); }
  .it.active { color: var(--accent); }
  .plus { width: 46px; height: 46px; border-radius: var(--r-md); background: var(--accent);
    color: var(--accent-ink); border: none; flex-shrink: 0; display: grid; place-items: center;
    cursor: pointer; box-shadow: var(--shadow-md);
    transition: transform var(--dur-fast) var(--ease-out); }
  .plus svg { width: 24px; height: 24px; }
  .plus:active { transform: scale(0.94); }
</style>
