<script lang="ts">
  import PulsoForm from "../routes/forms/PulsoForm.svelte";
  import CravingForm from "../routes/forms/CravingForm.svelte";
  import SlipForm from "../routes/forms/SlipForm.svelte";
  import DailyForm from "../routes/forms/DailyForm.svelte";
  import { captura, type AbaCaptura } from "./capture.svelte";

  let { onClose }: { onClose: () => void } = $props();
  // Aba inicial = a pedida por quem abriu (FAB → pulso, chip → tipo do chip).
  let aba = $state<AbaCaptura>(captura.aba);

  const ABAS: { id: AbaCaptura; label: string }[] = [
    { id: "pulso", label: "Pulso" },
    { id: "craving", label: "Craving" },
    { id: "slip", label: "Slip" },
    { id: "daily", label: "Daily" },
  ];
</script>

<div class="dim" onclick={onClose} role="presentation"></div>
<div class="sheet" role="dialog" aria-modal="true" aria-label="Registrar">
  <div class="grab"></div>
  <div class="abas" role="tablist" aria-label="Tipo de registro">
    {#each ABAS as a}
      <button role="tab" aria-selected={aba === a.id} class:active={aba === a.id} onclick={() => (aba = a.id)}>{a.label}</button>
    {/each}
  </div>
  {#if aba === "pulso"}
    <!-- humorInicial vem das carinhas do Início: o form abre com o humor já
         marcado, mas quem salva continua sendo o form. -->
    <PulsoForm onDone={onClose} humorInicial={captura.humorInicial} />
  {:else if aba === "craving"}
    <CravingForm onDone={onClose} />
  {:else if aba === "slip"}
    <SlipForm onDone={onClose} />
  {:else}
    <DailyForm onDone={onClose} />
  {/if}
</div>

<style>
  .dim { position: fixed; inset: 0; background: var(--scrim); z-index: 30; }
  .sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 31; background: var(--bg);
    border-radius: var(--r-xl) var(--r-xl) 0 0;
    padding: var(--s-3) var(--s-4) calc(var(--s-6) + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; max-height: 88vh; overflow-y: auto;
    box-shadow: var(--shadow-md);
    animation: sobe var(--dur-mid) var(--ease-out); }
  @keyframes sobe { from { transform: translateY(12px); opacity: 0; } }
  .grab { width: 36px; height: 4px; background: var(--border-2); border-radius: var(--r-pill); margin: 0 auto var(--s-4); }
  .abas { display: flex; gap: var(--s-1); margin-bottom: var(--s-4);
    background: var(--surface-3); padding: var(--s-1); border-radius: var(--r-pill); }
  .abas button { flex: 1; background: none; border: none;
    color: var(--text-muted); border-radius: var(--r-pill); padding: var(--s-2) 0;
    font-size: 13px; font-weight: 600; cursor: pointer;
    transition: background var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out); }
  .abas button:hover { color: var(--text); }
  .abas button.active { background: var(--accent); color: var(--accent-ink); box-shadow: var(--shadow-sm); }
</style>
