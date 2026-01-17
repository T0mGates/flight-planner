import { StrictMode }                       from 'react'
import { createRoot }                       from 'react-dom/client'
import './index.css'
import App                                  from './App.tsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as Sentry                          from "@sentry/react";

Sentry.init({
  dsn: "https://a8152a02e76baaa30eb4c031715069f2@o4510726117982208.ingest.us.sentry.io/4510728140881920",
  integrations: [Sentry.browserTracingIntegration()],
  // Set tracesSampleRate to 1.0 to capture 100%
  // of transactions for performance monitoring.
  // We recommend adjusting this value in production
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", "http://127.0.0.1/"],
  sendDefaultPii: true,
});

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <StrictMode>
      <App />
    </StrictMode>
  </QueryClientProvider>
)
