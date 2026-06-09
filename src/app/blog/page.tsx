import { getPosts } from "@/lib/posts";
import Link from "next/link";
import { Tag } from "@/components/tag";

export const metadata = {
  title: "Blog",
  description:
    "Every training run, dataset experiment, and lesson learned — written up in full.",
};

export default function BlogPage() {
  const posts = getPosts();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <header className="mb-12">
        <p className="font-mono text-xs font-semibold uppercase tracking-widest text-accent-light">
          The Log
        </p>
        <h1 className="mt-3 text-balance text-3xl font-bold tracking-tight sm:text-4xl">
          All Posts
        </h1>
        <p className="mt-3 max-w-xl text-pretty leading-relaxed text-muted-foreground">
          Every training run, dataset experiment, and lesson learned.
        </p>
      </header>

      {posts.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-card/50 p-12 text-center">
          <p className="text-base font-medium text-foreground">No posts yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Add a <code className="font-mono text-accent-light">.md</code> file
            to{" "}
            <code className="font-mono text-accent-light">content/blog/</code> to
            get started.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {posts.map((post) => (
            <li key={post.slug}>
              <Link
                href={`/blog/${post.slug}`}
                className="group block rounded-xl border border-border bg-card p-5 transition-colors hover:border-accent/50 sm:p-6"
              >
                <div className="flex items-center gap-3">
                  <time className="font-mono text-xs text-muted-foreground">
                    {post.date}
                  </time>
                  <span className="h-px flex-1 bg-border" />
                </div>
                <h2 className="mt-3 text-lg font-semibold tracking-tight text-foreground transition-colors group-hover:text-accent-light">
                  {post.title}
                </h2>
                <p className="mt-1.5 line-clamp-2 text-sm leading-relaxed text-muted-foreground">
                  {post.excerpt}
                </p>
                {post.tags.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {post.tags.map((tag) => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
