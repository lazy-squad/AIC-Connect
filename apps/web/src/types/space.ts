export interface UserSummary {
  id: string;
  username?: string;
  displayName?: string;
  avatarUrl?: string;
}

export interface ArticleSummary {
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

export interface Space {
  id: string;
  name: string;
  slug: string;
  description?: string;
  tags: string[];
  visibility: 'public' | 'private';
  ownerId: string;
  memberCount: number;
  articleCount: number;
  createdAt: string;
  updatedAt?: string;
  owner: UserSummary;
  isMember?: boolean;
  memberRole?: 'owner' | 'moderator' | 'member';
}

export interface SpaceMember {
  user: UserSummary;
  role: 'owner' | 'moderator' | 'member';
  joinedAt: string;
}

export interface SpaceArticle {
  article: ArticleSummary;
  addedBy: UserSummary;
  pinned: boolean;
  addedAt: string;
}

export interface SpaceFormData {
  name: string;
  description?: string;
  tags: string[];
  visibility: 'public' | 'private';
}

export interface SpaceListResponse {
  spaces: Space[];
  total: number;
  skip: number;
  limit: number;
}

export interface MemberListResponse {
  members: SpaceMember[];
  total: number;
  skip: number;
  limit: number;
}

export interface SpaceArticleListResponse {
  articles: SpaceArticle[];
  total: number;
  skip: number;
  limit: number;
}