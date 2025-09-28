'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Compass,
  TrendingUp,
  Users,
  FileText,
  Eye,
  Clock,
  Sparkles
} from 'lucide-react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { DiscoveryResponse } from '@/types/feed'

export default function DiscoverPage() {
  const [activeTab, setActiveTab] = useState('rising_articles')
  const [discoveryData, setDiscoveryData] = useState<DiscoveryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDiscoveryData = async (category: string) => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        category,
        limit: '20',
        exclude_seen: 'false',
      })

      const response = await fetch(`/api/feed/discover?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch discovery data')
      }

      const data = await response.json()
      setDiscoveryData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDiscoveryData(activeTab)
  }, [activeTab])

  const renderDiscoveryItem = (item: any, index: number) => {
    if (item.article) {
      return (
        <Card key={item.article.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <Avatar className="h-12 w-12">
                  <AvatarFallback>
                    {item.article.author?.displayName?.[0] || 'U'}
                  </AvatarFallback>
                </Avatar>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className="text-xs">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    Rising
                  </Badge>
                  {item.metrics?.viewVelocity && (
                    <span className="text-xs text-muted-foreground">
                      {item.metrics.viewVelocity} views/hour
                    </span>
                  )}
                </div>
                <Link href={`/articles/${item.article.slug}`}>
                  <h3 className="font-semibold text-lg mb-2 hover:text-primary transition-colors line-clamp-2">
                    {item.article.title}
                  </h3>
                </Link>
                {item.article.summary && (
                  <p className="text-muted-foreground mb-3 line-clamp-2">
                    {item.article.summary}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {item.article.tags?.slice(0, 3).map((tag: string) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {item.metrics?.viewCount || 0}
                    </div>
                    <span>by {item.article.author?.displayName}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (item.space) {
      return (
        <Card key={item.space.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className="text-xs">
                    <Sparkles className="w-3 h-3 mr-1" />
                    Active
                  </Badge>
                </div>
                <Link href={`/spaces/${item.space.slug}`}>
                  <h3 className="font-semibold text-lg mb-2 hover:text-primary transition-colors">
                    {item.space.name}
                  </h3>
                </Link>
                {item.space.description && (
                  <p className="text-muted-foreground mb-3 line-clamp-2">
                    {item.space.description}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {item.space.tags?.slice(0, 3).map((tag: string) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {item.space.memberCount}
                    </div>
                    <div className="flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      {item.space.articleCount}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )
    }

    if (item.user) {
      return (
        <Card key={item.user.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="text-lg">
                  {item.user.displayName?.[0] || 'U'}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary" className="text-xs">
                    <Users className="w-3 h-3 mr-1" />
                    New Member
                  </Badge>
                  {item.user.joinedAt && (
                    <span className="text-xs text-muted-foreground">
                      Joined {formatDistanceToNow(new Date(item.user.joinedAt), { addSuffix: true })}
                    </span>
                  )}
                </div>
                <h3 className="font-semibold text-lg">
                  {item.user.displayName}
                </h3>
                <p className="text-muted-foreground text-sm">
                  {item.user.email}
                </p>
              </div>
              <Button variant="outline" size="sm">
                Follow
              </Button>
            </div>
          </CardContent>
        </Card>
      )
    }

    return null
  }

  const tabs = [
    {
      value: 'rising_articles',
      label: 'Rising Articles',
      icon: TrendingUp,
      description: 'Articles gaining traction fast'
    },
    {
      value: 'active_spaces',
      label: 'Active Spaces',
      icon: Users,
      description: 'Communities with recent activity'
    },
    {
      value: 'new_users',
      label: 'New Members',
      icon: Users,
      description: 'Recently joined community members'
    },
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center gap-3 mb-8">
        <Compass className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Discover</h1>
          <p className="text-muted-foreground">
            Find new content and connect with the community
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} className="flex items-center gap-2">
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <div className="mt-6">
          {tabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value}>
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">{tab.label}</h2>
                <p className="text-muted-foreground">{tab.description}</p>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Card key={i} className="animate-pulse">
                      <CardContent className="p-6">
                        <div className="flex gap-4">
                          <div className="w-12 h-12 bg-muted rounded-full" />
                          <div className="flex-1 space-y-3">
                            <div className="h-4 bg-muted rounded w-1/4" />
                            <div className="h-6 bg-muted rounded w-3/4" />
                            <div className="h-16 bg-muted rounded" />
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
                    <Button onClick={() => fetchDiscoveryData(activeTab)}>
                      Try Again
                    </Button>
                  </CardContent>
                </Card>
              ) : !discoveryData || discoveryData.items.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-muted-foreground">
                      No {tab.label.toLowerCase()} found
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {discoveryData.items.map((item, index) =>
                    renderDiscoveryItem(item, index)
                  )}
                </div>
              )}
            </TabsContent>
          ))}
        </div>
      </Tabs>

      {discoveryData && (
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Clock className="w-4 h-4 inline mr-1" />
          Refreshes {formatDistanceToNow(new Date(discoveryData.refreshAt), { addSuffix: true })}
        </div>
      )}
    </div>
  )
}