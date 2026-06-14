<script lang="ts">
  import { api } from "../../lib/api";

  let { onDone }: { onDone: () => void } = $props();
  let substancia = $state<"alcool" | "tabaco" | "ambos">("alcool");
  let intensidade_pico = $state(6);
  let gatilho_texto = $state("");
  let duracao_min = $state(0);
  let intensidade_final = $state(0);
  let aprendizado = $state("");
  let erro = $state("");

  async function salvar() {
    erro = "";
    if (!gatilho_texto.trim()) {
      erro = "Informe o gatilho.";
      return;
    }
    const payload: Record<string, unknown> = {
      timestamp: new Date().toISOString(),
      substancia,
      intensidade_pico,
      gatilho_texto: gatilho_texto.trim(),
      duracao_min: duracao_min || undefined,
      intensidade_final: intensidade_final || undefined,
      aprendizado: aprendizado.trim() || undefined,
    };
    try {
      await api.post("/api/log/cravings/", payload);
      onDone();
    } catch {
      erro = "Não consegui salvar.";
    }
  }
</script>

<h2>Craving</h2>
<label class="lab">Substância</label>
<select class="sel" bind:value={substancia}>
  <option value="alcool">Álcool</option>
  <option value="tabaco">Tabaco</option>
  <option value="ambos">Ambos</option>
</select>
<label class="lab">Intensidade pico: {intensidade_pico}</label>
<input type="range" min="0" max="10" bind:value={intensidade_pico} />
<label class="lab">Gatilho *</label>
<input class="nota" placeholder="descreva o gatilho" bind:value={gatilho_texto} />
<label class="lab">Duração (min)</label>
<input class="nota" type="number" min="0" bind:value={duracao_min} />
<label class="lab">Intensidade final: {intensidade_final}</label>
<input type="range" min="0" max="10" bind:value={intensidade_final} />
<label class="lab">Aprendizado (opcional)</label>
<input class="nota" placeholder="o que aprendi?" bind:value={aprendizado} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" onclick={salvar}>Salvar craving</button>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; box-sizing: border-box; }
  .sel { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: #5eead4; color: #0b0b10; border: none; border-radius: 12px; font-weight: 700; }
  .erro { color: #f87171; }
</style>
