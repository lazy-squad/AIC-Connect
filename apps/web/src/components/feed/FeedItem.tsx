'use client'

import Link from 'next/link'
import { FeedItem as FeedItemType } from '@/types/feed'

// Simple utility function for time formatting
function formatTimeAgo(date: string): string {
  const now = new Date()
  const then = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

interface FeedItemProps {
  item: FeedItemType
  onInteraction?: (type: string, targetId: string) => void
}

export function FeedItem({ item, onInteraction }: FeedItemProps) {
  const handleClick = () => {
    if (item.article && onInteraction) {
      onInteraction('click', item.article.id)
    }
  }

  const handleView = () => {
    if (item.article && onInteraction) {
      onInteraction('view', item.article.id)
    }
  }

  if (item.type === 'article' && item.article) {
    const { article } = item

    return (
      <div className="bg-white rounded-lg border border-gray-200 mb-4 hover:shadow-md transition-shadow">
        <div className="p-4 pb-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-600">
                {article.author.displayName?.[0] || article.author.username?.[0] || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm text-gray-900">
                  {article.author.displayName || article.author.username}
                </span>
                {article.publishedAt && (
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(article.publishedAt)}
                  </span>
                )}
                {item.reason && (
                  <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                    {item.reason === 'trending_in_period' && '📈 '}
                    {item.reason.replace('_', ' ')}
                  </span>
                )}
              </div>
              <Link
                href={`/articles/${article.slug}`}
                onClick={handleClick}
                onMouseEnter={handleView}
                className="block mt-1"
              >
                <h3 className="font-semibold text-lg text-gray-900 hover:text-blue-600 transition-colors">
                  {article.title}
                </h3>
              </Link>
            </div>
          </div>
        </div>

        <div className="px-4 pb-4">
          {article.summary && (
            <p className="text-gray-600 mb-3 line-clamp-3">
              {article.summary}
            </p>
          )}

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-1">
              {article.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs border">
                  {tag}
                </span>
              ))}
              {article.tags.length > 3 && (
                <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs border">
                  +{article.tags.length - 3}
                </span>
              )}
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <span>👁️</span>
                {article.viewCount}
              </div>
              <div className="flex items-center gap-1">
                <span>👍</span>
                {article.likeCount}
              </div>
              {item.score && (
                <div className="flex items-center gap-1">
                  <span>📈</span>
                  {Math.round(item.score)}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (item.type === 'space_activity' && item.data) {
    // TODO: Implement space activity rendering
    return (
      <Card className="mb-4">
        <CardContent className="pt-6">
          <p className="text-muted-foreground">Space activity: {JSON.stringify(item.data)}</p>
        </CardContent>
      </Card>
    )
  }

  if (item.type === 'user_activity' && item.data) {
    // TODO: Implement user activity rendering
    return (
      <Card className="mb-4">
        <CardContent className="pt-6">
          <p className="text-muted-foreground">User activity: {JSON.stringify(item.data)}</p>
        </CardContent>
      </Card>
    )
  }

  return null
}