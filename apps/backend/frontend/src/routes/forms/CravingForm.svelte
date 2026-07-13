<script lang="ts">
  import { api } from "../../lib/api";
  import { formatApiError } from "../../lib/errors";
  import { toast } from "../../lib/toast.svelte";
  import ConfirmDialog from "../../lib/ConfirmDialog.svelte";
  import GatilhoPicker from "../../lib/GatilhoPicker.svelte";
  import { carregarEstados, carregarSubstituicoes } from "../../lib/taxonomia.svelte";
  import type { Item } from "../../lib/taxonomia.svelte";
  import type { CravingInput, CravingEvent, Substancia3 } from "../../lib/types";

  let { onDone, registro }: { onDone: () => void; registro?: CravingEvent } = $props();

  const editando = !!registro;
  let confirmar = $state(false);

  // A taxonomia é fixa e vem do backend (`apps/baseline/taxonomia.py`). Não há autocomplete de
  // texto livre: escolher da lista é um toque, e é o que impede o mapa de virar lixo.
  let estadosTax = $state<Item[]>([]);
  let substituicoesTax = $state<Item[]>([]);
  $effect(() => {
    carregarEstados().then((e) => (estadosTax = e)).catch(() => {});
    carregarSubstituicoes().then((s) => (substituicoesTax = s)).catch(() => {});
  });

  let substancia = $state<Substancia3>(registro?.substancia ?? "alcool");
  let intensidade_pico = $state(registro?.intensidade_pico ?? 6);
  let gatilho = $state(registro?.gatilho ?? "");
  let adicionais = $state<string[]>([...(registro?.gatilhos_adicionais ?? [])]);
  let estados = $state<string[]>([...(registro?.estados ?? [])]);
  let detalhes = $state(registro?.detalhes ?? "");
  // number-input vazio vira "" em Svelte; tratamos no salvar.
  let duracao_min = $state<number | string>(registro?.duracao_min ?? 0);
  let intensidade_final = $state(registro?.intensidade_final ?? 0);
  let tempo_para_baixar_3 = $state<number | string>(registro?.tempo_para_baixar_3 ?? "");
  let substituicao = $state(registro?.substituicao ?? "");
  let substituicao_detalhes = $state(registro?.substituicao_detalhes ?? "");
  let aprendizado = $state(registro?.aprendizado ?? "");
  let erro = $state("");
  let salvando = $state(false);

  // Thought record: passo OPCIONAL depois de salvar. Pedir 7 colunas no meio de um craving de
  // intensidade 9 é pedir para o registro não acontecer — grava-se o mínimo primeiro.
  let idCriado = $state<number | null>(null);
  let pensamento_automatico = $state("");
  let evidencia_favor = $state("");
  let evidencia_contra = $state("");
  let pensamento_balanceado = $state("");

  function alternar(lista: string[], codigo: string): string[] {
    return lista.includes(codigo) ? lista.filter((c) => c !== codigo) : [...lista, codigo];
  }

  // Nº opcional: "" (não informado) vira undefined; texto inválido vira NaN e é barrado no salvar.
  function numeroOpcional(v: number | string): number | undefined {
    const s = String(v).replace(",", ".").trim();
    return s === "" ? undefined : Number(s);
  }

  async function salvar() {
    if (salvando) return;
    erro = "";
    if (!gatilho) {
      erro = "Escolha o gatilho.";
      return;
    }
    const dur = Number(String(duracao_min).replace(",", ".").trim() || "0");
    if (!Number.isFinite(dur) || dur < 0) {
      erro = "duração: informe minutos ≥ 0.";
      return;
    }
    const baixar = numeroOpcional(tempo_para_baixar_3);
    if (baixar !== undefined && (!Number.isFinite(baixar) || baixar < 0)) {
      erro = "tempo para baixar: informe minutos ≥ 0.";
      return;
    }
    salvando = true;
    const payload: CravingInput = {
      timestamp: registro?.timestamp ?? new Date().toISOString(),
      substancia,
      intensidade_pico,
      gatilho,
      gatilhos_adicionais: adicionais,
      estados,
      detalhes: detalhes.trim(),
      duracao_min: dur,
      intensidade_final,
      tempo_para_baixar_3: baixar ?? null,
      substituicao,
      substituicao_detalhes: substituicao_detalhes.trim(),
      aprendizado: aprendizado.trim() || undefined,
    };
    try {
      if (editando) {
        await api.patch(`/api/log/cravings/${registro!.id}/`, payload);
        toast.ok("Craving atualizado");
        onDone();
      } else {
        const criado = await api.post<CravingEvent>("/api/log/cravings/", payload);
        toast.ok("Craving salvo");
        idCriado = criado.id; // gravado: agora (e só agora) oferecemos o aprofundamento
      }
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }

  async function salvarReflexao() {
    if (salvando || idCriado === null) return;
    salvando = true;
    erro = "";
    try {
      await api.patch(`/api/log/cravings/${idCriado}/`, {
        pensamento_automatico: pensamento_automatico.trim(),
        evidencia_favor: evidencia_favor.trim(),
        evidencia_contra: evidencia_contra.trim(),
        pensamento_balanceado: pensamento_balanceado.trim(),
      });
      toast.ok("Reflexão salva");
      onDone();
    } catch (e) {
      erro = formatApiError(e);
    } finally {
      salvando = false;
    }
  }
</script>

{#if idCriado !== null}
  <h2>Quer aprofundar?</h2>
  <p class="sub">O craving já está gravado. Isto aqui é opcional — dá pra fechar e seguir.</p>
  <label class="lab" for="tr-pensamento">Pensamento automático</label>
  <input id="tr-pensamento" class="nota" placeholder="o que a cabeça disse?" bind:value={pensamento_automatico} />
  <label class="lab" for="tr-favor">Evidência a favor</label>
  <input id="tr-favor" class="nota" placeholder="o que sustenta esse pensamento?" bind:value={evidencia_favor} />
  <label class="lab" for="tr-contra">Evidência contra</label>
  <input id="tr-contra" class="nota" placeholder="o que contradiz?" bind:value={evidencia_contra} />
  <label class="lab" for="tr-balanceado">Pensamento balanceado</label>
  <input id="tr-balanceado" class="nota" placeholder="uma versão mais justa" bind:value={pensamento_balanceado} />
  {#if erro}<p class="erro">{erro}</p>{/if}
  <button class="save" disabled={salvando} onclick={salvarReflexao}>
    {salvando ? "Salvando…" : "Salvar reflexão"}
  </button>
  <button class="depois" onclick={onDone}>Agora não</button>
{:else}
  <h2>{editando ? "Editar craving" : "Craving"}</h2>
  <label class="lab" for="cr-substancia">Substância</label>
  <select id="cr-substancia" class="sel" bind:value={substancia}>
    <option value="alcool">Álcool</option>
    <option value="tabaco">Tabaco</option>
    <option value="ambos">Ambos</option>
  </select>

  <label class="lab" for="cr-pico">Intensidade pico: {intensidade_pico}</label>
  <input id="cr-pico" type="range" min="0" max="10" bind:value={intensidade_pico} />

  <GatilhoPicker bind:gatilho bind:adicionais idSelect="cr-gatilho" />

  <span class="lab">Estado interno (opcional)</span>
  <div class="chips">
    {#each estadosTax as e}
      <label class="chip" class:on={estados.includes(e.codigo)}>
        <input
          type="checkbox"
          aria-label={`estado ${e.rotulo}`}
          checked={estados.includes(e.codigo)}
          onchange={() => (estados = alternar(estados, e.codigo))}
        />
        {e.rotulo}
      </label>
    {/each}
  </div>

  <label class="lab" for="cr-detalhes">Detalhes (opcional)</label>
  <input id="cr-detalhes" class="nota" placeholder="o que aconteceu, nas suas palavras" bind:value={detalhes} />

  <label class="lab" for="cr-fiz">O que eu fiz</label>
  <select id="cr-fiz" class="sel" bind:value={substituicao}>
    <option value="">nada / não registrei</option>
    {#each substituicoesTax as s}<option value={s.codigo}>{s.rotulo}</option>{/each}
  </select>

  <label class="lab" for="cr-fiz-detalhes">O que você fez, nas suas palavras</label>
  <input id="cr-fiz-detalhes" class="nota" placeholder="ex: corri 5k no fim da tarde"
         bind:value={substituicao_detalhes} />

  <label class="lab" for="cr-baixar">Minutos até baixar para 3</label>
  <input id="cr-baixar" class="nota" type="number" inputmode="numeric" min="0"
         placeholder="deixe vazio se não baixou" bind:value={tempo_para_baixar_3} />

  <label class="lab" for="cr-duracao">Duração (min)</label>
  <input id="cr-duracao" class="nota" type="number" inputmode="numeric" min="0" bind:value={duracao_min} />

  <label class="lab" for="cr-final">Intensidade final: {intensidade_final}</label>
  <input id="cr-final" type="range" min="0" max="10" bind:value={intensidade_final} />

  <label class="lab" for="cr-aprendizado">Aprendizado (opcional)</label>
  <input id="cr-aprendizado" class="nota" placeholder="o que aprendi?" bind:value={aprendizado} />

  {#if erro}<p class="erro">{erro}</p>{/if}
  <button class="save" disabled={salvando} onclick={() => (editando ? (confirmar = true) : salvar())}>
    {salvando ? "Salvando…" : editando ? "Salvar alterações" : "Salvar craving"}
  </button>
{/if}

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
  .sub { font-size: 13px; opacity: .7; margin: 0 0 4px; }
  input[type=range] { width: 100%; }
  .nota { width: 100%; margin-top: 4px; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; box-sizing: border-box; }
  .sel { width: 100%; padding: 10px; border-radius: var(--r-sm); border: 1px solid var(--border); background: var(--input-bg); color: var(--text); font-size: 16px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip { display: inline-flex; align-items: center; gap: 5px; background: var(--surface-3); border: 1px solid var(--border-2); color: var(--text); border-radius: 999px; padding: 6px 10px; font-size: 12px; }
  .chip.on { border-color: var(--accent); color: var(--accent); }
  .chip input { accent-color: var(--accent); }
  .save { width: 100%; margin-top: 16px; padding: 13px; background: var(--accent); color: var(--accent-ink); border: none; border-radius: var(--r-md); font-weight: 700; font-size: 16px; }
  .save:disabled { opacity: .6; }
  .depois { width: 100%; margin-top: 8px; padding: 11px; background: none; border: none; color: var(--text-muted); font-size: 14px; }
  .erro { color: var(--danger); white-space: pre-line; }
</style>
