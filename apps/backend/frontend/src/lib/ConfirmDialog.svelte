<script lang="ts">
  // Diálogo de confirmação reusável (modal central). Usado p/ apagar registro
  // e p/ confirmar edição de registro histórico. z-index acima da sheet de edição.
  let {
    titulo,
    sub = "",
    confirmLabel = "Confirmar",
    cancelLabel = "Cancelar",
    perigo = false,
    onConfirm,
    onCancel,
  }: {
    titulo: string;
    sub?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    perigo?: boolean;
    onConfirm: () => void;
    onCancel: () => void;
  } = $props();
</script>

<div class="dim" onclick={onCancel} role="presentation"></div>
<div class="confirm" role="alertdialog" aria-modal="true">
  <p class="c-titulo">{titulo}</p>
  {#if sub}<p class="c-sub">{sub}</p>{/if}
  <div class="c-acoes">
    <button class="c-cancel" onclick={onCancel}>{cancelLabel}</button>
    <button class="c-ok" class:perigo onclick={onConfirm}>{confirmLabel}</button>
  </div>
</div>

<style>
  .dim { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 50; }
  .confirm { position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 51;
    width: 86vw; max-width: 360px; background: var(--surface-2); border-radius: var(--r-xl); padding: 20px; }
  .c-titulo { font-size: 16px; font-weight: 700; }
  .c-sub { font-size: 13px; opacity: .65; margin-top: 6px; }
  .c-acoes { display: flex; gap: 10px; margin-top: 18px; }
  .c-acoes button { flex: 1; border: none; border-radius: var(--r-md); padding: 12px; font-size: 15px; font-weight: 700; }
  .c-cancel { background: var(--surface-3); color: var(--text); }
  .c-ok { background: var(--accent); color: var(--accent-ink); }
  .c-ok.perigo { background: var(--danger); color: #1a0606; }
</style>
