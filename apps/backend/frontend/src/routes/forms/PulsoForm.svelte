<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import type { PulsoInput, Pulso } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: Pulso } = $props();

  const editando = !!registro;
  let humor = $state(registro?.humor ?? 3);
  let energia = $state(registro?.energia ?? 3);
  let craving = $state(registro?.craving ?? 0);
  let nota = $state(registro?.nota ?? "");
  let erro = $state("");
  let salvando = $state(false);

  async function salvar() {
    if (salvando) return;
    erro = "";
    salvando = true;
    const payload: PulsoInput = {
      timestamp: registro?.timestamp ?? new Date().toISOString(),
      humor, energia, craving, nota: nota.trim() || undefined,
    };
    try {
      if (editando) {
        await api.patch(`/api/log/pulsos/${registro!.id}/`, payload);
      } else {
        await api.post("/api/log/pulsos/", payload);
      }
      toast.ok(editando ? "Pulso atualizado" : "Pulso salvo");
      onDone();
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }
</script>

<h2>{editando ? "Editar pulso" : "Pulso"}</h2>
<label class="lab">Humor</label>
<div class="scale" role="radiogroup" aria-label="Humor">
  {#each [1, 2, 3, 4, 5] as n}
    <button role="radio" aria-checked={humor === n} class:on={humor === n} onclick={() => (humor = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Energia</label>
<div class="scale" role="radiogroup" aria-label="Energia">
  {#each [1, 2, 3, 4, 5] as n}
    <button role="radio" aria-checked={energia === n} class:on={energia === n} onclick={() => (energia = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Craving: {craving}</label>
<input type="range" min="0" max="10" aria-label="Craving" bind:value={craving} />
<input class="nota" placeholder="nota (opcional)" bind:value={nota} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" disabled={salvando} onclick={salvar}>
  {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar pulso"}
</button>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  .scale { display: flex; gap: 6px; }
  .scale button { flex: 1; padding: 10px 0; background: var(--surface-3); border: none; color: var(--text); border-radius: var(--r-sm); font-weight: 700; font-size: 16px; }
  .scale button.on { background: var(--accent); color: var(--accent-ink); }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 12px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
