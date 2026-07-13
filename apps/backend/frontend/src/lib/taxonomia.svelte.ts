import { api } from "./api";

export interface Item {
  codigo: string;
  rotulo: string;
}
export interface GrupoGatilhos {
  categoria: string;
  rotulo: string;
  situacoes: Item[];
}
export interface Taxonomia {
  grupos: GrupoGatilhos[];
  sem_categoria: Item[];
}

// A taxonomia é fixa (mora em código no backend): buscar uma vez por sessão basta.
let pedidoGatilhos: Promise<Taxonomia> | null = null;
let pedidoEstados: Promise<Item[]> | null = null;
let pedidoSubstituicoes: Promise<Item[]> | null = null;
const rotulos = new Map<string, string>();

function memorizar(itens: Item[]) {
  for (const i of itens) rotulos.set(i.codigo, i.rotulo);
}

export function carregarGatilhos(): Promise<Taxonomia> {
  if (!pedidoGatilhos) {
    pedidoGatilhos = api.get<Taxonomia>("/api/taxonomia/gatilhos/").then((t) => {
      for (const g of t.grupos) memorizar(g.situacoes);
      memorizar(t.sem_categoria);
      return t;
    });
  }
  return pedidoGatilhos;
}

export function carregarEstados(): Promise<Item[]> {
  if (!pedidoEstados) {
    pedidoEstados = api
      .get<{ estados: Item[] }>("/api/taxonomia/estados/")
      .then((r) => {
        memorizar(r.estados);
        return r.estados;
      });
  }
  return pedidoEstados;
}

export function carregarSubstituicoes(): Promise<Item[]> {
  if (!pedidoSubstituicoes) {
    pedidoSubstituicoes = api
      .get<{ substituicoes: Item[] }>("/api/taxonomia/substituicoes/")
      .then((r) => {
        memorizar(r.substituicoes);
        return r.substituicoes;
      });
  }
  return pedidoSubstituicoes;
}

/** Rótulo humano de um código. Antes da carga, devolve o próprio código (nunca quebra a tela). */
export function rotuloDe(codigo: string): string {
  return rotulos.get(codigo) ?? codigo;
}

/** Só para os testes: limpa o cache entre casos. */
export function resetTaxonomia(): void {
  pedidoGatilhos = null;
  pedidoEstados = null;
  pedidoSubstituicoes = null;
  rotulos.clear();
}
