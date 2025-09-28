'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Article, ArticleFormData } from '@/types/article';
import ArticleForm from '@/components/articles/ArticleForm';
import { articleAPI, APIError } from '@/lib/api';

interface EditArticlePageProps {
  params: { slug: string };
}

export default function EditArticlePage({ params }: EditArticlePageProps) {
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

      // Check if user is the author
      if (!articleData.isAuthor) {
        setError('You are not authorized to edit this article');
        return;
      }

      setArticle(articleData);
    } catch (err) {
      if (err instanceof APIError && err.status === 404) {
        setError('Article not found');
      } else if (err instanceof APIError && err.status === 403) {
        setError('You are not authorized to edit this article');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load article');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: ArticleFormData) => {
    if (!article) return;

    try {
      const updatedArticle = await articleAPI.updateArticle(article.id, data);

      // Redirect based on publication status
      if (data.published) {
        router.push(`/articles/${updatedArticle.slug}`);
      } else {
        router.push('/drafts');
      }
    } catch (error) {
      console.error('Failed to update article:', error);
      throw error; // Re-throw to let the form handle the error
    }
  };

  const handleCancel = () => {
    if (article) {
      router.push(`/articles/${article.slug}`);
    } else {
      router.back();
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
            {error.includes('not found') ? '404 - Article Not Found' : 'Error'}
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
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Edit Article
          </h1>
          <p className="text-gray-600 mt-2">
            Update your article details
          </p>
        </div>
      </div>

      <ArticleForm
        article={article}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
    </div>
  );
}