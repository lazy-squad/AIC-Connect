import Link from 'next/link';
import { ArticlePreview } from '@/types/article';

interface ArticleCardProps {
  article: ArticlePreview;
  variant?: 'default' | 'compact' | 'featured';
  showAuthor?: boolean;
  onTagClick?: (tag: string) => void;
}

export default function ArticleCard({
  article,
  variant = 'default',
  showAuthor = true,
  onTagClick,
}: ArticleCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatViewCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  if (variant === 'compact') {
    return (
      <div className="p-3 border-b border-gray-200 hover:bg-gray-50 transition-colors">
        <Link href={`/articles/${article.slug}`}>
          <h3 className="font-medium text-sm text-gray-900 hover:text-blue-600 mb-1">
            {article.title}
          </h3>
        </Link>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>{formatDate(article.createdAt)}</span>
          <span>{formatViewCount(article.viewCount)} views</span>
        </div>
      </div>
    );
  }

  return (
    <article
      className={`
        bg-white rounded-lg border border-gray-200 p-6
        hover:shadow-md transition-shadow
        ${variant === 'featured' ? 'border-2 border-blue-500' : ''}
      `}
    >
      <Link href={`/articles/${article.slug}`}>
        <h2
          className={`
            font-bold text-gray-900 hover:text-blue-600 mb-2
            ${variant === 'featured' ? 'text-2xl' : 'text-xl'}
          `}
        >
          {article.title}
        </h2>
      </Link>

      {article.summary && (
        <p className="text-gray-600 mb-4 line-clamp-2">{article.summary}</p>
      )}

      {article.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags.map((tag) => (
            <button
              key={tag}
              onClick={() => onTagClick?.(tag)}
              className="
                px-2 py-1 text-xs font-medium
                bg-gray-100 text-gray-700
                rounded-full hover:bg-gray-200
                transition-colors
              "
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          {showAuthor && article.author && (
            <div className="flex items-center gap-2">
              {article.author.avatarUrl ? (
                <img
                  src={article.author.avatarUrl}
                  alt={article.author.displayName || article.author.username}
                  className="w-6 h-6 rounded-full"
                />
              ) : (
                <div className="w-6 h-6 rounded-full bg-gray-300" />
              )}
              <span className="font-medium">
                {article.author.displayName || article.author.username}
              </span>
            </div>
          )}
          <span>{formatDate(article.publishedAt || article.createdAt)}</span>
        </div>

        <div className="flex items-center gap-3">
          <span>{formatViewCount(article.viewCount)} views</span>
          {article.likeCount > 0 && (
            <span>{article.likeCount} likes</span>
          )}
        </div>
      </div>
    </article>
  );
}