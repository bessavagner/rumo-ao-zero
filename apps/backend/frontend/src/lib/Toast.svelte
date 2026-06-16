<script lang="ts">
  import { toastState } from "./toast.svelte";
</script>

{#if toastState.msg}
  <div class="toast" class:erro={toastState.tipo === "erro"} role="status" aria-live="polite">
    {toastState.msg}
  </div>
{/if}

<style>
  .toast {
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    bottom: calc(96px + env(safe-area-inset-bottom));
    z-index: 50;
    max-width: 88vw;
    padding: 12px 18px;
    border-radius: var(--r-md);
    background: var(--accent);
    color: var(--accent-ink);
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
    white-space: pre-line;
    text-align: center;
  }
  .toast.erro {
    background: var(--danger);
    color: #1a0606;
  }
</style>
