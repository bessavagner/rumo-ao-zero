<script lang="ts">
  interface Item { label: string; valor: number; }
  interface Props { titulo: string; itens: Item[]; compacto?: boolean; }
  let { titulo, itens, compacto = false }: Props = $props();

  const visiveis = $derived(compacto ? itens.slice(0, 3) : itens);
  const max = $derived(visiveis.length > 0 ? Math.max(...visiveis.map(i => i.valor)) : 1);
</script>

<section class="freq-bars">
  <h3 class="titulo">{titulo}</h3>
  {#if visiveis.length === 0}
    <p class="vazio">sem dados</p>
  {:else}
    {#each visiveis as item}
      <!-- Rótulo em cima, barra embaixo: o gatilho tem nome longo ("fim de
           expediente") e cortá-lo em "fim de expedi…" apagava justamente a
           informação que a tela existe para dar. -->
      <div class="row">
        <div class="head">
          <span class="label">{item.label}</span>
          <span class="valor">{item.valor}</span>
        </div>
        <div class="bar-wrap">
          <div class="bar" style="width: {(item.valor / max) * 100}%"></div>
        </div>
      </div>
    {/each}
  {/if}
</section>

<style>
  .freq-bars {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: var(--s-4) var(--s-5);
    margin-bottom: var(--s-3);
    box-shadow: var(--shadow-sm);
  }
  .titulo {
    font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text-muted); margin: 0 0 var(--s-4) 0;
  }
  .vazio { font-size: 13px; color: var(--text-muted); margin: 0; }

  .row { margin-bottom: var(--s-3); }
  .row:last-child { margin-bottom: 0; }

  .head { display: flex; align-items: baseline; gap: var(--s-3); margin-bottom: var(--s-2); }
  .label { flex: 1; min-width: 0; font-size: 13px; color: var(--text); overflow-wrap: anywhere; }
  .valor {
    flex-shrink: 0;
    font-family: var(--display); font-optical-sizing: auto; font-weight: 500;
    font-variation-settings: "SOFT" 40, "opsz" 14;
    font-feature-settings: "tnum" 1;
    font-size: 14px; color: var(--accent);
  }

  .bar-wrap { background: var(--surface-3); border-radius: var(--r-pill); height: 8px; overflow: hidden; }
  .bar {
    height: 100%; background: var(--accent); border-radius: var(--r-pill); min-width: 3px;
    transition: width var(--dur-mid) var(--ease-out);
  }
</style>
