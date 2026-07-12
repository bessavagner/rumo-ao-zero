import { mount } from 'svelte'
// Fontes self-hosted (Field Journal): Fraunces = títulos/números, Inter = UI.
// `full` expõe todos os eixos do Fraunces (wght + opsz + SOFT + WONK) — sem ele
// os ajustes de "SOFT"/"opsz" seriam ignorados. Italic p/ o tagline do Login.
import '@fontsource-variable/fraunces/full.css'
import '@fontsource-variable/fraunces/full-italic.css'
import '@fontsource-variable/inter/index.css'
import './tokens.css'
import App from './App.svelte'

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app
