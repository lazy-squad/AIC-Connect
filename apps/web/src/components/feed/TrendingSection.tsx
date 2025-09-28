'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { TrendingUp, TrendingDown, Minus, Eye, Users, FileText } from 'lucide-react'
import Link from 'next/link'
import { TrendingItem, TrendingResponse } from '@/types/feed'

interface TrendingSectionProps {
  type: 'articles' | 'spaces' | 'tags' | 'all'
  timeRange: string
  limit?: number
  onTimeRangeChange?: (range: string) => void
}

export function TrendingSection({
  type,
  timeRange,
  limit = 10,
  onTimeRangeChange,
}: TrendingSectionProps) {
  const [trendingData, setTrendingData] = useState<TrendingResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTrendingData()
  }, [type, timeRange, limit])

  const fetchTrendingData = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        type,
        time_range: timeRange,
        limit: limit.toString(),
      })

      const response = await fetch(`/api/feed/trending?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch trending data')
      }

      const data = await response.json()
      setTrendingData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'rising':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'falling':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const renderTrendingItem = (item: TrendingItem, index: number) => {
    if (item.type === 'article') {
      return (
        <div key={item.data.id || index} className="flex items-start gap-3 p-3 hover:bg-muted/50 rounded-lg transition-colors">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
            {index + 1}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              {getTrendIcon(item.trend)}
              <span className="text-xs text-muted-foreground">
                Score: {Math.round(item.score)}
              </span>
            </div>
            <Link
              href={`/articles/${item.data.slug}`}
              className="block mt-1"
            >
              <h4 className="font-medium text-sm hover:text-primary transition-colors line-clamp-2">
                {item.data.title}
              </h4>
            </Link>
            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                {item.viewsInPeriod || item.data.viewCount}
              </div>
              <span>by {item.data.author?.displayName}</span>
            </div>
          </div>
        </div>
      )
    }

    if (item.type === 'space') {
      return (
        <div key={item.data.id || index} className="flex items-start gap-3 p-3 hover:bg-muted/50 rounded-lg transition-colors">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
            {index + 1}
          </div>
          <div className="flex-1 min-w-0">
            <Link
              href={`/spaces/${item.data.slug}`}
              className="block"
            >
              <h4 className="font-medium text-sm hover:text-primary transition-colors">
                {item.data.name}
              </h4>
            </Link>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {item.data.description}
            </p>
            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Users className="w-3 h-3" />
                {item.data.memberCount} members
              </div>
              <div className="flex items-center gap-1">
                <FileText className="w-3 h-3" />
                {item.data.articleCount} articles
              </div>
              {item.newMembers && (
                <span>+{item.newMembers} new</span>
              )}
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Trending {type}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="animate-pulse flex gap-3">
                <div className="w-8 h-8 bg-muted rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Trending {type}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={fetchTrendingData} size="sm">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const items = type === 'all'
    ? [...(trendingData?.articles || []), ...(trendingData?.spaces || [])]
        .sort((a, b) => (b.score || 0) - (a.score || 0))
        .slice(0, limit)
    : type === 'articles'
      ? trendingData?.articles || []
      : type === 'spaces'
        ? trendingData?.spaces || []
        : trendingData?.tags || []

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg capitalize">
            Trending {type}
          </CardTitle>
          {onTimeRangeChange && (
            <Select value={timeRange} onValueChange={onTimeRangeChange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">24h</SelectItem>
                <SelectItem value="7d">7d</SelectItem>
                <SelectItem value="30d">30d</SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {items.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No trending {type} found</p>
          </div>
        ) : (
          <div className="space-y-1">
            {items.map((item, index) => renderTrendingItem(item, index))}
          </div>
        )}

        {items.length > 0 && type !== 'all' && (
          <div className="mt-4 text-center">
            <Link href={`/trending?type=${type}&time_range=${timeRange}`}>
              <Button variant="outline" size="sm">
                See More
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  )
}