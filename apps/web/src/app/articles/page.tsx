'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArticlePreview, ArticleQueryParams } from '@/types/article';
import ArticleCard from '@/components/articles/ArticleCard';
import { articleAPI } from '@/lib/api';

// AI Tags for filtering
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

export default function ArticlesPage() {
  const [articles, setArticles] = useState<ArticlePreview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'latest' | 'popular' | 'trending'>('latest');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const limit = 20;

  useEffect(() => {
    fetchArticles();
  }, [searchQuery, selectedTags, sortBy, page]);

  const fetchArticles = async () => {
    setLoading(true);
    setError(null);

    try {
      const params: ArticleQueryParams = {
        skip: page * limit,
        limit,
        sort: sortBy,
      };

      if (searchQuery) params.q = searchQuery;
      if (selectedTags.length > 0) params.tags = selectedTags;

      const response = await articleAPI.getArticles(params);
      setArticles(response.articles);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
    setPage(0); // Reset to first page
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0); // Reset to first page
    fetchArticles();
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedTags([]);
    setSortBy('latest');
    setPage(0);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Articles</h1>
            <Link
              href="/articles/new"
              className="
                px-4 py-2 bg-blue-600 text-white
                rounded-lg hover:bg-blue-700
                transition-colors font-medium
              "
            >
              Write Article
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="space-y-4">
            <form onSubmit={handleSearch} className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search articles..."
                className="
                  flex-1 px-4 py-2 border border-gray-300
                  rounded-lg focus:outline-none focus:ring-2
                  focus:ring-blue-500
                "
              />
              <button
                type="submit"
                className="
                  px-6 py-2 bg-gray-600 text-white
                  rounded-lg hover:bg-gray-700
                  transition-colors
                "
              >
                Search
              </button>
            </form>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Sort by:</label>
                <select
                  value={sortBy}
                  onChange={(e) => {
                    setSortBy(e.target.value as 'latest' | 'popular' | 'trending');
                    setPage(0);
                  }}
                  className="
                    px-3 py-1 border border-gray-300 rounded
                    focus:outline-none focus:ring-2 focus:ring-blue-500
                  "
                >
                  <option value="latest">Latest</option>
                  <option value="popular">Popular</option>
                  <option value="trending">Trending</option>
                </select>
              </div>

              {(selectedTags.length > 0 || searchQuery) && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear filters
                </button>
              )}
            </div>

            {/* Tag Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by tags:
              </label>
              <div className="flex flex-wrap gap-2">
                {AI_TAGS.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => handleTagClick(tag)}
                    className={`
                      px-3 py-1 text-sm font-medium rounded-full
                      transition-colors
                      ${
                        selectedTags.includes(tag)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
            <button
              onClick={fetchArticles}
              className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
            >
              Try again
            </button>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading articles...</p>
            </div>
          </div>
        ) : articles.length === 0 ? (
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
              No articles found
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || selectedTags.length > 0
                ? 'Try adjusting your search or filters.'
                : 'Be the first to share your knowledge!'}
            </p>
            <Link
              href="/articles/new"
              className="
                px-6 py-3 bg-blue-600 text-white
                rounded-lg hover:bg-blue-700
                transition-colors font-medium
              "
            >
              Write First Article
            </Link>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <p className="text-gray-600">
                {total} article{total !== 1 ? 's' : ''} found
                {selectedTags.length > 0 && (
                  <span> with tags: {selectedTags.join(', ')}</span>
                )}
              </p>
            </div>

            <div className="grid gap-6">
              {articles.map((article) => (
                <ArticleCard
                  key={article.id}
                  article={article}
                  onTagClick={handleTagClick}
                />
              ))}
            </div>

            {/* Pagination */}
            {total > limit && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 0}
                  className="
                    px-4 py-2 text-sm font-medium
                    border border-gray-300 rounded-lg
                    disabled:opacity-50 disabled:cursor-not-allowed
                    hover:bg-gray-50
                  "
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {page + 1} of {Math.ceil(total / limit)}
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={(page + 1) * limit >= total}
                  className="
                    px-4 py-2 text-sm font-medium
                    border border-gray-300 rounded-lg
                    disabled:opacity-50 disabled:cursor-not-allowed
                    hover:bg-gray-50
                  "
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}