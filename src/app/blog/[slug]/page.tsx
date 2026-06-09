import { getPostBySlug, getPostSlugs } from "@/lib/posts";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeSlug from "rehype-slug";
import remarkGfm from "remark-gfm";

export function generateStaticParams() {
  const slugs = getPostSlugs();
  return slugs.map((s) => ({ slug: s.replace(/\.md$/, "") }));
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) notFound();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <Link
        href="/blog"
        className="text-sm text-[var(--accent-light)] hover:underline"
      >
        &larr; All posts
      </Link>

      <article className="mt-8">
        <header className="mb-10">
          <time className="text-xs text-[var(--muted)] font-mono">
            {post.date}
          </time>
          <h1 className="text-3xl font-bold mt-2 mb-4">{post.title}</h1>
          {post.tags.length > 0 && (
            <div className="flex gap-2 flex-wrap">
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
        </header>

        <div className="prose prose-invert max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight, rehypeSlug]}
          >
            {post.content}
          </ReactMarkdown>
        </div>
      </article>

      <footer className="mt-16 border-t border-[var(--border)] pt-8">
        <Link
          href="/blog"
          className="text-sm text-[var(--accent-light)] hover:underline"
        >
          &larr; All posts
        </Link>
      </footer>
    </div>
  );
}
