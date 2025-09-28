export interface UserSummary {
  id: string;
  username?: string;
  displayName?: string;
  avatarUrl?: string;
}

export interface Article {
  id: string;
  title: string;
  slug: string;
  content: any; // Tiptap JSON
  summary?: string;
  tags: string[];
  status: 'draft' | 'published' | 'archived';
  author: UserSummary;
  viewCount: number;
  likeCount: number;
  publishedAt?: string;
  createdAt: string;
  updatedAt?: string;
  isAuthor?: boolean;
}

export interface ArticlePreview {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  tags: string[];
  author: UserSummary;
  viewCount: number;
  likeCount: number;
  publishedAt?: string;
  createdAt: string;
}

export interface ArticleFormData {
  title: string;
  content: any;
  summary?: string;
  tags: string[];
  published: boolean;
}

export interface ArticleQueryParams {
  tags?: string[];
  author?: string;
  q?: string;
  skip?: number;
  limit?: number;
  sort?: 'latest' | 'popular' | 'trending';
}

export interface ArticleListResponse {
  articles: ArticlePreview[];
  total: number;
  skip: number;
  limit: number;
}