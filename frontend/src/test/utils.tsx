import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";

import { TooltipProvider } from "@/components/ui/tooltip";

/** Render with the same providers as the app, but a fresh query client with no retries. */
export function renderWithProviders(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <TooltipProvider>{ui}</TooltipProvider>
    </QueryClientProvider>,
  );
}
