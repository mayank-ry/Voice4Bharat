import { Public_Sans } from "next/font/google";
import localFont from "next/font/local";
import { headers } from "next/headers";
import { ThemeProvider } from "@/components/app/theme-provider";
import { ThemeToggle } from "@/components/app/theme-toggle";
import { cn } from "@/lib/shadcn/utils";
import Link from 'next/link'
import { getAppConfig, getStyles } from "@/lib/utils";
import { OutboundCallPanel } from "@/components/app/outbound-call-panel";
import "@/styles/globals.css";

const publicSans = Public_Sans({
  variable: "--font-public-sans",
  subsets: ["latin"],
});

const commitMono = localFont({
  display: "swap",
  variable: "--font-commit-mono",
  src: [
    {
      path: "../fonts/CommitMono-400-Regular.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../fonts/CommitMono-700-Regular.otf",
      weight: "700",
      style: "normal",
    },
    {
      path: "../fonts/CommitMono-400-Italic.otf",
      weight: "400",
      style: "italic",
    },
    {
      path: "../fonts/CommitMono-700-Italic.otf",
      weight: "700",
      style: "italic",
    },
  ],
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default async function RootLayout({
  children,
}: RootLayoutProps) {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);
  const styles = getStyles(appConfig);

  const {
    pageTitle,
    pageDescription,
  } = appConfig;

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        publicSans.variable,
        commitMono.variable,
        "scroll-smooth font-sans antialiased"
      )}
    >
      <head>
        {styles && <style>{styles}</style>}

        <title>{pageTitle}</title>

        <meta
          name="description"
          content={pageDescription}
        />
      </head>

      <body className="h-svh overflow-x-hidden">

        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          forcedTheme="light"
          disableTransitionOnChange
        >
        <div className="flex h-svh flex-col">
          {/* HEADER */}
         {/* HEADER */}
<header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
  <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">

    {/* BRAND */}
    <div className="flex items-center gap-3">

      <Link
        href="/"
        aria-label="Go to NyaAI home"
        className="flex items-center"
      >
        <img
          src="/nyaai-logo.svg"
          alt="NyaAI"
          className="h-9 w-9 cursor-pointer"
        />
      </Link>

      <div>
        <p className="text-sm font-bold leading-tight text-slate-900">
          NyaAI
        </p>

        <p className="text-xs leading-tight text-slate-500">
          AI Legal Literacy Assistant
        </p>
      </div>

    </div>

    {/* NAVIGATION */}
    <nav className="flex items-center gap-2">

      <OutboundCallPanel />

      <Link
        href="/dashboard"
        className="flex h-9 items-center rounded-full border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
      >
        Dashboard
      </Link>

      <Link
        href="/escalations"
        className="flex h-9 items-center rounded-full border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition-colors hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
      >
        Escalations
      </Link>

    </nav>

  </div>

  {/* GOLD ACCENT */}
  <div className="h-[2px] bg-gradient-to-r from-transparent via-amber-400 to-transparent" />

</header>

          {/* PAGE CONTENT */}
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
  {children}
</div>
    </div>
          {/* THEME TOGGLE */}
          <div className="group fixed bottom-0 left-1/2 z-50 mb-2 -translate-x-1/2">
            <ThemeToggle
              className="translate-y-20 transition-transform delay-150 duration-300 group-hover:translate-y-0"
            />
          </div>

        </ThemeProvider>

      </body>
    </html>
  );
}