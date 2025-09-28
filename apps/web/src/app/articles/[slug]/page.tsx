'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Article } from '@/types/article';
import ArticleView from '@/components/articles/ArticleView';
import { articleAPI, APIError } from '@/lib/api';

interface ArticlePageProps {
  params: { slug: string };
}

export default function ArticlePage({ params }: ArticlePageProps) {
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticle();
  }, [params.slug]);

  const fetchArticle = async () => {
    setLoading(true);
    setError(null);

    try {
      const articleData = await articleAPI.getArticle(params.slug);
      setArticle(articleData);
    } catch (err) {
      if (err instanceof APIError && err.status === 404) {
        setError('Article not found');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load article');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    if (article) {
      router.push(`/articles/${article.slug}/edit`);
    }
  };

  const handleDelete = async () => {
    if (!article) return;

    try {
      await articleAPI.deleteArticle(article.id);
      router.push('/drafts'); // Redirect to drafts after deletion
    } catch (err) {
      console.error('Failed to delete article:', err);
      alert('Failed to delete article. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading article...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {error === 'Article not found' ? '404 - Article Not Found' : 'Error'}
          </h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!article) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ArticleView
        article={article}
        isAuthor={article.isAuthor || false}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}