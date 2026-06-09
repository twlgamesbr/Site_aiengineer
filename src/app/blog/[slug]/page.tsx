import { getPostBySlug, getPostSlugs } from "@/lib/posts";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeSlug from "rehype-slug";
import remarkGfm from "remark-gfm";
import type { Metadata } from "next";
import { Tag } from "@/components/tag";

export function generateStaticParams() {
  const slugs = getPostSlugs();
  return slugs.map((s) => ({ slug: s.replace(/\.md$/, "") }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return { title: "Post not found" };
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: "article",
    },
  };
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
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <Link
        href="/blog"
        className="group inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <span className="transition-transform group-hover:-translate-x-0.5">
          &larr;
        </span>
        All posts
      </Link>

      <article className="mt-8">
        <header className="border-b border-border pb-8">
          <time className="font-mono text-xs text-muted-foreground">
            {post.date}
          </time>
          <h1 className="mt-3 text-balance text-3xl font-bold leading-tight tracking-tight sm:text-4xl">
            {post.title}
          </h1>
          {post.tags.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </div>
          )}
        </header>

        <div className="prose prose-invert mt-10 max-w-none prose-headings:tracking-tight prose-h2:mt-12 prose-h2:text-2xl prose-h3:text-xl prose-img:mx-auto">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight, rehypeSlug]}
          >
            {post.content}
          </ReactMarkdown>
        </div>
      </article>

      <footer className="mt-16 border-t border-border pt-8">
        <Link
          href="/blog"
          className="group inline-flex items-center gap-1.5 text-sm font-medium text-accent-light"
        >
          <span className="transition-transform group-hover:-translate-x-0.5">
            &larr;
          </span>
          Back to all posts
        </Link>
      </footer>
    </div>
  );
}
