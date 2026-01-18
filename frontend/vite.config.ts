import { defineConfig } from 'vite'
import { sentryVitePlugin } from "@sentry/vite-plugin"
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    sentryVitePlugin({
      // Using default Sentry setup - need to configure env variables here. Enables source maps and babel
      reactComponentAnnotation: {
        enabled: true,
        // Can add any components to ignore here
        ignoredComponents: [],
      },
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
