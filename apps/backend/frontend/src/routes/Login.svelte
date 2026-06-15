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
  <h1>Rumo ao Zero</h1>
  <input placeholder="usuário" bind:value={username} autocomplete="username" />
  <input type="password" placeholder="senha" bind:value={password} autocomplete="current-password" />
  {#if erro}<p class="erro">{erro}</p>{/if}
  <button type="submit">Entrar</button>
</form>

<style>
  .login { display: flex; flex-direction: column; gap: 12px; max-width: 320px; margin: 18vh auto; padding: 0 20px; }
  input, button { padding: 12px; border-radius: 10px; border: 1px solid #2a2a32; font-size: 16px; }
  button { background: #5eead4; color: #0b0b10; font-weight: 700; border: none; }
  .erro { color: #f87171; font-size: 14px; }
</style>
