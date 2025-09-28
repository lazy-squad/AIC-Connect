'use client';

import { useRouter } from 'next/navigation';
import { ArticleFormData } from '@/types/article';
import ArticleForm from '@/components/articles/ArticleForm';
import { articleAPI } from '@/lib/api';

export default function NewArticlePage() {
  const router = useRouter();

  const handleSubmit = async (data: ArticleFormData) => {
    try {
      const article = await articleAPI.createArticle(data);

      // Redirect based on publication status
      if (data.published) {
        router.push(`/articles/${article.slug}`);
      } else {
        router.push('/drafts');
      }
    } catch (error) {
      console.error('Failed to create article:', error);
      throw error; // Re-throw to let the form handle the error
    }
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Create New Article
          </h1>
          <p className="text-gray-600 mt-2">
            Share your knowledge with the AI community
          </p>
        </div>
      </div>

      <ArticleForm onSubmit={handleSubmit} onCancel={handleCancel} />
    </div>
  );
}