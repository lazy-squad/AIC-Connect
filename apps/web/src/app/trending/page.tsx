'use client'

import { useState } from 'react'
import { TrendingSection } from '@/components/feed/TrendingSection'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { TrendingUp } from 'lucide-react'

export default function TrendingPage() {
  const [timeRange, setTimeRange] = useState('24h')
  const [activeTab, setActiveTab] = useState('articles')

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Trending</h1>
            <p className="text-muted-foreground">
              Discover what's hot in the AI community
            </p>
          </div>
        </div>

        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Time range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="24h">Last 24 hours</SelectItem>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
            <SelectItem value="all">All time</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="articles">Articles</TabsTrigger>
          <TabsTrigger value="spaces">Spaces</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="articles" className="space-y-6">
            <TrendingSection
              type="articles"
              timeRange={timeRange}
              limit={20}
            />
          </TabsContent>

          <TabsContent value="spaces" className="space-y-6">
            <TrendingSection
              type="spaces"
              timeRange={timeRange}
              limit={20}
            />
          </TabsContent>

          <TabsContent value="tags" className="space-y-6">
            <TrendingSection
              type="tags"
              timeRange={timeRange}
              limit={20}
            />
          </TabsContent>

          <TabsContent value="all" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TrendingSection
                type="articles"
                timeRange={timeRange}
                limit={10}
              />
              <TrendingSection
                type="spaces"
                timeRange={timeRange}
                limit={10}
              />
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  )
}