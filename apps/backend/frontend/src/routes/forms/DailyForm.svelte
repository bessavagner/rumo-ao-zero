<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import ConfirmDialog from "../../lib/ConfirmDialog.svelte";
  import type { DailyEntryInput, DailyEntry } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: DailyEntry } = $props();

  const editando = !!registro;
  // Confirmação ao editar registro histórico (criar não pede).
  let confirmar = $state(false);
  let data = $state(registro?.data ?? new Date().toISOString().slice(0, 10));
  let humor = $state(registro?.humor ?? 3);
  let energia = $state(registro?.energia ?? 3);
  let sono_q = $state(registro?.sono_q ?? 3);
  // sono_h vem como string (DecimalField) no output; mantemos como texto p/ aceitar vírgula.
  let sono_h = $state(registro ? String(registro.sono_h) : "7");
  let craving_pico = $state(registro?.craving_pico ?? 0);
  let coisa_boa = $state(registro?.coisa_boa ?? "");
  let coisa_dificil = $state(registro?.coisa_dificil ?? "");
  let erro = $state("");
  let salvando = $state(false);

  async function salvar() {
    if (salvando) return;
    erro = "";
    // Normaliza vírgula→ponto; campo vazio é inválido p/ DecimalField obrigatório.
    const sonoNum = Number(String(sono_h).replace(",", ".").trim());
    if (!Number.isFinite(sonoNum)) {
      erro = "horas de sono: informe um número (ex.: 7.5).";
      return;
    }
    salvando = true;
    const payload: DailyEntryInput = {
      data,
      humor,
      energia,
      sono_q,
      sono_h: sonoNum,
      craving_pico,
      coisa_boa: coisa_boa.trim() || undefined,
      coisa_dificil: coisa_dificil.trim() || undefined,
    };
    try {
      if (editando) {
        // Edita pela id (PATCH no /{id}/); manter a mesma `data` não quebra o unique.
        await api.patch(`/api/log/daily/${registro!.id}/`, payload);
      } else {
        await api.post("/api/log/daily/", payload);
      }
      toast.ok(editando ? "Daily atualizado" : "Daily salvo");
      onDone();
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }
</script>

<h2>{editando ? "Editar daily" : "Daily"}</h2>
<label class="lab">Data</label>
<input class="nota" type="date" bind:value={data} disabled={editando} />
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
<label class="lab">Qualidade do sono</label>
<div class="scale" role="radiogroup" aria-label="Qualidade do sono">
  {#each [1, 2, 3, 4, 5] as n}
    <button role="radio" aria-checked={sono_q === n} class:on={sono_q === n} onclick={() => (sono_q = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Horas de sono</label>
<input class="nota" type="text" inputmode="decimal" placeholder="ex: 7.5" bind:value={sono_h} />
<label class="lab">Craving pico: {craving_pico}</label>
<input type="range" min="0" max="10" aria-label="Craving pico" bind:value={craving_pico} />
<label class="lab">Coisa boa (opcional)</label>
<input class="nota" placeholder="algo positivo do dia" bind:value={coisa_boa} />
<label class="lab">Coisa difícil (opcional)</label>
<input class="nota" placeholder="algo desafiador" bind:value={coisa_dificil} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" disabled={salvando} onclick={() => (editando ? (confirmar = true) : salvar())}>
  {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar daily"}
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
  .scale { display: flex; gap: 6px; }
  .scale button { flex: 1; padding: 10px 0; background: var(--surface-3); border: none; color: var(--text); border-radius: var(--r-sm); font-weight: 700; font-size: 16px; }
  .scale button.on { background: var(--accent); color: var(--accent-ink); }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .nota:disabled { opacity: .6; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
