<script lang="ts">
  import PulsoForm from "../routes/forms/PulsoForm.svelte";
  import CravingForm from "../routes/forms/CravingForm.svelte";
  import SlipForm from "../routes/forms/SlipForm.svelte";
  import DailyForm from "../routes/forms/DailyForm.svelte";
  let { onClose }: { onClose: () => void } = $props();
  let form = $state<"menu" | "pulso" | "craving" | "slip" | "daily">("menu");
</script>

<div class="dim" onclick={onClose} role="presentation"></div>
<div class="sheet" role="dialog" aria-modal="true" aria-label="Registrar">
  {#if form === "menu"}
    <div class="grab"></div>
    <div class="grid">
      <button onclick={() => (form = "pulso")}>💓 Pulso</button>
      <button onclick={() => (form = "craving")}>🌊 Craving</button>
      <button onclick={() => (form = "slip")}>⚠️ Slip</button>
      <button onclick={() => (form = "daily")}>🌙 Daily</button>
    </div>
  {:else if form === "pulso"}
    <PulsoForm onDone={onClose} />
  {:else if form === "craving"}
    <CravingForm onDone={onClose} />
  {:else if form === "slip"}
    <SlipForm onDone={onClose} />
  {:else if form === "daily"}
    <DailyForm onDone={onClose} />
  {/if}
</div>

<style>
  .dim { position: fixed; inset: 0; background: rgba(0,0,0,.5); }
  .sheet { position: fixed; left: 0; right: 0; bottom: 0; background: var(--surface-2);
    border-radius: var(--r-xl) var(--r-xl) 0 0; padding: 14px 16px calc(24px + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; max-height: 88vh; overflow-y: auto; }
  .grab { width: 36px; height: 4px; background: #3a3a44; border-radius: 3px; margin: 0 auto 16px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .grid button { background: var(--surface-3); border: none; color: var(--text); border-radius: var(--r-lg); padding: 18px; font-size: 14px; }
</style>
