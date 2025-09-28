'use client'

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { X, Filter, Plus } from 'lucide-react'
import { FeedFilters as FeedFiltersType } from '@/types/feed'

interface FeedFiltersProps {
  selectedTags: string[]
  onTagsChange: (tags: string[]) => void
  timeRange: string
  onTimeRangeChange: (range: string) => void
  view: string
  onViewChange: (view: string) => void
  onClearFilters: () => void
}

export function FeedFilters({
  selectedTags,
  onTagsChange,
  timeRange,
  onTimeRangeChange,
  view,
  onViewChange,
  onClearFilters,
}: FeedFiltersProps) {
  const [newTag, setNewTag] = useState('')

  const handleAddTag = () => {
    if (newTag.trim() && !selectedTags.includes(newTag.trim())) {
      onTagsChange([...selectedTags, newTag.trim()])
      setNewTag('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    onTagsChange(selectedTags.filter(tag => tag !== tagToRemove))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  const hasActiveFilters = selectedTags.length > 0 || timeRange !== '24h' || view !== 'latest'

  return (
    <Card className="mb-6">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters
          </CardTitle>
          {hasActiveFilters && (
            <Button
              variant="outline"
              size="sm"
              onClick={onClearFilters}
              className="text-xs"
            >
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* View Selection */}
        <div>
          <label className="text-sm font-medium mb-2 block">View</label>
          <div className="flex gap-2">
            {[
              { value: 'latest', label: 'Latest' },
              { value: 'trending', label: 'Trending' },
              { value: 'following', label: 'Following' },
              { value: 'recommended', label: 'Recommended' },
            ].map((option) => (
              <Button
                key={option.value}
                variant={view === option.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => onViewChange(option.value)}
                className="text-xs"
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Time Range (for trending view) */}
        {view === 'trending' && (
          <div>
            <label className="text-sm font-medium mb-2 block">Time Range</label>
            <Select value={timeRange} onValueChange={onTimeRangeChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select time range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="all">All time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Tag Filter */}
        <div>
          <label className="text-sm font-medium mb-2 block">Tags</label>

          {/* Selected Tags */}
          {selectedTags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {selectedTags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 hover:text-destructive"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}

          {/* Add Tag Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Add tag..."
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={handleKeyPress}
              className="text-sm"
            />
            <Button
              size="sm"
              onClick={handleAddTag}
              disabled={!newTag.trim() || selectedTags.includes(newTag.trim())}
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Popular Tags (TODO: Fetch from API) */}
        <div>
          <label className="text-sm font-medium mb-2 block">Popular Tags</label>
          <div className="flex flex-wrap gap-2">
            {['RAG', 'LLMs', 'Agents', 'Machine Learning', 'AI', 'Deep Learning'].map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="text-xs cursor-pointer hover:bg-secondary"
                onClick={() => {
                  if (!selectedTags.includes(tag)) {
                    onTagsChange([...selectedTags, tag])
                  }
                }}
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}