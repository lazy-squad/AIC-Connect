"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Space, SpaceListResponse } from "@/types/space";
import { SpaceCard } from "@/components/spaces/SpaceCard";

export default function SpacesPage() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showMySpaces, setShowMySpaces] = useState(false);

  useEffect(() => {
    fetchSpaces();
  }, [selectedTags, searchQuery, showMySpaces]);

  const fetchSpaces = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append("q", searchQuery);
      if (showMySpaces) params.append("my_spaces", "true");
      selectedTags.forEach(tag => params.append("tags", tag));

      const response = await fetch(`/api/spaces?${params}`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch spaces");
      }

      const data: SpaceListResponse = await response.json();
      setSpaces(data.spaces);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load spaces");
    } finally {
      setLoading(false);
    }
  };

  const handleJoinSpace = async (spaceId: string) => {
    try {
      const response = await fetch(`/api/spaces/${spaceId}/join`, {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        // Refresh the spaces list
        fetchSpaces();
      }
    } catch (err) {
      console.error("Failed to join space:", err);
    }
  };

  const availableTags = ["RAG", "LLMs", "Vector DBs", "Embeddings", "Fine-tuning"];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Collaboration Spaces</h1>
          <Link
            href="/spaces/new"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Create Space
          </Link>
        </div>

        {/* Filters */}
        <div className="mb-6 space-y-4">
          <div className="flex items-center gap-4">
            <input
              type="text"
              placeholder="Search spaces..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 bg-slate-900 border border-slate-800 rounded focus:border-slate-700 focus:outline-none"
            />
            <button
              onClick={() => setShowMySpaces(!showMySpaces)}
              className={`px-4 py-2 rounded transition ${
                showMySpaces
                  ? "bg-blue-600 text-white"
                  : "bg-slate-900 text-slate-300 hover:bg-slate-800"
              }`}
            >
              My Spaces
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() =>
                  setSelectedTags(
                    selectedTags.includes(tag)
                      ? selectedTags.filter((t) => t !== tag)
                      : [...selectedTags, tag]
                  )
                }
                className={`px-3 py-1 rounded transition ${
                  selectedTags.includes(tag)
                    ? "bg-blue-600 text-white"
                    : "bg-slate-900 text-slate-400 hover:bg-slate-800"
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Spaces Grid */}
        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading spaces...</div>
        ) : error ? (
          <div className="text-center py-12 text-red-400">Error: {error}</div>
        ) : spaces.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            No spaces found. Create the first one!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {spaces.map((space) => (
              <SpaceCard
                key={space.id}
                space={space}
                showJoinButton={!space.isMember}
                onJoin={handleJoinSpace}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}