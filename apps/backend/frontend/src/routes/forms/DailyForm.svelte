<script lang="ts">
  import { api } from "../../lib/api";

  let { onDone }: { onDone: () => void } = $props();
  let data = $state(new Date().toISOString().slice(0, 10));
  let humor = $state(3);
  let energia = $state(3);
  let sono_q = $state(3);
  let sono_h = $state(7);
  let craving_pico = $state(0);
  let coisa_boa = $state("");
  let coisa_dificil = $state("");
  let erro = $state("");

  async function salvar() {
    erro = "";
    const payload: Record<string, unknown> = {
      data,
      humor,
      energia,
      sono_q,
      sono_h,
      craving_pico,
      coisa_boa: coisa_boa.trim() || undefined,
      coisa_dificil: coisa_dificil.trim() || undefined,
    };
    try {
      await api.post("/api/log/daily/", payload);
      onDone();
    } catch {
      erro = "Não consegui salvar.";
    }
  }
</script>

<h2>Daily</h2>
<label class="lab">Data</label>
<input class="nota" type="date" bind:value={data} />
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
<label class="lab">Qualidade do sono</label>
<div class="scale">
  {#each [1, 2, 3, 4, 5] as n}
    <button class:on={sono_q === n} onclick={() => (sono_q = n)}>{n}</button>
  {/each}
</div>
<label class="lab">Horas de sono</label>
<input class="nota" type="number" min="0" max="24" step="0.5" bind:value={sono_h} />
<label class="lab">Craving pico: {craving_pico}</label>
<input type="range" min="0" max="10" bind:value={craving_pico} />
<label class="lab">Coisa boa (opcional)</label>
<input class="nota" placeholder="algo positivo do dia" bind:value={coisa_boa} />
<label class="lab">Coisa difícil (opcional)</label>
<input class="nota" placeholder="algo desafiador" bind:value={coisa_dificil} />
{#if erro}<p class="erro">{erro}</p>{/if}
<button class="save" onclick={salvar}>Salvar daily</button>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; opacity: .6; margin: 12px 0 6px; }
  .scale { display: flex; gap: 6px; }
  .scale button { flex: 1; padding: 10px 0; background: #26262f; border: none; color: #e8e8ee; border-radius: 10px; font-weight: 700; }
  .scale button.on { background: #5eead4; color: #0b0b10; }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: 10px; border: 1px solid #2a2a32; background: #14141a; color: #e8e8ee; box-sizing: border-box; }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: #5eead4; color: #0b0b10; border: none; border-radius: 12px; font-weight: 700; }
  .erro { color: #f87171; }
</style>
