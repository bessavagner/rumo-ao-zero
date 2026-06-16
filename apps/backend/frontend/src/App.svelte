<script lang="ts">
  import type { Component } from "svelte";
  import { auth } from "./lib/auth.svelte";
  import { route } from "./lib/router.svelte";
  import Login from "./routes/Login.svelte";
  import Hoje from "./routes/Hoje.svelte";
  import Progresso from "./routes/Progresso.svelte";
  import Registros from "./routes/Registros.svelte";
  import BottomNav from "./lib/BottomNav.svelte";
  import CaptureSheet from "./lib/CaptureSheet.svelte";
  import Toast from "./lib/Toast.svelte";

  // Map de rotas simples e escalável (substitui o if/else aninhado).
  const ROTAS: Record<string, Component> = {
    "/hoje": Hoje,
    "/progresso": Progresso,
    "/registros": Registros,
  };
  const Tela = $derived(ROTAS[route.path] ?? Hoje);

  let sheetAberta = $state(false);
</script>

{#if !auth.token}
  <Login />
{:else}
  <main>
    <Tela />
  </main>
  <BottomNav onAdd={() => (sheetAberta = true)} />
  {#if sheetAberta}
    <CaptureSheet onClose={() => (sheetAberta = false)} />
  {/if}
{/if}
<Toast />

<style>
  main { padding: 16px 16px 90px; max-width: 480px; margin: 0 auto; }
  :global(body) { background: #0b0b10; color: #e8e8ee; font-family: system-ui, sans-serif; margin: 0; }
</style>
