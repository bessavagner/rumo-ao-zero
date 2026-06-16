<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import ConfirmDialog from "../../lib/ConfirmDialog.svelte";
  import type { CravingInput, CravingEvent, Substancia3 } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: CravingEvent } = $props();

  const editando = !!registro;
  // Confirmação ao editar registro histórico (criar não pede).
  let confirmar = $state(false);

  // Autocomplete: gatilhos já existentes no mapa (o backend faz get-or-create no salvar).
  let gatilhos = $state<string[]>([]);
  $effect(() => {
    api
      .list<{ nome: string }>("/api/baseline/triggers/")
      .then((p) => (gatilhos = p.results.map((t) => t.nome)))
      .catch(() => {});
  });
  let substancia = $state<Substancia3>(registro?.substancia ?? "alcool");
  let intensidade_pico = $state(registro?.intensidade_pico ?? 6);
  let gatilho_texto = $state(registro?.gatilho_texto ?? "");
  // number-input vazio vira "" em Svelte; tratamos no salvar.
  let duracao_min = $state<number | string>(registro?.duracao_min ?? 0);
  let intensidade_final = $state(registro?.intensidade_final ?? 0);
  let aprendizado = $state(registro?.aprendizado ?? "");
  let erro = $state("");
  let salvando = $state(false);

  async function salvar() {
    if (salvando) return;
    erro = "";
    if (!gatilho_texto.trim()) {
      erro = "Informe o gatilho.";
      return;
    }
    const dur = Number(String(duracao_min).replace(",", ".").trim() || "0");
    if (!Number.isFinite(dur) || dur < 0) {
      erro = "duração: informe minutos ≥ 0.";
      return;
    }
    salvando = true;
    const payload: CravingInput = {
      timestamp: registro?.timestamp ?? new Date().toISOString(),
      substancia,
      intensidade_pico,
      gatilho_texto: gatilho_texto.trim(),
      duracao_min: dur,
      intensidade_final,
      aprendizado: aprendizado.trim() || undefined,
    };
    try {
      if (editando) {
        await api.patch(`/api/log/cravings/${registro!.id}/`, payload);
      } else {
        await api.post("/api/log/cravings/", payload);
      }
      toast.ok(editando ? "Craving atualizado" : "Craving salvo");
      onDone();
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }
</script>

<h2>{editando ? "Editar craving" : "Craving"}</h2>
<label class="lab">Substância</label>
<select class="sel" bind:value={substancia}>
  <option value="alcool">Álcool</option>
  <option value="tabaco">Tabaco</option>
  <option value="ambos">Ambos</option>
</select>
<label class="lab">Intensidade pico: {intensidade_pico}</label>
<input type="range" min="0" max="10" aria-label="Intensidade pico" bind:value={intensidade_pico} />
<label class="lab">Gatilho *</label>
<input class="nota" placeholder="descreva o gatilho" bind:value={gatilho_texto} list="gatilhos-craving" />
<datalist id="gatilhos-craving">
  {#each gatilhos as g}<option value={g}></option>{/each}
</datalist>
<label class="lab">Duração (min)</label>
<input class="nota" type="number" inputmode="numeric" min="0" bind:value={duracao_min} />
<label class="lab">Intensidade final: {intensidade_final}</label>
<input type="range" min="0" max="10" aria-label="Intensidade final" bind:value={intensidade_final} />
<label class="lab">Aprendizado (opcional)</label>
<input class="nota" placeholder="o que aprendi?" bind:value={aprendizado} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" disabled={salvando} onclick={() => (editando ? (confirmar = true) : salvar())}>
  {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar craving"}
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
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .sel { width: 100%; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
