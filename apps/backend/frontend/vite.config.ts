/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { svelteTesting } from "@testing-library/svelte/vite";

// Build servido pelo Django em /static/spa/ (ver Fase C). Em dev, proxy /api -> gunicorn.
export default defineConfig({
  plugins: [svelte(), svelteTesting()],
  base: "/static/spa/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8492",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
