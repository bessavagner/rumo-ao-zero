<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import { toast } from "../lib/toast.svelte";
  import ConfirmDialog from "../lib/ConfirmDialog.svelte";
  import PulsoForm from "./forms/PulsoForm.svelte";
  import DailyForm from "./forms/DailyForm.svelte";
  import CravingForm from "./forms/CravingForm.svelte";
  import SlipForm from "./forms/SlipForm.svelte";
  import { carregarGatilhos, rotuloDe } from "../lib/taxonomia.svelte";
  import type { Pulso, DailyEntry, CravingEvent, Slip } from "../lib/types";

  // Os resumos mostram o RÓTULO da situação, não o código — mas o código nunca quebra a tela
  // (rotuloDe devolve o próprio código antes da carga).
  let taxCarregada = $state(0);
  $effect(() => {
    carregarGatilhos().then(() => (taxCarregada += 1)).catch(() => {});
  });

  type Tipo = "pulso" | "daily" | "craving" | "slip";
  type Registro = Pulso | DailyEntry | CravingEvent | Slip;

  // path, ordering field e rótulo por tipo.
  const TIPOS: { id: Tipo; label: string; path: string; ordering: string }[] = [
    { id: "pulso", label: "Pulso", path: "/api/log/pulsos/", ordering: "-timestamp" },
    { id: "daily", label: "Daily", path: "/api/log/daily/", ordering: "-data" },
    { id: "craving", label: "Craving", path: "/api/log/cravings/", ordering: "-timestamp" },
    { id: "slip", label: "Slip", path: "/api/log/slips/", ordering: "-timestamp" },
  ];

  let tipo = $state<Tipo>("pulso");
  // Dados carregados JUNTO com o tipo a que pertencem: durante o recarregamento
  // (assíncrono) ao trocar de aba, `tipo` já mudou mas os itens ainda são do tipo
  // anterior — renderizar pelo `dados.tipo` evita aplicar a lógica de um tipo nos
  // dados de outro (era a causa do crash em fmtDia ao trocar de aba).
  let dados = $state<{ tipo: Tipo; itens: Registro[] }>({ tipo: "pulso", itens: [] });
  let carregando = $state(false);
  let erro = $state("");

  // Form de edição aberto (registro selecionado) ou null.
  let editando = $state<Registro | null>(null);
  // Confirmação de delete pendente.
  let apagando = $state<Registro | null>(null);

  const tipoAtual = $derived(TIPOS.find((t) => t.id === tipo)!);

  async function carregar() {
    const t = tipoAtual; // captura o tipo desta carga (tipo pode mudar durante o await)
    carregando = true;
    erro = "";
    try {
      const page = await api.list<Registro>(t.path, { ordering: t.ordering });
      dados = { tipo: t.id, itens: page.results };
    } catch (e) {
      erro = formatApiError(e);
      dados = { tipo: t.id, itens: [] };
    } finally {
      carregando = false;
    }
  }

  $effect(() => {
    // Recarrega quando o tipo muda (lê `tipo` via tipoAtual).
    tipoAtual;
    carregar();
  });

  function fmtData(s: string): string {
    const d = new Date(s);
    return d.toLocaleString("pt-BR", {
      day: "2-digit", month: "2-digit", year: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  }
  function fmtDia(s: string): string {
    // `data` vem como "YYYY-MM-DD" — evita timezone shift.
    const [y, m, d] = s.split("-");
    return `${d}/${m}/${y.slice(2)}`;
  }

  function resumo(r: Registro, t: Tipo): { titulo: string; sub: string } {
    if (t === "pulso") {
      const p = r as Pulso;
      return { titulo: fmtData(p.timestamp), sub: `humor ${p.humor} · energia ${p.energia} · craving ${p.craving}` };
    }
    if (t === "daily") {
      const d = r as DailyEntry;
      return { titulo: fmtDia(d.data), sub: `humor ${d.humor} · energia ${d.energia} · sono ${d.sono_h}h` };
    }
    if (t === "craving") {
      const c = r as CravingEvent;
      void taxCarregada; // re-renderiza o resumo quando os rótulos chegam
      return {
        titulo: fmtData(c.timestamp),
        sub: `${c.substancia} · pico ${c.intensidade_pico} · ${rotuloDe(c.gatilho)}`,
      };
    }
    const s = r as Slip;
    void taxCarregada;
    return {
      titulo: fmtData(s.timestamp),
      sub: `${s.substancia} · ${rotuloDe(s.gatilho)}${s.quantidade ? ` · ${s.quantidade}` : ""}`,
    };
  }

  function aoEditarFeito() {
    editando = null;
    carregar();
  }

  async function confirmarApagar() {
    const r = apagando;
    if (!r) return;
    try {
      await api.del(`${tipoAtual.path}${r.id}/`);
      apagando = null;
      toast.ok("Registro apagado");
      carregar();
    } catch (e) {
      apagando = null;
      toast.erro(formatApiError(e));
    }
  }
</script>

<h1>Registros</h1>

<div class="tabs" role="tablist" aria-label="Tipo de registro">
  {#each TIPOS as t}
    <button
      role="tab"
      aria-selected={tipo === t.id}
      class:active={tipo === t.id}
      onclick={() => (tipo = t.id)}
    >{t.label}</button>
  {/each}
</div>

{#if carregando}
  <p class="msg">Carregando…</p>
{:else if erro}
  <p class="erro">{erro}</p>
  <button class="retry" onclick={carregar}>Tentar de novo</button>
{:else if dados.itens.length === 0}
  <p class="msg">Nenhum registro de {tipoAtual.label.toLowerCase()} ainda.</p>
{:else}
  <ul class="lista">
    {#each dados.itens as r (r.id)}
      {@const res = resumo(r, dados.tipo)}
      <li class="item">
        <div class="info">
          <div class="titulo">{res.titulo}</div>
          <div class="sub">{res.sub}</div>
        </div>
        <div class="acoes">
          <button class="edit" onclick={() => (editando = r)} aria-label="Editar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L18.5 9.5a2 2 0 0 0-2.83-2.83L5 17.17V20z" /><path d="M14 7.5 16.5 10" /></svg>
          </button>
          <button class="del" onclick={() => (apagando = r)} aria-label="Apagar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 7h14M10 7V5h4v2M8 7l1 12h6l1-12" /></svg>
          </button>
        </div>
      </li>
    {/each}
  </ul>
{/if}

<!-- Sheet de edição: reaproveita os forms em modo edição -->
{#if editando}
  <div class="dim" onclick={() => (editando = null)} role="presentation"></div>
  <div class="sheet">
    <div class="grab"></div>
    {#if tipo === "pulso"}
      <PulsoForm registro={editando as Pulso} onDone={aoEditarFeito} />
    {:else if tipo === "daily"}
      <DailyForm registro={editando as DailyEntry} onDone={aoEditarFeito} />
    {:else if tipo === "craving"}
      <CravingForm registro={editando as CravingEvent} onDone={aoEditarFeito} />
    {:else}
      <SlipForm registro={editando as Slip} onDone={aoEditarFeito} />
    {/if}
  </div>
{/if}

<!-- Confirmação de delete -->
{#if apagando}
  <ConfirmDialog
    titulo="Apagar este registro?"
    sub="Esta ação não pode ser desfeita."
    confirmLabel="Apagar"
    perigo
    onConfirm={confirmarApagar}
    onCancel={() => (apagando = null)}
  />
{/if}

<style>
  /* Abas de tipo — mesmo segmented control das abas do CaptureSheet: trilho
     tingido (surface-3) com a pílula ativa em accent. */
  .tabs { display: flex; gap: var(--s-1); margin-bottom: var(--s-4); background: var(--surface-3); padding: var(--s-1); border-radius: var(--r-pill); }
  .tabs button {
    flex: 1; background: none; border: none; color: var(--text-muted);
    border-radius: var(--r-pill); padding: var(--s-2) 0; font-size: 13px; font-weight: 600;
    cursor: pointer;
    transition: background var(--dur-fast) var(--ease-out),
                color var(--dur-fast) var(--ease-out),
                transform var(--dur-fast) var(--ease-out);
  }
  .tabs button:hover { color: var(--text); }
  .tabs button:active { transform: scale(0.97); }
  .tabs button.active { background: var(--accent); color: var(--accent-ink); box-shadow: var(--shadow-sm); }
  .msg { color: var(--text-muted); font-size: 14px; }
  .erro { color: var(--danger); font-size: 14px; }
  .retry {
    margin-top: 10px; background: var(--surface-3); color: var(--text); border: none;
    border-radius: var(--r-md); padding: var(--s-2) 14px; font-size: 14px; cursor: pointer;
    transition: background var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
  }
  .retry:hover { background: var(--surface-2); }
  .retry:active { transform: scale(0.97); }
  .lista { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: var(--s-2); }
  /* Card plano sobre --surface: em modo claro fica quase branco sobre o papel
     creme, então precisa de borda + sombra para se ler como card. */
  .item {
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-lg);
    padding: var(--s-3) 14px; box-shadow: var(--shadow-sm);
  }
  .info { min-width: 0; }
  .titulo { font-size: 14px; font-weight: 700; }
  .sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .acoes { display: flex; gap: 6px; flex-shrink: 0; }
  .acoes button {
    background: var(--surface-3); border: none; border-radius: var(--r-md); padding: var(--s-2);
    display: grid; place-items: center; color: var(--text-muted); cursor: pointer;
    transition: background var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
  }
  .acoes button:hover { background: var(--surface-2); }
  .acoes button:active { transform: scale(0.97); }
  .acoes button svg { width: 17px; height: 17px; display: block; }
  .acoes .del { color: var(--danger); }

  .dim { position: fixed; inset: 0; background: var(--scrim); z-index: 40; }
  .sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 41; background: var(--surface-2);
    border-radius: var(--r-xl) var(--r-xl) 0 0; padding: 14px var(--s-4) calc(var(--s-6) + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; max-height: 88vh; overflow-y: auto; box-shadow: var(--shadow-md); }
  .grab { width: 36px; height: 4px; background: var(--border-2); border-radius: 3px; margin: 0 auto var(--s-4); }
</style>
