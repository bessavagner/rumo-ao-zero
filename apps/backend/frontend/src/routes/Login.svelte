<script lang="ts">
  import { login } from "../lib/auth.svelte";
  let username = $state("");
  let password = $state("");
  let erro = $state("");
  async function submit(e: Event) {
    e.preventDefault();
    erro = "";
    try {
      await login(username, password);
    } catch {
      erro = "Usuário ou senha inválidos.";
    }
  }
</script>

<form onsubmit={submit} class="login">
  <header class="mark">
    <h1>Rumo ao Zero</h1>
    <p class="tag">seu caderno rumo ao zero</p>
  </header>
  <input placeholder="usuário" bind:value={username} autocomplete="username" />
  <input type="password" placeholder="senha" bind:value={password} autocomplete="current-password" />
  {#if erro}<p class="erro">{erro}</p>{/if}
  <button type="submit">Entrar</button>
</form>

<style>
  .login { display: flex; flex-direction: column; gap: var(--s-3); max-width: 320px; margin: 18vh auto; padding: 0 var(--s-5); }
  .mark { text-align: center; margin-bottom: var(--s-3); }
  /* Wordmark em Fraunces; a "linha do zero" centralizada é a assinatura. */
  .mark h1 { font-size: 34px; margin: 0; }
  .mark :global(h1::after) { margin-inline: auto; width: 32px; }
  .tag { font-family: var(--display); font-optical-sizing: auto; font-style: italic;
    font-variation-settings: "SOFT" 60; font-size: 15px; color: var(--text-muted); margin-top: 14px; }
  input, button { padding: var(--s-3) 14px; border-radius: var(--r-md); font-size: 16px; font-family: var(--sans); }
  input { background: var(--input-bg); border: 1px solid var(--border-2); color: var(--text); }
  input::placeholder { color: var(--text-muted); }
  input:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; border-color: transparent; }
  button {
    background: var(--accent); color: var(--accent-ink); font-weight: 700; border: none;
    margin-top: var(--s-1); cursor: pointer;
    transition: transform var(--dur-fast) var(--ease-out);
  }
  button:active { transform: scale(0.97); }
  .erro { color: var(--danger); font-size: 14px; text-align: center; }
</style>
