'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArticlePreview } from '@/types/article';
import ArticleCard from '@/components/articles/ArticleCard';
import { articleAPI } from '@/lib/api';

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<ArticlePreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDrafts();
  }, []);

  const fetchDrafts = async () => {
    setLoading(true);
    setError(null);

    try {
      const draftData = await articleAPI.getDrafts();
      setDrafts(draftData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load drafts');
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async (articleId: string) => {
    try {
      await articleAPI.publishArticle(articleId);
      // Refresh the list to remove the published article
      await fetchDrafts();
    } catch (err) {
      console.error('Failed to publish article:', err);
      alert('Failed to publish article. Please try again.');
    }
  };

  const handleDelete = async (articleId: string) => {
    if (!confirm('Are you sure you want to delete this draft?')) {
      return;
    }

    try {
      await articleAPI.deleteArticle(articleId);
      // Refresh the list to remove the deleted article
      await fetchDrafts();
    } catch (err) {
      console.error('Failed to delete article:', err);
      alert('Failed to delete article. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">My Drafts</h1>
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading drafts...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Drafts</h1>
          <Link
            href="/articles/new"
            className="
              px-4 py-2 bg-blue-600 text-white
              rounded-lg hover:bg-blue-700
              transition-colors font-medium
            "
          >
            New Article
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
            <button
              onClick={fetchDrafts}
              className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
            >
              Try again
            </button>
          </div>
        )}

        {drafts.length === 0 ? (
          <div className="text-center py-12">
            <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                className="w-full h-full"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No drafts yet
            </h3>
            <p className="text-gray-600 mb-6">
              Start writing your first article to see drafts here.
            </p>
            <Link
              href="/articles/new"
              className="
                px-6 py-3 bg-blue-600 text-white
                rounded-lg hover:bg-blue-700
                transition-colors font-medium
              "
            >
              Create Article
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {drafts.map((draft) => (
              <div key={draft.id} className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">
                      {draft.title}
                    </h2>
                    {draft.summary && (
                      <p className="text-gray-600 mb-4 line-clamp-2">
                        {draft.summary}
                      </p>
                    )}
                    {draft.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {draft.tags.map((tag) => (
                          <span
                            key={tag}
                            className="
                              px-2 py-1 text-xs font-medium
                              bg-gray-100 text-gray-700
                              rounded-full
                            "
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                    <p className="text-sm text-gray-500">
                      Last updated:{' '}
                      {new Date(draft.createdAt).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </p>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Link
                      href={`/articles/${draft.slug}/edit`}
                      className="
                        px-3 py-1 text-sm font-medium
                        bg-gray-100 text-gray-700
                        rounded hover:bg-gray-200
                        transition-colors
                      "
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => handlePublish(draft.id)}
                      className="
                        px-3 py-1 text-sm font-medium
                        bg-blue-600 text-white
                        rounded hover:bg-blue-700
                        transition-colors
                      "
                    >
                      Publish
                    </button>
                    <button
                      onClick={() => handleDelete(draft.id)}
                      className="
                        px-3 py-1 text-sm font-medium
                        bg-red-600 text-white
                        rounded hover:bg-red-700
                        transition-colors
                      "
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}