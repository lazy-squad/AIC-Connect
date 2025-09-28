'use client';

import { useState } from 'react';
import { Article, ArticleFormData } from '@/types/article';
import TiptapEditor from '../editor/TiptapEditor';

// AI Tags from the backend
const AI_TAGS = [
  'LLMs',
  'RAG',
  'Agents',
  'Fine-tuning',
  'Prompting',
  'Vector DBs',
  'Embeddings',
  'Training',
  'Inference',
  'Ethics',
  'Safety',
  'Benchmarks',
  'Datasets',
  'Tools',
  'Computer Vision',
  'NLP',
  'Speech',
  'Robotics',
  'RL',
];

interface ArticleFormProps {
  article?: Article;
  onSubmit: (data: ArticleFormData) => Promise<void>;
  onCancel: () => void;
}

export default function ArticleForm({
  article,
  onSubmit,
  onCancel,
}: ArticleFormProps) {
  const [title, setTitle] = useState(article?.title || '');
  const [content, setContent] = useState(article?.content || null);
  const [summary, setSummary] = useState(article?.summary || '');
  const [selectedTags, setSelectedTags] = useState<string[]>(
    article?.tags || []
  );
  const [saveAsDraft, setSaveAsDraft] = useState(
    article ? article.status === 'draft' : true
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (!content || !content.content || content.content.length === 0) {
      newErrors.content = 'Content is required';
    }

    if (summary && summary.length > 500) {
      newErrors.summary = 'Summary must be 500 characters or less';
    }

    if (selectedTags.length > 5) {
      newErrors.tags = 'Maximum 5 tags allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        title,
        content,
        summary: summary || undefined,
        tags: selectedTags,
        published: !saveAsDraft,
      });
    } catch (error) {
      console.error('Error submitting article:', error);
      setErrors({ submit: 'Failed to save article. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag)
        ? prev.filter((t) => t !== tag)
        : [...prev, tag].slice(0, 5)
    );
    setErrors((prev) => ({ ...prev, tags: '' }));
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto px-4 py-8">
      <div className="space-y-6">
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setErrors((prev) => ({ ...prev, title: '' }));
            }}
            className={`
              w-full px-3 py-2 border rounded-lg
              focus:outline-none focus:ring-2 focus:ring-blue-500
              ${errors.title ? 'border-red-500' : 'border-gray-300'}
            `}
            placeholder="Enter article title..."
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="summary"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Summary (optional)
          </label>
          <textarea
            id="summary"
            value={summary}
            onChange={(e) => {
              setSummary(e.target.value);
              setErrors((prev) => ({ ...prev, summary: '' }));
            }}
            rows={3}
            className={`
              w-full px-3 py-2 border rounded-lg
              focus:outline-none focus:ring-2 focus:ring-blue-500
              ${errors.summary ? 'border-red-500' : 'border-gray-300'}
            `}
            placeholder="Brief description of your article..."
            maxLength={500}
          />
          <div className="flex justify-between mt-1">
            {errors.summary && (
              <p className="text-sm text-red-600">{errors.summary}</p>
            )}
            <p className="text-sm text-gray-500">
              {summary.length}/500 characters
            </p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Content *
          </label>
          <TiptapEditor
            content={content}
            onChange={(newContent) => {
              setContent(newContent);
              setErrors((prev) => ({ ...prev, content: '' }));
            }}
            placeholder="Start writing your article..."
            className={errors.content ? 'border-red-500' : ''}
          />
          {errors.content && (
            <p className="mt-1 text-sm text-red-600">{errors.content}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (max 5)
          </label>
          <div className="flex flex-wrap gap-2">
            {AI_TAGS.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                disabled={
                  selectedTags.length >= 5 && !selectedTags.includes(tag)
                }
                className={`
                  px-3 py-1 text-sm font-medium rounded-full
                  transition-colors
                  ${
                    selectedTags.includes(tag)
                      ? 'bg-blue-600 text-white'
                      : selectedTags.length >= 5
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {tag}
              </button>
            ))}
          </div>
          {errors.tags && (
            <p className="mt-1 text-sm text-red-600">{errors.tags}</p>
          )}
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="saveAsDraft"
            checked={saveAsDraft}
            onChange={(e) => setSaveAsDraft(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label
            htmlFor="saveAsDraft"
            className="ml-2 block text-sm text-gray-700"
          >
            Save as draft (you can publish later)
          </label>
        </div>

        {errors.submit && (
          <div className="p-3 bg-red-50 border border-red-300 rounded-lg">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className={`
              px-6 py-2 text-white font-medium rounded-lg
              transition-colors
              ${
                isSubmitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }
            `}
          >
            {isSubmitting
              ? 'Saving...'
              : saveAsDraft
              ? 'Save Draft'
              : 'Publish'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="
              px-6 py-2 text-gray-700 font-medium
              border border-gray-300 rounded-lg
              hover:bg-gray-50 transition-colors
            "
          >
            Cancel
          </button>
        </div>
      </div>
    </form>
  );
}