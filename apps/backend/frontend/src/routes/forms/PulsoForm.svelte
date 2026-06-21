<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import ConfirmDialog from "../../lib/ConfirmDialog.svelte";
  import Scale from "../../lib/Scale.svelte";
  import type { PulsoInput, Pulso } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: Pulso } = $props();

  const editando = !!registro;
  // Confirmação ao editar registro histórico (criar não pede).
  let confirmar = $state(false);
  let humor = $state(registro?.humor ?? 5);
  let energia = $state(registro?.energia ?? 5);
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
<Scale label="Humor" bind:value={humor} />
<Scale label="Energia" bind:value={energia} />
<Scale label="Craving" bind:value={craving} />
<input class="nota" placeholder="nota (opcional)" bind:value={nota} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" disabled={salvando} onclick={() => (editando ? (confirmar = true) : salvar())}>
  {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar pulso"}
</button>

{#if confirmar}
  <ConfirmDialog
    titulo="Salvar alterações neste registro?"
    sub="Editar um registro histórico altera seus dados e pode afetar suas métricas e sua trajetória."
    confirmLabel="Salvar"
    onConfirm={() => { confirmar = false; salvar(); }}
    onCancel={() => (confirmar = false)}
  />
{/if}

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  .nota { width: 100%; margin-top: 12px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
