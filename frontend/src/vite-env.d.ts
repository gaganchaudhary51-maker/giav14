/// <reference types="vite/client" />

export {};

type GiaDesktopProviderStatus = {
  configured: boolean;
  setupComplete: boolean;
  baseUrl: string;
  model: string;
  hasApiKey: boolean;
};

declare global {
  interface Window {
    giaDesktop?: {
      getProviderSettings: () => Promise<GiaDesktopProviderStatus>;
      saveProviderSettings: (settings: { baseUrl: string; model: string; apiKey: string }) => Promise<GiaDesktopProviderStatus>;
      skipProviderSetup: () => Promise<GiaDesktopProviderStatus>;
    };
  }
}
