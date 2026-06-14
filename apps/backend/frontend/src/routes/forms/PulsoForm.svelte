<script lang="ts">
  import { api } from "../../lib/api";
  import type { PulsoInput } from "../../lib/types";

  let { onDone }: { onDone: () => void } = $props();
  let humor = $state(3);
  let energia = $state(3);
  let craving = $state(0);
  let nota = $state("");
  let erro = $state("");

  async function salvar() {
    erro = "";
    const payload: PulsoInput = {
      timestamp: new Date().toISOString(),
      humor, energia, craving, nota: nota || undefined,
    };
    try {
      await api.post("/api/log/pulsos/", payload);
      onDone();
    } catch {
      erro = "Não consegui salvar.";
    }
  }
</script>

<h2>Pulso</h2>
<label class="lab">Humor</label>
<div class="scale">
  {#each [1, 2, 3, 4, 5] as n}
    <button class:on={humor === n} onclick={() => (humor = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Energia</label>
<div class="scale">
  {#each [1, 2, 3, 4, 5] as n}
    <button class:on={energia === n} onclick={() => (energia = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Craving: {craving}</label>
<input type="range" min="0" max="10" bind:value={craving} />
<input class="nota" placeholder="nota (opcional)" bind:value={nota} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" onclick={salvar}>Salvar pulso</button>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  .scale { display: flex; gap: 6px; }
  .scale button { flex: 1; padding: 10px 0; background: #26262f; border: none; color: #e8e8ee; border-radius: 10px; font-weight: 700; }
  .scale button.on { background: #5eead4; color: #0b0b10; }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 12px; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: #5eead4; color: #0b0b10; border: none; border-radius: 12px; font-weight: 700; }
  .erro { color: #f87171; }
</style>
