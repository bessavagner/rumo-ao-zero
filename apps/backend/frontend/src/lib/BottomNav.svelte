<script lang="ts">
  import { route, go } from "./router.svelte";
  import { abrirCaptura } from "./capture.svelte";

  const ITENS = [
    { path: "/hoje", label: "Início", ic: "⌂" },
    { path: "/progresso", label: "Progresso", ic: "📈" },
    { path: "/registros", label: "Registros", ic: "📋" },
  ];
</script>

<nav class="tabbar">
  {#each ITENS as it}
    <button class="it" class:active={route.path === it.path} onclick={() => go(it.path)}>
      <span class="ic">{it.ic}</span>
      <span class="lb">{it.label}</span>
    </button>
  {/each}
  <button class="plus" onclick={() => abrirCaptura()} aria-label="Registrar">＋</button>
</nav>

<style>
  .tabbar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; align-items: center;
    justify-content: space-around; gap: 4px; background: var(--surface-nav); border-top: 1px solid var(--border);
    padding: 8px 12px calc(10px + env(safe-area-inset-bottom)); max-width: 480px; margin: 0 auto; }
  .it { background: none; border: none; color: var(--text-muted); display: flex; flex-direction: column;
    align-items: center; gap: 2px; font-size: 11px; padding: 4px 8px; }
  .it .ic { font-size: 18px; line-height: 1; }
  .it.active { color: var(--accent); }
  .plus { width: 44px; height: 44px; border-radius: var(--r-md); background: var(--accent);
    color: var(--accent-ink); font-size: 24px; font-weight: 700; border: none; flex-shrink: 0; }
</style>
