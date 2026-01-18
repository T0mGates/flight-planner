import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "https://a8152a02e76baaa30eb4c031715069f2@o4510726117982208.ingest.us.sentry.io/4510728140881920",
  integrations: [Sentry.browserTracingIntegration(), Sentry.browserProfilingIntegration()],

  // Set tracesSampleRate to 1.0 to capture 100%
  // of transactions for performance monitoring.
  // We recommend adjusting this value in production
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", "http://127.0.0.1/"],
  sendDefaultPii: true,
  profileLifecycle: "trace",
  profileSessionSampleRate: 1.0,
});

const queryClient = new QueryClient();

const container = document.getElementById('root');
const root = createRoot(container!, {
  // Default sentry error handling

  // Callback called when an error is thrown and not caught by an ErrorBoundary.
  onUncaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn('Uncaught error', error, errorInfo.componentStack);
  }),
  // Callback called when React catches an error in an ErrorBoundary.
  onCaughtError: Sentry.reactErrorHandler(),
  // Callback called when React automatically recovers from errors.
  onRecoverableError: Sentry.reactErrorHandler(),
})

root.render(
  <QueryClientProvider client={queryClient}>
    <StrictMode>
      <App />
    </StrictMode>
  </QueryClientProvider>
);

