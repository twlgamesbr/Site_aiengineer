export function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 font-mono text-xs text-muted-foreground transition-colors group-hover:border-accent/40">
      {children}
    </span>
  );
}
