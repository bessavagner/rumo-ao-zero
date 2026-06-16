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
    <PulsoForm onDone={onClose} />
  {:else if aba === "craving"}
    <CravingForm onDone={onClose} />
  {:else if aba === "slip"}
    <SlipForm onDone={onClose} />
  {:else}
    <DailyForm onDone={onClose} />
  {/if}
</div>

<style>
  .dim { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 30; }
  .sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 31; background: var(--surface-2);
    border-radius: var(--r-xl) var(--r-xl) 0 0; padding: 14px 16px calc(24px + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; max-height: 88vh; overflow-y: auto; }
  .grab { width: 36px; height: 4px; background: var(--border-2); border-radius: 3px; margin: 0 auto 14px; }
  .abas { display: flex; gap: 6px; margin-bottom: 14px; }
  .abas button { flex: 1; background: var(--surface); border: 1.5px solid var(--border-2);
    color: var(--text-muted); border-radius: var(--r-sm); padding: 8px 0; font-size: 13px; font-weight: 600; }
  .abas button.active { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
</style>
