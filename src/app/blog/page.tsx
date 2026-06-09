import { getPosts, type Post } from "@/lib/posts";
import Link from "next/link";

export default function BlogPage() {
  const posts = getPosts();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <Link
        href="/"
        className="text-sm text-[var(--accent-light)] hover:underline mb-8 inline-block"
      >
        &larr; Back home
      </Link>
      <h1 className="text-3xl font-bold mt-8 mb-2">All Posts</h1>
      <p className="text-[var(--muted)] mb-10">
        Every training run, dataset experiment, and lesson learned.
      </p>

      {posts.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] p-12 text-center text-[var(--muted)]">
          <p className="text-lg font-medium mb-1">No posts yet</p>
          <p className="text-sm">
            Add a <code>.md</code> file to <code>content/blog/</code> to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {posts.map((post) => (
            <article key={post.slug}>
              <Link href={`/blog/${post.slug}`} className="group block">
                <div className="border-l-2 border-[var(--border)] pl-4 transition-colors group-hover:border-[var(--accent)]">
                  <time className="text-xs text-[var(--muted)] font-mono">
                    {post.date}
                  </time>
                  <h2 className="text-lg font-semibold mt-1 group-hover:text-[var(--accent-light)] transition-colors">
                    {post.title}
                  </h2>
                  <p className="text-sm text-[var(--muted)] mt-1 line-clamp-2">
                    {post.excerpt}
                  </p>
                  {post.tags.length > 0 && (
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {post.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-0.5 rounded-full bg-[var(--card)] text-[var(--muted)] border border-[var(--border)]"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
