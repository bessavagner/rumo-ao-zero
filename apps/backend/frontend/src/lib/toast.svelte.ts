// Toast simples e reutilizável (Svelte 5 runes). Uma mensagem por vez basta
// para o fluxo de captura mobile. Some sozinho após `ms`.
export const toastState = $state<{ msg: string; tipo: "ok" | "erro" }>({
  msg: "",
  tipo: "ok",
});

let timer: ReturnType<typeof setTimeout> | undefined;

function show(msg: string, tipo: "ok" | "erro", ms: number): void {
  toastState.msg = msg;
  toastState.tipo = tipo;
  if (timer) clearTimeout(timer);
  timer = setTimeout(() => {
    toastState.msg = "";
  }, ms);
}

export const toast = {
  ok: (msg: string, ms = 2200) => show(msg, "ok", ms),
  erro: (msg: string, ms = 3500) => show(msg, "erro", ms),
};
