import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
  display: "swap",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://aiengineer.dev"),
  title: {
    default: "AI Engineer — Training Log",
    template: "%s — AI Engineer",
  },
  description:
    "A daily training log on dataset generation, LLM fine-tuning runs, and model evaluations. Raw, technical, no fluff.",
  keywords: [
    "AI engineering",
    "LLM fine-tuning",
    "dataset generation",
    "model evaluation",
    "machine learning",
  ],
  openGraph: {
    title: "AI Engineer — Training Log",
    description:
      "Daily notes on dataset generation, LLM fine-tuning runs, and model comparisons.",
    type: "website",
  },
};

export const viewport = {
  themeColor: "#08080a",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} bg-background`}
    >
      <body className="min-h-screen antialiased font-sans">
        <div className="flex min-h-screen flex-col">
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
