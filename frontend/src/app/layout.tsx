import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RoadLancer 🚛 | Direct Trucking Marketplace",
  description: "Eliminating 40-60% middleman margins in India's trucking industry through AI price floors, 5-minute bidding windows, and verified carriers.",
  manifest: "/manifest.json",
  keywords: ["trucking marketplace india", "roadlancer", "ai logistics", "freight bidding", "transport management system"],
};

export const viewport: Viewport = {
  themeColor: "#2563eb",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-slate-50 antialiased selection:bg-blue-600 selection:text-white dark:bg-slate-950">
        <div className="flex min-h-full flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
