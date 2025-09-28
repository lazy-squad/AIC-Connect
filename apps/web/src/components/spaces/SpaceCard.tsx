"use client";

import Link from "next/link";
import { Space } from "@/types/space";

interface SpaceCardProps {
  space: Space;
  showJoinButton?: boolean;
  onJoin?: (spaceId: string) => void;
}

export function SpaceCard({ space, showJoinButton = false, onJoin }: SpaceCardProps) {
  const handleJoin = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onJoin) {
      onJoin(space.id);
    }
  };

  return (
    <Link
      href={`/spaces/${space.slug}`}
      className="block p-4 bg-slate-900/50 border border-slate-800 rounded-lg hover:border-slate-700 hover:bg-slate-900/70 transition"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-slate-100">{space.name}</h3>
        {space.visibility === 'private' && (
          <span className="px-2 py-1 text-xs bg-slate-800 text-slate-400 rounded">
            Private
          </span>
        )}
      </div>

      {space.description && (
        <p className="text-sm text-slate-400 mb-3 line-clamp-2">
          {space.description}
        </p>
      )}

      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span>by {space.owner.displayName || space.owner.username}</span>
        <span>{space.memberCount} members</span>
        <span>{space.articleCount} articles</span>
      </div>

      {space.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {space.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 text-xs bg-slate-800/50 text-slate-400 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {showJoinButton && !space.isMember && (
        <button
          onClick={handleJoin}
          className="mt-3 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          Join Space
        </button>
      )}

      {space.isMember && (
        <div className="mt-3 text-xs text-slate-400">
          {space.memberRole === 'owner' && '👑 Owner'}
          {space.memberRole === 'moderator' && '⚡ Moderator'}
          {space.memberRole === 'member' && '✓ Member'}
        </div>
      )}
    </Link>
  );
}