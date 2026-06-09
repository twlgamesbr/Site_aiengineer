import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Engineer — Daily Blog",
  description:
    "Daily blog about dataset generation, LLM training progress, and model comparisons.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="min-h-screen">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
