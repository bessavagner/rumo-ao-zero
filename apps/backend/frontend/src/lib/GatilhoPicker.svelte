<script lang="ts">
  import { carregarGatilhos } from "./taxonomia.svelte";
  import type { Taxonomia } from "./taxonomia.svelte";

  // Seletor de gatilho reutilizável (CravingForm e SlipForm). A taxonomia é fixa e vem do
  // backend (`apps/baseline/taxonomia.py`): não há autocomplete de texto livre, escolher da
  // lista é um toque — e é o que impede o mapa de virar lixo.
  let {
    gatilho = $bindable(),
    adicionais = $bindable([]),
    idSelect = "gatilho",
    rotuloPrincipal = "Gatilho principal",
  }: {
    gatilho: string;
    adicionais?: string[];
    idSelect?: string;
    rotuloPrincipal?: string;
  } = $props();

  let tax = $state<Taxonomia | null>(null);
  $effect(() => {
    carregarGatilhos()
      .then((t) => (tax = t))
      .catch(() => {});
  });

  // O principal nunca pode ficar em `adicionais`: se o usuário marca "bebendo" como adicional e
  // depois troca o principal para "bebendo", o chip some da tela (o `{#if s.codigo !== gatilho}`
  // abaixo filtra a lista visível) mas o código continuaria no array e iria no payload — sujeira
  // silenciosa. Este efeito varre o array toda vez que `gatilho` muda.
  $effect(() => {
    if (gatilho && adicionais.includes(gatilho)) {
      adicionais = adicionais.filter((c) => c !== gatilho);
    }
  });

  function alternar(lista: string[], codigo: string): string[] {
    return lista.includes(codigo) ? lista.filter((c) => c !== codigo) : [...lista, codigo];
  }
</script>

<label class="lab" for={idSelect}>{rotuloPrincipal}</label>
<select id={idSelect} class="sel" bind:value={gatilho}>
  <option value="" disabled>escolha…</option>
  {#each tax?.grupos ?? [] as g}
    <optgroup label={g.rotulo}>
      {#each g.situacoes as s}<option value={s.codigo}>{s.rotulo}</option>{/each}
    </optgroup>
  {/each}
  {#each tax?.sem_categoria ?? [] as s}<option value={s.codigo}>{s.rotulo}</option>{/each}
</select>

<span class="lab">Também pesou (opcional)</span>
<div class="chips">
  {#each tax?.grupos ?? [] as g}
    {#each g.situacoes as s}
      {#if s.codigo !== gatilho}
        <label class="chip" class:on={adicionais.includes(s.codigo)}>
          <input
            type="checkbox"
            aria-label={s.rotulo}
            checked={adicionais.includes(s.codigo)}
            onchange={() => (adicionais = alternar(adicionais, s.codigo))}
          />
          {s.rotulo}
        </label>
      {/if}
    {/each}
  {/each}
</div>

<style>
  .lab { display: block; font-size: 11px; text-transform: uppercase; color: var(--text-muted); margin: var(--s-3) 0 var(--s-2); }
  .sel {
    width: 100%; padding: var(--s-3); border-radius: var(--r-sm); border: 1px solid var(--border);
    background: var(--input-bg); color: var(--text); font-size: 16px;
    transition: border-color var(--dur-fast) var(--ease-out);
  }
  .sel:hover, .sel:focus { border-color: var(--accent); }
  .chips { display: flex; flex-wrap: wrap; gap: var(--s-2); }
  .chip {
    display: inline-flex; align-items: center; gap: 5px; background: var(--surface-3);
    border: 1px solid var(--border-2); color: var(--text); border-radius: var(--r-pill);
    padding: var(--s-2) var(--s-3); font-size: 12px; cursor: pointer;
    transition: border-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out);
  }
  .chip.on { border-color: var(--accent); color: var(--accent); }
  .chip input { accent-color: var(--accent); }
</style>
