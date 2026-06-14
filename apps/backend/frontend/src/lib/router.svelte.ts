// Router por hash (#/hoje, #/progresso). Simples o bastante p/ 3 telas; evita dep extra.
export const route = $state({ path: window.location.hash.slice(1) || "/hoje" });
window.addEventListener("hashchange", () => {
  route.path = window.location.hash.slice(1) || "/hoje";
});
export function go(path: string): void {
  window.location.hash = path;
}
