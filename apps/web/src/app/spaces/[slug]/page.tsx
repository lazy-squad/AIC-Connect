"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Space, SpaceArticle } from "@/types/space";
import { SpaceHeader } from "@/components/spaces/SpaceHeader";
import { SpaceMemberList } from "@/components/spaces/SpaceMemberList";

type TabType = "articles" | "members" | "about";

export default function SpaceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [space, setSpace] = useState<Space | null>(null);
  const [articles, setArticles] = useState<SpaceArticle[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>("articles");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (slug) {
      fetchSpace();
      fetchArticles();
    }
  }, [slug]);

  const fetchSpace = async () => {
    try {
      const response = await fetch(`/api/spaces/${slug}`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch space");
      }

      const data = await response.json();
      setSpace(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load space");
    } finally {
      setLoading(false);
    }
  };

  const fetchArticles = async () => {
    try {
      const response = await fetch(`/api/spaces/${slug}/articles`, {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setArticles(data.articles);
      }
    } catch (err) {
      console.error("Failed to fetch articles:", err);
    }
  };

  const handleJoin = async () => {
    if (!space) return;

    try {
      const response = await fetch(`/api/spaces/${space.id}/join`, {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        fetchSpace(); // Refresh space data
      }
    } catch (err) {
      console.error("Failed to join space:", err);
    }
  };

  const handleLeave = async () => {
    if (!space) return;

    try {
      const response = await fetch(`/api/spaces/${space.id}/leave`, {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        fetchSpace(); // Refresh space data
      }
    } catch (err) {
      console.error("Failed to leave space:", err);
    }
  };

  const handleEdit = () => {
    router.push(`/spaces/${slug}/edit`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center">
        <div>Loading space...</div>
      </div>
    );
  }

  if (error || !space) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center">
        <div className="text-red-400">Error: {error || "Space not found"}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <SpaceHeader
          space={space}
          isMember={space.isMember || false}
          memberRole={space.memberRole}
          onJoin={handleJoin}
          onLeave={handleLeave}
          onEdit={handleEdit}
        />

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-slate-800">
          <button
            onClick={() => setActiveTab("articles")}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "articles"
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Articles ({space.articleCount})
          </button>
          <button
            onClick={() => setActiveTab("members")}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "members"
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Members ({space.memberCount})
          </button>
          <button
            onClick={() => setActiveTab("about")}
            className={`px-4 py-2 font-medium transition ${
              activeTab === "about"
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            About
          </button>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === "articles" && (
            <div>
              {space.isMember && (
                <button className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                  Share Article
                </button>
              )}
              {articles.length === 0 ? (
                <div className="text-slate-400">No articles shared yet</div>
              ) : (
                <div className="space-y-4">
                  {articles.map((item) => (
                    <div
                      key={item.article.id}
                      className="p-4 bg-slate-900/50 border border-slate-800 rounded-lg"
                    >
                      {item.pinned && (
                        <span className="text-xs bg-yellow-900/20 text-yellow-400 px-2 py-1 rounded mb-2 inline-block">
                          📌 Pinned
                        </span>
                      )}
                      <h3 className="text-lg font-semibold text-slate-100 mb-2">
                        {item.article.title}
                      </h3>
                      {item.article.summary && (
                        <p className="text-sm text-slate-400 mb-2">{item.article.summary}</p>
                      )}
                      <div className="text-xs text-slate-500">
                        Shared by {item.addedBy.displayName || item.addedBy.username} •{" "}
                        {new Date(item.addedAt).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "members" && (
            <SpaceMemberList
              spaceId={space.id}
              canManage={space.memberRole === "owner" || space.memberRole === "moderator"}
            />
          )}

          {activeTab === "about" && (
            <div className="prose prose-invert max-w-none">
              <h3 className="text-xl font-semibold mb-4">About this space</h3>
              <p className="text-slate-400 mb-4">
                {space.description || "No description provided."}
              </p>
              <div className="mt-6">
                <h4 className="text-lg font-semibold mb-2">Space Information</h4>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-slate-500 inline">Created:</dt>{" "}
                    <dd className="text-slate-300 inline">
                      {new Date(space.createdAt).toLocaleDateString()}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500 inline">Owner:</dt>{" "}
                    <dd className="text-slate-300 inline">
                      {space.owner.displayName || space.owner.username}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500 inline">Visibility:</dt>{" "}
                    <dd className="text-slate-300 inline capitalize">{space.visibility}</dd>
                  </div>
                </dl>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}