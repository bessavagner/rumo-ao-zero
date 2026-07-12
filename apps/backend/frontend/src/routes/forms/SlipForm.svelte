<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import ConfirmDialog from "../../lib/ConfirmDialog.svelte";
  import GatilhoPicker from "../../lib/GatilhoPicker.svelte";
  import type { SlipInput, Slip, Substancia2 } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: Slip } = $props();

  const editando = !!registro;
  // Confirmação ao editar registro histórico (criar não pede).
  let confirmar = $state(false);

  let substancia = $state<Substancia2>(registro?.substancia ?? "alcool");
  let quantidade = $state(registro?.quantidade ?? "");
  let gatilho = $state(registro?.gatilho ?? "");
  let adicionais = $state<string[]>([...(registro?.gatilhos_adicionais ?? [])]);
  let detalhes = $state(registro?.detalhes ?? "");
  let contexto = $state(registro?.contexto ?? "");
  let reset_streak_alcool = $state(registro?.reset_streak_alcool ?? false);
  let reset_streak_tabaco = $state(registro?.reset_streak_tabaco ?? false);
  let erro = $state("");
  let salvando = $state(false);

  async function salvar() {
    if (salvando) return;
    erro = "";
    if (!gatilho) {
      erro = "Escolha o gatilho.";
      return;
    }
    salvando = true;
    const payload: SlipInput = {
      timestamp: registro?.timestamp ?? new Date().toISOString(),
      substancia,
      gatilho,
      gatilhos_adicionais: adicionais,
      detalhes: detalhes.trim(),
      quantidade: quantidade.trim() || undefined,
      contexto: contexto.trim() || undefined,
      reset_streak_alcool,
      reset_streak_tabaco,
    };
    try {
      if (editando) {
        await api.patch(`/api/log/slips/${registro!.id}/`, payload);
      } else {
        await api.post("/api/log/slips/", payload);
      }
      toast.ok(editando ? "Slip atualizado" : "Slip salvo");
      onDone();
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }
</script>

<h2>{editando ? "Editar slip" : "Slip"}</h2>
<label class="lab">Substância</label>
<select class="sel" bind:value={substancia}>
  <option value="alcool">Álcool</option>
  <option value="tabaco">Tabaco</option>
</select>
<label class="lab">Quantidade (opcional)</label>
<input class="nota" placeholder="ex: 2 cervejas" bind:value={quantidade} />
<GatilhoPicker bind:gatilho bind:adicionais idSelect="sl-gatilho" rotuloPrincipal="Gatilho *" />

<label class="lab" for="sl-detalhes">Detalhes (opcional)</label>
<input id="sl-detalhes" class="nota" placeholder="o que aconteceu, nas suas palavras" bind:value={detalhes} />

<label class="lab">Contexto (opcional)</label>
<textarea class="nota" placeholder="onde estava, com quem..." bind:value={contexto}></textarea>
<div class="checks">
  <label class="check-lab">
    <input type="checkbox" bind:checked={reset_streak_alcool} />
    Resetar streak álcool
  </label>
  <label class="check-lab">
    <input type="checkbox" bind:checked={reset_streak_tabaco} />
    Resetar streak tabaco
  </label>
</div>
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" disabled={salvando} onclick={() => (editando ? (confirmar = true) : salvar())}>
  {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar slip"}
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
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .sel { width: 100%; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; }
  textarea.nota { resize: vertical; min-height: 72px; }
  .checks { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
  .check-lab { display: flex; align-items: center; gap: 8px; font-size: 14px; color: var(--text); cursor: pointer; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
