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
  /* Sem backdrop escuro fixo: --scrim já carrega a versão certa p/ cada banda. */
  .dim { position: fixed; inset: 0; background: var(--scrim); z-index: 50; }
  .confirm { position: fixed; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 51;
    width: 86vw; max-width: 360px; background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--r-xl); padding: var(--s-5); box-shadow: var(--shadow-md); }
  .c-titulo { font-size: 16px; font-weight: 700; }
  .c-sub { font-size: 13px; color: var(--text-muted); margin-top: var(--s-2); }
  .c-acoes { display: flex; gap: var(--s-3); margin-top: var(--s-5); }
  .c-acoes button {
    flex: 1; border: none; border-radius: var(--r-md); padding: var(--s-3);
    font-size: 15px; font-weight: 700; cursor: pointer;
    transition: transform var(--dur-fast) var(--ease-out);
  }
  .c-acoes button:active { transform: scale(0.97); }
  .c-cancel { background: var(--surface-3); color: var(--text); }
  .c-ok { background: var(--accent); color: var(--accent-ink); }
  .c-ok.perigo { background: var(--danger); color: var(--danger-ink); }
</style>
