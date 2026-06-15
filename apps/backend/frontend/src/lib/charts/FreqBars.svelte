<script lang="ts">
  interface Item { label: string; valor: number; }
  interface Props { titulo: string; itens: Item[]; }
  let { titulo, itens }: Props = $props();

  const max = $derived(itens.length > 0 ? Math.max(...itens.map(i => i.valor)) : 1);
</script>

<section class="freq-bars">
  <h3 class="titulo">{titulo}</h3>
  {#if itens.length === 0}
    <p class="vazio">sem dados</p>
  {:else}
    {#each itens as item}
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
  .freq-bars {
    background: #1e1e27;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
  }
  .titulo {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #a5b4fc;
    margin: 0 0 10px 0;
  }
  .vazio {
    font-size: 13px;
    color: #6b6b80;
    margin: 0;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 7px;
  }
  .row:last-child { margin-bottom: 0; }
  .label {
    font-size: 12px;
    color: #e8e8ee;
    min-width: 90px;
    max-width: 90px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .bar-wrap {
    flex: 1;
    background: #2a2a38;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
  }
  .bar {
    height: 100%;
    background: #6366f1;
    border-radius: 4px;
    transition: width 0.3s ease;
    min-width: 2px;
  }
  .valor {
    font-size: 12px;
    color: #a5b4fc;
    min-width: 28px;
    text-align: right;
    flex-shrink: 0;
  }
</style>
