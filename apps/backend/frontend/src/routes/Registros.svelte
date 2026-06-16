<script lang="ts">
  import { api } from "../lib/api";
  import { formatApiError } from "../lib/errors";
  import { toast } from "../lib/toast.svelte";
  import PulsoForm from "./forms/PulsoForm.svelte";
  import DailyForm from "./forms/DailyForm.svelte";
  import CravingForm from "./forms/CravingForm.svelte";
  import SlipForm from "./forms/SlipForm.svelte";
  import type { Pulso, DailyEntry, CravingEvent, Slip } from "../lib/types";

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
  let itens = $state<Registro[]>([]);
  let carregando = $state(false);
  let erro = $state("");

  // Form de edição aberto (registro selecionado) ou null.
  let editando = $state<Registro | null>(null);
  // Confirmação de delete pendente.
  let apagando = $state<Registro | null>(null);

  const tipoAtual = $derived(TIPOS.find((t) => t.id === tipo)!);

  async function carregar() {
    carregando = true;
    erro = "";
    try {
      const page = await api.list<Registro>(tipoAtual.path, { ordering: tipoAtual.ordering });
      itens = page.results;
    } catch (e) {
      erro = formatApiError(e);
      itens = [];
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

  function resumo(r: Registro): { titulo: string; sub: string } {
    if (tipo === "pulso") {
      const p = r as Pulso;
      return { titulo: fmtData(p.timestamp), sub: `humor ${p.humor} · energia ${p.energia} · craving ${p.craving}` };
    }
    if (tipo === "daily") {
      const d = r as DailyEntry;
      return { titulo: fmtDia(d.data), sub: `humor ${d.humor} · energia ${d.energia} · sono ${d.sono_h}h` };
    }
    if (tipo === "craving") {
      const c = r as CravingEvent;
      return { titulo: fmtData(c.timestamp), sub: `${c.substancia} · pico ${c.intensidade_pico} · ${c.gatilho_texto}` };
    }
    const s = r as Slip;
    return { titulo: fmtData(s.timestamp), sub: `${s.substancia}${s.quantidade ? ` · ${s.quantidade}` : ""}` };
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
{:else if itens.length === 0}
  <p class="msg">Nenhum registro de {tipoAtual.label.toLowerCase()} ainda.</p>
{:else}
  <ul class="lista">
    {#each itens as r (r.id)}
      {@const res = resumo(r)}
      <li class="item">
        <div class="info">
          <div class="titulo">{res.titulo}</div>
          <div class="sub">{res.sub}</div>
        </div>
        <div class="acoes">
          <button class="edit" onclick={() => (editando = r)} aria-label="Editar">✏️</button>
          <button class="del" onclick={() => (apagando = r)} aria-label="Apagar">🗑️</button>
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
  <div class="dim" onclick={() => (apagando = null)} role="presentation"></div>
  <div class="confirm" role="alertdialog" aria-modal="true">
    <p class="c-titulo">Apagar este registro?</p>
    <p class="c-sub">Esta ação não pode ser desfeita.</p>
    <div class="c-acoes">
      <button class="c-cancel" onclick={() => (apagando = null)}>Cancelar</button>
      <button class="c-del" onclick={confirmarApagar}>Apagar</button>
    </div>
  </div>
{/if}

<style>
  h1 { font-size: 22px; font-weight: 800; margin: 0 0 16px; }
  .tabs { display: flex; gap: 6px; margin-bottom: 16px; }
  .tabs button { flex: 1; background: var(--surface); border: 1.5px solid var(--border-2); color: var(--indigo-soft); border-radius: var(--r-sm); padding: 8px 0; font-size: 13px; font-weight: 600; }
  .tabs button.active { background: var(--indigo); border-color: var(--indigo); color: #fff; }
  .msg { opacity: .7; font-size: 14px; }
  .erro { color: var(--danger); font-size: 14px; }
  .retry { margin-top: 10px; background: var(--surface-3); color: var(--text); border: none; border-radius: var(--r-sm); padding: 8px 14px; font-size: 14px; }
  .lista { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
  .item { display: flex; align-items: center; justify-content: space-between; gap: 10px; background: var(--surface); border-radius: var(--r-lg); padding: 12px 14px; }
  .info { min-width: 0; }
  .titulo { font-size: 14px; font-weight: 700; }
  .sub { font-size: 12px; opacity: .65; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .acoes { display: flex; gap: 6px; flex-shrink: 0; }
  .acoes button { background: var(--surface-3); border: none; border-radius: var(--r-sm); padding: 8px 10px; font-size: 15px; }

  .dim { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 40; }
  .sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 41; background: var(--surface-2);
    border-radius: var(--r-xl) var(--r-xl) 0 0; padding: 14px 16px calc(24px + env(safe-area-inset-bottom));
    max-width: 480px; margin: 0 auto; max-height: 88vh; overflow-y: auto; }
  .grab { width: 36px; height: 4px; background: #3a3a44; border-radius: 3px; margin: 0 auto 16px; }

  .confirm { position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 41;
    width: 86vw; max-width: 360px; background: var(--surface-2); border-radius: var(--r-xl); padding: 20px; }
  .c-titulo { font-size: 16px; font-weight: 700; }
  .c-sub { font-size: 13px; opacity: .65; margin-top: 6px; }
  .c-acoes { display: flex; gap: 10px; margin-top: 18px; }
  .c-acoes button { flex: 1; border: none; border-radius: var(--r-md); padding: 12px; font-size: 15px; font-weight: 700; }
  .c-cancel { background: var(--surface-3); color: var(--text); }
  .c-del { background: var(--danger); color: #1a0606; }
</style>
