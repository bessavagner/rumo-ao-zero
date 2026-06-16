<script lang="ts">
  import { route, go } from "./router.svelte";
  let { onAdd }: { onAdd: () => void } = $props();
</script>

<nav class="tabbar">
  <button class:active={route.path === "/hoje"} onclick={() => go("/hoje")}>Hoje</button>
  <button class:active={route.path === "/registros"} onclick={() => go("/registros")}>Registros</button>
  <button class="fab" onclick={onAdd} aria-label="Registrar">+</button>
  <button class:active={route.path === "/progresso"} onclick={() => go("/progresso")}>Progresso</button>
</nav>

<style>
  .tabbar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; justify-content: space-around;
    align-items: center; background: var(--surface-nav); border-top: 1px solid var(--border);
    padding: 8px 0 calc(12px + env(safe-area-inset-bottom)); }
  button { background: none; border: none; color: var(--text-muted); font-size: 13px; padding: 6px 12px; }
  button.active { color: var(--accent); }
  .fab { width: 46px; height: 46px; border-radius: 50%; background: var(--accent); color: var(--accent-ink);
    font-size: 26px; font-weight: 700; margin-top: -28px; box-shadow: 0 4px 14px rgba(94,234,212,.5); }
</style>
