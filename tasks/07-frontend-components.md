# Task 07: Frontend Components Implementation

## Objective
Build all essential React components for the MVP: article editor with Tiptap, article cards, tag selectors, user profiles, and collaboration spaces UI.

## Current State
- Authentication flow implemented (Task 06)
- Navigation component exists
- shadcn/ui available for base components

## Acceptance Criteria
- [ ] Tiptap editor for article creation
- [ ] Article display with rich text rendering
- [ ] Tag selection and filtering
- [ ] User profile pages
- [ ] Spaces listing and detail pages
- [ ] Feed with filtering options

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check existing components
ls -la apps/web/src/components/
find apps/web/src/components -name "*.tsx" 2>/dev/null

# Check for editor components
find apps/web/src -name "*.tsx" | xargs grep -l "editor\|Editor\|tiptap"

# Check installed UI libraries
grep -E "@tiptap|shadcn|radix-ui" apps/web/package.json

# Check existing pages that might use these components
ls -la apps/web/src/app/articles/ 2>/dev/null
ls -la apps/web/src/app/feed/ 2>/dev/null
ls -la apps/web/src/app/spaces/ 2>/dev/null

# Check for UI component library setup
ls -la apps/web/src/components/ui/
cat apps/web/components.json 2>/dev/null

# Check Tailwind configuration for prose styles
cat apps/web/tailwind.config.ts | grep prose

# Check for date formatting libraries
grep "date-fns\|dayjs\|moment" apps/web/package.json

# Check existing types/interfaces
find apps/web/src -name "*.ts" -o -name "*.tsx" | xargs grep -l "interface.*Article\|type.*Article"
```

### 1. Tiptap Editor Setup
Install dependencies:
```bash
cd apps/web
pnpm add @tiptap/react @tiptap/starter-kit @tiptap/extension-link @tiptap/extension-code-block-lowlight lowlight
```

Create `apps/web/src/components/editor/tiptap-editor.tsx`:

```tsx
'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { lowlight } from 'lowlight';
import { Button } from '@/components/ui/button';
import {
  Bold, Italic, Code, List, ListOrdered,
  Link2, Quote, Heading2, CodeSquare
} from 'lucide-react';

interface TiptapEditorProps {
  content?: any;
  onChange: (content: any) => void;
  placeholder?: string;
}

export function TiptapEditor({ content, onChange, placeholder }: TiptapEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        codeBlock: false,
      }),
      Link.configure({
        openOnClick: false,
      }),
      CodeBlockLowlight.configure({
        lowlight,
      }),
    ],
    content,
    editorProps: {
      attributes: {
        class: 'prose prose-invert max-w-none min-h-[400px] p-4 focus:outline-none',
      },
    },
    onUpdate: ({ editor }) => {
      onChange(editor.getJSON());
    },
  });

  if (!editor) {
    return null;
  }

  return (
    <div className="border border-slate-700 rounded-lg bg-slate-900">
      <div className="border-b border-slate-700 p-2 flex flex-wrap gap-1">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'bg-slate-800' : ''}
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'bg-slate-800' : ''}
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleCode().run()}
          className={editor.isActive('code') ? 'bg-slate-800' : ''}
        >
          <Code className="h-4 w-4" />
        </Button>
        <div className="w-px bg-slate-700 mx-1" />
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive('heading', { level: 2 }) ? 'bg-slate-800' : ''}
        >
          <Heading2 className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'bg-slate-800' : ''}
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'bg-slate-800' : ''}
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          className={editor.isActive('blockquote') ? 'bg-slate-800' : ''}
        >
          <Quote className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          className={editor.isActive('codeBlock') ? 'bg-slate-800' : ''}
        >
          <CodeSquare className="h-4 w-4" />
        </Button>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
```

### 2. Article Creation Page
Create `apps/web/src/app/articles/new/page.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Navigation } from '@/components/layout/navigation';
import { TiptapEditor } from '@/components/editor/tiptap-editor';
import { TagSelector } from '@/components/ui/tag-selector';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useAuth } from '@/contexts/auth-context';

export default function NewArticlePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState(null);
  const [tags, setTags] = useState<string[]>([]);
  const [published, setPublished] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    if (!title || !content) {
      alert('Title and content are required');
      return;
    }

    setSaving(true);
    try {
      const response = await fetch('/api/articles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title,
          summary,
          content,
          tags,
          published,
        }),
      });

      if (response.ok) {
        const article = await response.json();
        router.push(`/articles/${article.slug}`);
      } else {
        throw new Error('Failed to save article');
      }
    } catch (error) {
      console.error('Save failed:', error);
      alert('Failed to save article');
    } finally {
      setSaving(false);
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950">
        <Navigation />
        <main className="mx-auto max-w-4xl px-4 py-8">
          <h1 className="text-2xl font-semibold text-slate-100 mb-8">Write Article</h1>

          <div className="space-y-6">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter article title..."
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="summary">Summary (optional)</Label>
              <Textarea
                id="summary"
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Brief description of your article..."
                className="mt-1"
                rows={3}
              />
            </div>

            <div>
              <Label>Content</Label>
              <div className="mt-1">
                <TiptapEditor
                  content={content}
                  onChange={setContent}
                  placeholder="Start writing your article..."
                />
              </div>
            </div>

            <div>
              <Label>Tags</Label>
              <div className="mt-1">
                <TagSelector
                  selected={tags}
                  onChange={setTags}
                  max={5}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="published"
                checked={published}
                onCheckedChange={setPublished}
              />
              <Label htmlFor="published">
                Publish immediately (uncheck to save as draft)
              </Label>
            </div>

            <div className="flex gap-4">
              <Button
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : (published ? 'Publish' : 'Save Draft')}
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/feed')}
              >
                Cancel
              </Button>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
```

### 3. Tag Selector Component
Create `apps/web/src/components/ui/tag-selector.tsx`:

```tsx
'use client';

import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

const AI_TAGS = [
  "LLMs", "RAG", "Agents", "Fine-tuning", "Prompting",
  "Vector DBs", "Embeddings", "Training", "Inference",
  "Ethics", "Safety", "Benchmarks", "Datasets", "Tools",
  "Computer Vision", "NLP", "Speech", "Robotics", "RL"
];

interface TagSelectorProps {
  selected: string[];
  onChange: (tags: string[]) => void;
  max?: number;
}

export function TagSelector({ selected, onChange, max = 5 }: TagSelectorProps) {
  function toggleTag(tag: string) {
    if (selected.includes(tag)) {
      onChange(selected.filter(t => t !== tag));
    } else if (selected.length < max) {
      onChange([...selected, tag]);
    }
  }

  return (
    <div className="space-y-4">
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selected.map(tag => (
            <Badge key={tag} variant="secondary" className="pr-1">
              {tag}
              <button
                onClick={() => toggleTag(tag)}
                className="ml-1 hover:bg-slate-700 rounded p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {AI_TAGS.map(tag => (
          <button
            key={tag}
            onClick={() => toggleTag(tag)}
            disabled={!selected.includes(tag) && selected.length >= max}
            className={`
              px-3 py-1 rounded-full text-sm transition
              ${selected.includes(tag)
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }
              ${!selected.includes(tag) && selected.length >= max
                ? 'opacity-50 cursor-not-allowed'
                : ''
              }
            `}
          >
            {tag}
          </button>
        ))}
      </div>

      <p className="text-xs text-slate-500">
        Select up to {max} tags
      </p>
    </div>
  );
}
```

### 4. Article Card Component
Create `apps/web/src/components/articles/article-card.tsx`:

```tsx
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Eye, MessageSquare } from 'lucide-react';

interface ArticleCardProps {
  article: {
    id: string;
    title: string;
    slug: string;
    summary?: string;
    tags: string[];
    view_count: number;
    created_at: string;
    author: {
      username: string;
      name: string;
      avatar_url?: string;
    };
  };
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <article className="border border-slate-800 rounded-lg p-6 hover:bg-slate-900/50 transition">
      <div className="flex items-start gap-4">
        <Link href={`/users/${article.author.username}`}>
          <Avatar className="h-10 w-10">
            <AvatarImage src={article.author.avatar_url} />
            <AvatarFallback>{article.author.name[0]}</AvatarFallback>
          </Avatar>
        </Link>

        <div className="flex-1 space-y-3">
          <div>
            <Link href={`/articles/${article.slug}`}>
              <h3 className="text-lg font-semibold text-slate-100 hover:text-blue-400 transition">
                {article.title}
              </h3>
            </Link>

            <div className="flex items-center gap-3 mt-1 text-sm text-slate-400">
              <Link href={`/users/${article.author.username}`} className="hover:text-slate-300">
                {article.author.name}
              </Link>
              <span>•</span>
              <time>
                {formatDistanceToNow(new Date(article.created_at), { addSuffix: true })}
              </time>
            </div>
          </div>

          {article.summary && (
            <p className="text-slate-300 line-clamp-2">
              {article.summary}
            </p>
          )}

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              {article.tags.map(tag => (
                <Link key={tag} href={`/feed?tag=${tag}`}>
                  <Badge variant="secondary" className="hover:bg-slate-700">
                    {tag}
                  </Badge>
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-4 text-sm text-slate-500">
              <span className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                {article.view_count}
              </span>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}
```

### 5. Feed Page with Filtering
Update `apps/web/src/app/feed/page.tsx`:

```tsx
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Navigation } from '@/components/layout/navigation';
import { ArticleCard } from '@/components/articles/article-card';
import { TagFilter } from '@/components/ui/tag-filter';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function FeedPage() {
  const searchParams = useSearchParams();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTags, setSelectedTags] = useState<string[]>(() => {
    const tag = searchParams.get('tag');
    return tag ? [tag] : [];
  });

  useEffect(() => {
    fetchArticles();
  }, [selectedTags]);

  async function fetchArticles() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      selectedTags.forEach(tag => params.append('tags', tag));

      const response = await fetch(`/api/articles?${params}`, {
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setArticles(data);
      }
    } catch (error) {
      console.error('Failed to fetch articles:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950">
        <Navigation />

        <main className="mx-auto max-w-7xl px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <aside className="lg:col-span-1">
              <div className="sticky top-4 space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3">Filter by Tags</h3>
                  <TagFilter
                    selected={selectedTags}
                    onChange={setSelectedTags}
                  />
                </div>
              </div>
            </aside>

            <div className="lg:col-span-3">
              <Tabs defaultValue="latest" className="space-y-6">
                <TabsList>
                  <TabsTrigger value="latest">Latest</TabsTrigger>
                  <TabsTrigger value="trending">Trending</TabsTrigger>
                  <TabsTrigger value="following">Following</TabsTrigger>
                </TabsList>

                <TabsContent value="latest" className="space-y-4">
                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-300 mx-auto"></div>
                    </div>
                  ) : articles.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-slate-400">No articles found</p>
                    </div>
                  ) : (
                    articles.map(article => (
                      <ArticleCard key={article.id} article={article} />
                    ))
                  )}
                </TabsContent>

                <TabsContent value="trending">
                  <p className="text-slate-400 text-center py-12">
                    Trending articles coming soon
                  </p>
                </TabsContent>

                <TabsContent value="following">
                  <p className="text-slate-400 text-center py-12">
                    Follow users to see their articles here
                  </p>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
```

### 6. Space List Component
Create `apps/web/src/components/spaces/space-card.tsx`:

```tsx
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Users, FileText, Lock, Globe } from 'lucide-react';

interface SpaceCardProps {
  space: {
    id: string;
    name: string;
    slug: string;
    description?: string;
    tags: string[];
    visibility: 'public' | 'private';
    member_count: number;
    article_count: number;
    owner: {
      username: string;
      name: string;
    };
    is_member: boolean;
  };
}

export function SpaceCard({ space }: SpaceCardProps) {
  return (
    <div className="border border-slate-800 rounded-lg p-6 hover:bg-slate-900/50 transition">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {space.visibility === 'private' ? (
            <Lock className="h-5 w-5 text-slate-500" />
          ) : (
            <Globe className="h-5 w-5 text-slate-500" />
          )}
          <Link href={`/spaces/${space.slug}`}>
            <h3 className="text-lg font-semibold text-slate-100 hover:text-blue-400 transition">
              {space.name}
            </h3>
          </Link>
        </div>

        {space.is_member && (
          <Badge variant="secondary">Member</Badge>
        )}
      </div>

      {space.description && (
        <p className="text-slate-300 mb-3 line-clamp-2">
          {space.description}
        </p>
      )}

      <div className="flex flex-wrap gap-2 mb-3">
        {space.tags.map(tag => (
          <Badge key={tag} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>by {space.owner.name}</span>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            {space.member_count}
          </span>
          <span className="flex items-center gap-1">
            <FileText className="h-4 w-4" />
            {space.article_count}
          </span>
        </div>
      </div>
    </div>
  );
}
```

## Testing Steps

1. **Article Creation**
   - Navigate to `/articles/new`
   - Write article with rich text formatting
   - Select tags and publish

2. **Feed Filtering**
   - View feed at `/feed`
   - Filter by tags
   - Switch between tabs

3. **Space Interaction**
   - Browse spaces at `/spaces`
   - Join/leave spaces
   - View space details

## Success Metrics
- Editor loads instantly
- Rich text renders correctly
- Tag filtering works smoothly
- Components are responsive

## Dependencies
- Task 06 (Frontend Auth) complete
- Tiptap and dependencies installed
- API endpoints functional

## Common Issues

### Issue: Tiptap styles not applying
- Solution: Add prose classes to Tailwind config

### Issue: Date formatting errors
- Solution: Install date-fns: `pnpm add date-fns`

### Issue: Tags not filtering
- Solution: Ensure query params are properly encoded

## Notes for AI Agents
- Keep components simple and reusable
- Use shadcn/ui components as base
- Don't over-optimize for MVP
- Focus on core functionality