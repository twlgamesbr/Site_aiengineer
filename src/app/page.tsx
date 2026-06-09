import Link from "next/link";
import { getPosts } from "@/lib/posts";

export default function Home() {
  const posts = getPosts();
  const latest = posts.slice(0, 5);

  return (
    <div className="bg-grid">
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 sm:py-24">
        {/* Hero */}
        <header className="mb-20">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            <span className="font-mono text-xs font-medium tracking-wide text-accent-light">
              AI ENGINEER
            </span>
          </div>
          <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl">
            Training Log
          </h1>
          <p className="mt-5 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            Daily notes on dataset generation, LLM fine-tuning runs, and model
            comparisons. Raw, technical, no fluff.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/blog"
              className="inline-flex h-10 items-center justify-center rounded-lg bg-accent px-5 text-sm font-medium text-accent-foreground transition-colors hover:bg-accent-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Read the log
            </Link>
            <a
              href="#latest"
              className="inline-flex h-10 items-center justify-center rounded-lg border border-border bg-card px-5 text-sm font-medium text-foreground transition-colors hover:border-accent/50 hover:bg-muted"
            >
              Latest posts
            </a>
          </div>
        </header>

        {/* Latest posts */}
        <section id="latest" className="scroll-mt-20">
          <div className="mb-6 flex items-baseline justify-between">
            <h2 className="font-mono text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              Latest Posts
            </h2>
            <span className="font-mono text-xs text-muted-foreground">
              {posts.length} total
            </span>
          </div>

          {latest.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-card/50 p-12 text-center">
              <p className="text-base font-medium text-foreground">
                No posts yet
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                The training log is warming up. Check back soon.
              </p>
            </div>
          ) : (
            <ul className="-mx-3">
              {latest.map((post) => (
                <li key={post.slug}>
                  <Link
                    href={`/blog/${post.slug}`}
                    className="group flex items-baseline justify-between gap-4 rounded-lg px-3 py-4 transition-colors hover:bg-card"
                  >
                    <span className="min-w-0">
                      <span className="block truncate font-medium text-foreground transition-colors group-hover:text-accent-light">
                        {post.title}
                      </span>
                      <span className="mt-1 block truncate text-sm text-muted-foreground">
                        {post.excerpt}
                      </span>
                    </span>
                    <time className="shrink-0 font-mono text-xs text-muted-foreground">
                      {post.date}
                    </time>
                  </Link>
                </li>
              ))}
            </ul>
          )}

          {latest.length > 0 && (
            <div className="mt-8">
              <Link
                href="/blog"
                className="group inline-flex items-center gap-1.5 text-sm font-medium text-accent-light"
              >
                View all posts
                <span className="transition-transform group-hover:translate-x-0.5">
                  &rarr;
                </span>
              </Link>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
