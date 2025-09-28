'use client';

import { Article } from '@/types/article';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import { useRouter } from 'next/navigation';

const lowlight = createLowlight(common);

interface ArticleViewProps {
  article: Article;
  isAuthor: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function ArticleView({
  article,
  isAuthor,
  onEdit,
  onDelete,
}: ArticleViewProps) {
  const router = useRouter();

  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: true,
        HTMLAttributes: {
          class: 'text-blue-600 hover:text-blue-800 underline',
        },
      }),
      CodeBlockLowlight.configure({
        lowlight,
      }),
    ],
    content: article.content,
    editable: false,
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this article?')) {
      return;
    }
    await onDelete?.();
  };

  return (
    <article className="max-w-4xl mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {article.title}
        </h1>

        {article.summary && (
          <p className="text-xl text-gray-600 mb-6">{article.summary}</p>
        )}

        <div className="flex items-center justify-between border-b border-gray-200 pb-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              {article.author.avatarUrl ? (
                <img
                  src={article.author.avatarUrl}
                  alt={article.author.displayName || article.author.username}
                  className="w-12 h-12 rounded-full"
                />
              ) : (
                <div className="w-12 h-12 rounded-full bg-gray-300" />
              )}
              <div>
                <p className="font-semibold text-gray-900">
                  {article.author.displayName || article.author.username}
                </p>
                <p className="text-sm text-gray-500">
                  {formatDate(article.publishedAt || article.createdAt)}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-sm text-gray-500">
              <span className="font-medium">{article.viewCount}</span> views
            </div>
            {article.likeCount > 0 && (
              <div className="text-sm text-gray-500">
                <span className="font-medium">{article.likeCount}</span> likes
              </div>
            )}
          </div>
        </div>

        {article.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {article.tags.map((tag) => (
              <span
                key={tag}
                className="
                  px-3 py-1 text-sm font-medium
                  bg-gray-100 text-gray-700
                  rounded-full
                "
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {isAuthor && (
          <div className="flex gap-4 mt-6">
            <button
              onClick={onEdit}
              className="
                px-4 py-2 text-sm font-medium
                bg-blue-600 text-white
                rounded-lg hover:bg-blue-700
                transition-colors
              "
            >
              Edit Article
            </button>
            <button
              onClick={handleDelete}
              className="
                px-4 py-2 text-sm font-medium
                bg-red-600 text-white
                rounded-lg hover:bg-red-700
                transition-colors
              "
            >
              Delete Article
            </button>
            {article.status === 'draft' && (
              <span className="
                px-3 py-2 text-sm font-medium
                bg-yellow-100 text-yellow-800
                rounded-lg
              ">
                Draft
              </span>
            )}
          </div>
        )}
      </header>

      <EditorContent
        editor={editor}
        className="prose prose-lg max-w-none"
      />
    </article>
  );
}