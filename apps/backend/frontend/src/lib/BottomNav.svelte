<script lang="ts">
  import { route, go } from "./router.svelte";
  let { onAdd }: { onAdd: () => void } = $props();
</script>

<nav class="tabbar">
  <button class:active={route.path === "/hoje"} onclick={() => go("/hoje")}>Hoje</button>
  <button class="fab" onclick={onAdd} aria-label="Registrar">+</button>
  <button class:active={route.path === "/progresso"} onclick={() => go("/progresso")}>Progresso</button>
</nav>

<style>
  .tabbar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; justify-content: space-around;
    align-items: center; background: #1a1a22; border-top: 1px solid #2a2a32; padding: 8px 0 12px; }
  button { background: none; border: none; color: #8a8a94; font-size: 13px; padding: 6px 18px; }
  button.active { color: #5eead4; }
  .fab { width: 46px; height: 46px; border-radius: 50%; background: #5eead4; color: #0b0b10;
    font-size: 26px; font-weight: 700; margin-top: -28px; box-shadow: 0 4px 14px rgba(94,234,212,.5); }
</style>
