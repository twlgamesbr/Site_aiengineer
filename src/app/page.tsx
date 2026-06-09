import Link from "next/link";
import { getPosts } from "@/lib/posts";

export default function Home() {
  const posts = getPosts().slice(0, 5);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <header className="mb-16">
        <div className="flex items-center gap-2 mb-4">
          <span className="h-2 w-2 rounded-full bg-[var(--accent)]" />
          <span className="text-sm font-medium text-[var(--accent-light)]">
            AI Engineer
          </span>
        </div>
        <h1 className="text-4xl font-bold tracking-tight mb-3">
          Training Log
        </h1>
        <p className="text-lg text-[var(--muted)] max-w-xl">
          Daily notes on dataset generation, LLM fine-tuning runs, and
          model comparisons. Raw, technical, no fluff.
        </p>
      </header>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-widest text-[var(--muted)] mb-6">
          Latest Posts
        </h2>
        <div className="space-y-1">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group flex items-baseline justify-between gap-4 border-b border-[var(--border)] py-3 transition-colors hover:border-[var(--accent)]"
            >
              <span className="font-medium group-hover:text-[var(--accent-light)] transition-colors">
                {post.title}
              </span>
              <span className="shrink-0 text-sm text-[var(--muted)]">
                {post.date}
              </span>
            </Link>
          ))}
        </div>
        <div className="mt-8">
          <Link
            href="/blog"
            className="text-sm font-medium text-[var(--accent-light)] hover:underline"
          >
            View all posts &rarr;
          </Link>
        </div>
      </section>

      <footer className="mt-24 border-t border-[var(--border)] pt-8 text-sm text-[var(--muted)]">
        <p>AI Engineer &mdash; daily training log</p>
      </footer>
    </div>
  );
}
