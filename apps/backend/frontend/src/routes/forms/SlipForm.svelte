<script lang="ts">
  import { api } from "../../lib/api";

  let { onDone }: { onDone: () => void } = $props();
  let substancia = $state<"alcool" | "tabaco">("alcool");
  let quantidade = $state("");
  let gatilho_texto = $state("");
  let contexto = $state("");
  let reset_streak_alcool = $state(false);
  let reset_streak_tabaco = $state(false);
  let erro = $state("");

  async function salvar() {
    erro = "";
    const payload: Record<string, unknown> = {
      timestamp: new Date().toISOString(),
      substancia,
      quantidade: quantidade.trim() || undefined,
      gatilho_texto: gatilho_texto.trim() || undefined,
      contexto: contexto.trim() || undefined,
      reset_streak_alcool,
      reset_streak_tabaco,
    };
    try {
      await api.post("/api/log/slips/", payload);
      onDone();
    } catch {
      erro = "Não consegui salvar.";
    }
  }
</script>

<h2>Slip</h2>
<label class="lab">Substância</label>
<select class="sel" bind:value={substancia}>
  <option value="alcool">Álcool</option>
  <option value="tabaco">Tabaco</option>
</select>
<label class="lab">Quantidade (opcional)</label>
<input class="nota" placeholder="ex: 2 cervejas" bind:value={quantidade} />
<label class="lab">Gatilho (opcional)</label>
<input class="nota" placeholder="o que aconteceu?" bind:value={gatilho_texto} />
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
<button class="save" onclick={salvar}>Salvar slip</button>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; box-sizing: border-box; }
  .sel { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; }
  textarea.nota { resize: vertical; min-height: 72px; }
  .checks { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
  .check-lab { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #e8e8ee; cursor: pointer; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: #5eead4; color: #0b0b10; border: none; border-radius: 12px; font-weight: 700; }
  .erro { color: #f87171; }
</style>
