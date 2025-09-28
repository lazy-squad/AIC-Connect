import { Article, ArticleFormData, ArticleListResponse, ArticlePreview } from '@/types/article';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(endpoint, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      response.status,
      errorData.detail || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export const articleAPI = {
  // Create a new article
  async createArticle(data: ArticleFormData): Promise<Article> {
    return apiRequest<Article>('/api/articles', {
      method: 'POST',
      body: JSON.stringify({
        title: data.title,
        content: JSON.stringify(data.content),
        summary: data.summary,
        tags: data.tags,
      }),
    });
  },

  // Get articles with filters
  async getArticles(params: {
    tags?: string[];
    author?: string;
    q?: string;
    skip?: number;
    limit?: number;
    sort?: 'latest' | 'popular' | 'trending';
  } = {}): Promise<ArticleListResponse> {
    const searchParams = new URLSearchParams();

    if (params.tags?.length) {
      params.tags.forEach(tag => searchParams.append('tags', tag));
    }
    if (params.author) searchParams.append('author', params.author);
    if (params.q) searchParams.append('q', params.q);
    if (params.skip) searchParams.append('skip', params.skip.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.sort) searchParams.append('sort', params.sort);

    const query = searchParams.toString();
    return apiRequest<ArticleListResponse>(
      `/api/articles${query ? `?${query}` : ''}`
    );
  },

  // Get user's drafts
  async getDrafts(): Promise<ArticlePreview[]> {
    return apiRequest<ArticlePreview[]>('/api/articles/drafts');
  },

  // Get article by slug
  async getArticle(slug: string): Promise<Article> {
    return apiRequest<Article>(`/api/articles/${slug}`);
  },

  // Update article
  async updateArticle(id: string, data: Partial<ArticleFormData>): Promise<Article> {
    const updateData: any = {};

    if (data.title !== undefined) updateData.title = data.title;
    if (data.content !== undefined) updateData.content = JSON.stringify(data.content);
    if (data.summary !== undefined) updateData.summary = data.summary;
    if (data.tags !== undefined) updateData.tags = data.tags;
    if (data.published !== undefined) {
      updateData.status = data.published ? 'published' : 'draft';
    }

    return apiRequest<Article>(`/api/articles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  },

  // Delete article
  async deleteArticle(id: string): Promise<void> {
    return apiRequest<void>(`/api/articles/${id}`, {
      method: 'DELETE',
    });
  },

  // Publish article
  async publishArticle(id: string): Promise<Article> {
    return apiRequest<Article>(`/api/articles/${id}/publish`, {
      method: 'POST',
    });
  },

  // Unpublish article
  async unpublishArticle(id: string): Promise<Article> {
    return apiRequest<Article>(`/api/articles/${id}/unpublish`, {
      method: 'POST',
    });
  },
};

export { APIError };