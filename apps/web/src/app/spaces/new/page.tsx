"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SpaceFormData } from "@/types/space";

export default function CreateSpacePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<SpaceFormData>({
    name: "",
    description: "",
    tags: [],
    visibility: "public",
  });

  const availableTags = ["RAG", "LLMs", "Vector DBs", "Embeddings", "Fine-tuning"];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/spaces", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create space");
      }

      const space = await response.json();
      router.push(`/spaces/${space.slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create space");
      setLoading(false);
    }
  };

  const toggleTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.includes(tag)
        ? formData.tags.filter((t) => t !== tag)
        : [...formData.tags, tag].slice(0, 5), // Max 5 tags
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8">Create New Space</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Space Name *
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              maxLength={100}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-800 rounded focus:border-slate-700 focus:outline-none"
              placeholder="e.g., RAG Enthusiasts"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-2">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              maxLength={500}
              rows={4}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-800 rounded focus:border-slate-700 focus:outline-none"
              placeholder="What is this space about?"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Tags (max 5)
            </label>
            <div className="flex flex-wrap gap-2">
              {availableTags.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  disabled={formData.tags.length >= 5 && !formData.tags.includes(tag)}
                  className={`px-3 py-1 rounded transition ${
                    formData.tags.includes(tag)
                      ? "bg-blue-600 text-white"
                      : "bg-slate-900 text-slate-400 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Visibility</label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="public"
                  checked={formData.visibility === "public"}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value as any })}
                  className="mr-2"
                />
                <span>Public</span>
                <span className="text-sm text-slate-500 ml-2">Anyone can view and join</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="private"
                  checked={formData.visibility === "private"}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value as any })}
                  className="mr-2"
                />
                <span>Private</span>
                <span className="text-sm text-slate-500 ml-2">Only members can view</span>
              </label>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-900/20 border border-red-800 rounded text-red-400">
              {error}
            </div>
          )}

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading || !formData.name}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? "Creating..." : "Create Space"}
            </button>
            <button
              type="button"
              onClick={() => router.push("/spaces")}
              className="px-4 py-2 bg-slate-800 text-slate-200 rounded hover:bg-slate-700 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}