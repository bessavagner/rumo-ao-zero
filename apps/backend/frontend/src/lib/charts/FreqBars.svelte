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
      <div class="row">
        <span class="label">{item.label}</span>
        <div class="bar-wrap">
          <div class="bar" style="width: {(item.valor / max) * 100}%"></div>
        </div>
        <span class="valor">{item.valor}</span>
      </div>
    {/each}
  {/if}
</section>

<style>
  .freq-bars { background: var(--surface); border-radius: var(--r-lg); padding: 14px 16px; margin-bottom: 12px; }
  .titulo { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--accent); margin: 0 0 10px 0; }
  .vazio { font-size: 13px; color: var(--text-muted); margin: 0; }
  .row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
  .row:last-child { margin-bottom: 0; }
  .label { font-size: 12px; color: var(--text); min-width: 90px; max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 0; }
  .bar-wrap { flex: 1; background: var(--border-2); border-radius: 4px; height: 8px; overflow: hidden; }
  .bar { height: 100%; background: var(--accent); border-radius: 4px; transition: width 0.3s ease; min-width: 2px; }
  .valor { font-size: 12px; color: var(--accent); min-width: 28px; text-align: right; flex-shrink: 0; }
</style>
