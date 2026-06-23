import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['src/**/*.spec.{ts,tsx}'],
    globals: true,
  },
})