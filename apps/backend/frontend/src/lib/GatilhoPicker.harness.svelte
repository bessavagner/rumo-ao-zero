<script lang="ts">
  // Harness só para teste: expõe os dois valores $bindable de GatilhoPicker no DOM (via JSON num
  // <pre>) para que o teste possa afirmar o estado depois de interações do usuário — sem isso
  // não há como observar de fora um valor que o componente muda internamente por bind:.
  import GatilhoPicker from "./GatilhoPicker.svelte";

  let gatilho = $state("");
  let adicionais = $state<string[]>([]);
</script>

<GatilhoPicker bind:gatilho bind:adicionais />
<pre data-testid="estado">{JSON.stringify({ gatilho, adicionais })}</pre>
