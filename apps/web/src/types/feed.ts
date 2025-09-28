/**
 * Type definitions for the feed system
 */

import { Article, UserSummary } from './article'
import { Space } from './space'

export interface FeedItem {
  type: 'article' | 'space_activity' | 'user_activity'
  data?: Article | SpaceActivity | UserActivity
  article?: Article
  reason?: string
  score?: number
}

export interface TrendingItem {
  type: 'article' | 'space' | 'tag'
  data: any
  score: number
  trend: 'rising' | 'steady' | 'falling'
  metrics?: {
    views?: number
    members?: number
    articles?: number
  }
  viewsInPeriod?: number
  newMembers?: number
  activityScore?: number
}

export interface Activity {
  id: string
  actor: UserSummary
  action: string
  target: {
    type: string
    id: string
    name?: string
    title?: string
    slug?: string
    summary?: string
    description?: string
  }
  timestamp: string
  metadata?: Record<string, any>
}

export interface SpaceActivity {
  space: Space
  activity: string
  count: number
  timestamp: string
}

export interface UserActivity {
  user: UserSummary
  activity: string
  timestamp: string
}

export interface UserPreferences {
  preferredTags: string[]
  feedView: 'latest' | 'trending' | 'following'
}

export interface FeedResponse {
  items: FeedItem[]
  total: number
  skip: number
  limit: number
  nextCursor?: string | null
}

export interface TrendingResponse {
  articles: TrendingItem[]
  spaces: TrendingItem[]
  tags: Array<{
    tag: string
    count: number
    change: string
    articles: number
  }>
}

export interface DiscoveryResponse {
  category: string
  items: Array<{
    article?: Article
    space?: Space
    user?: UserSummary
    metrics?: {
      viewVelocity?: number
      viewCount?: number
      shareCount?: number
      firstSeen?: string
    }
  }>
  refreshAt: string
}

export interface ActivityResponse {
  activities: Activity[]
  hasMore: boolean
  oldestTimestamp?: string | null
}

export interface FeedFilters {
  tags?: string[]
  timeRange?: string
  view?: string
}