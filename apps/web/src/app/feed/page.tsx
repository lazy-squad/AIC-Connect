'use client'

import { useState, useEffect, useCallback } from 'react'
import { FeedItem } from '@/components/feed/FeedItem'
import { FeedFilters } from '@/components/feed/FeedFilters'
import { TrendingSection } from '@/components/feed/TrendingSection'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Loader2, RefreshCw } from 'lucide-react'
import { FeedResponse, FeedFilters as FeedFiltersType } from '@/types/feed'

export default function FeedPage() {
  // State
  const [feedData, setFeedData] = useState<FeedResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [view, setView] = useState('latest')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [timeRange, setTimeRange] = useState('24h')

  // Pagination
  const [hasMore, setHasMore] = useState(true)

  // Fetch feed data
  const fetchFeed = useCallback(async (skip = 0, reset = true) => {
    try {
      if (reset) {
        setLoading(true)
        setError(null)
      } else {
        setLoadingMore(true)
      }

      const params = new URLSearchParams({
        view,
        skip: skip.toString(),
        limit: '20',
      })

      if (selectedTags.length > 0) {
        selectedTags.forEach(tag => params.append('tags', tag))
      }

      if (view === 'trending') {
        params.set('time_range', timeRange)
      }

      const response = await fetch(`/api/feed?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch feed')
      }

      const newData: FeedResponse = await response.json()

      if (reset) {
        setFeedData(newData)
      } else {
        setFeedData(prev => ({
          ...newData,
          items: [...(prev?.items || []), ...newData.items]
        }))
      }

      setHasMore(newData.items.length === 20)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [view, selectedTags, timeRange])

  // Load more items
  const loadMore = () => {
    if (feedData && hasMore && !loadingMore) {
      fetchFeed(feedData.items.length, false)
    }
  }

  // Track interactions
  const trackInteraction = async (type: string, targetId: string) => {
    try {
      await fetch('/api/feed/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          target_type: 'article',
          target_id: targetId,
        }),
      })
    } catch (err) {
      console.error('Failed to track interaction:', err)
    }
  }

  // Refresh feed
  const refreshFeed = () => {
    fetchFeed(0, true)
  }

  // Clear all filters
  const clearFilters = () => {
    setView('latest')
    setSelectedTags([])
    setTimeRange('24h')
  }

  // Effects
  useEffect(() => {
    fetchFeed(0, true)
  }, [fetchFeed])

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Feed */}
        <div className="flex-1 lg:max-w-2xl">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold">Feed</h1>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshFeed}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Filters */}
          <FeedFilters
            selectedTags={selectedTags}
            onTagsChange={setSelectedTags}
            timeRange={timeRange}
            onTimeRangeChange={setTimeRange}
            view={view}
            onViewChange={setView}
            onClearFilters={clearFilters}
          />

          {/* Feed Items */}
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="flex gap-3">
                      <div className="w-10 h-10 bg-muted rounded-full" />
                      <div className="flex-1 space-y-3">
                        <div className="h-4 bg-muted rounded w-1/4" />
                        <div className="h-6 bg-muted rounded w-3/4" />
                        <div className="h-20 bg-muted rounded" />
                        <div className="flex gap-2">
                          <div className="h-6 bg-muted rounded w-16" />
                          <div className="h-6 bg-muted rounded w-16" />
                          <div className="h-6 bg-muted rounded w-16" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : error ? (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={refreshFeed}>Try Again</Button>
              </CardContent>
            </Card>
          ) : !feedData || feedData.items.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground mb-4">
                  No items found with current filters
                </p>
                <Button onClick={clearFilters} variant="outline">
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="space-y-4">
                {feedData.items.map((item, index) => (
                  <FeedItem
                    key={`${item.type}-${item.article?.id || index}`}
                    item={item}
                    onInteraction={trackInteraction}
                  />
                ))}
              </div>

              {/* Load More */}
              {hasMore && (
                <div className="mt-8 text-center">
                  <Button
                    onClick={loadMore}
                    disabled={loadingMore}
                    variant="outline"
                    size="lg"
                  >
                    {loadingMore ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      'Load More'
                    )}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Sidebar */}
        <div className="lg:w-80 space-y-6">
          {/* Trending Articles */}
          <TrendingSection
            type="articles"
            timeRange={timeRange}
            limit={5}
            onTimeRangeChange={setTimeRange}
          />

          {/* Trending Spaces */}
          <TrendingSection
            type="spaces"
            timeRange={timeRange}
            limit={5}
          />
        </div>
      </div>
    </div>
  )
}