"use client";

import { Space } from "@/types/space";

interface SpaceHeaderProps {
  space: Space;
  isMember: boolean;
  memberRole?: string;
  onJoin: () => void;
  onLeave: () => void;
  onEdit: () => void;
}

export function SpaceHeader({
  space,
  isMember,
  memberRole,
  onJoin,
  onLeave,
  onEdit,
}: SpaceHeaderProps) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">{space.name}</h1>
          {space.description && (
            <p className="text-slate-400">{space.description}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {space.visibility === 'private' && (
            <span className="px-3 py-1 text-sm bg-slate-800 text-slate-400 rounded">
              Private
            </span>
          )}

          {memberRole === 'owner' && (
            <button
              onClick={onEdit}
              className="px-4 py-2 text-sm bg-slate-800 text-slate-200 rounded hover:bg-slate-700 transition"
            >
              Edit Space
            </button>
          )}

          {!isMember ? (
            <button
              onClick={onJoin}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            >
              Join Space
            </button>
          ) : memberRole !== 'owner' ? (
            <button
              onClick={onLeave}
              className="px-4 py-2 text-sm bg-slate-800 text-slate-200 rounded hover:bg-slate-700 transition"
            >
              Leave Space
            </button>
          ) : null}
        </div>
      </div>

      <div className="flex items-center gap-6 text-sm text-slate-400">
        <div>
          <span className="text-slate-500">Owner: </span>
          <span className="text-slate-300">
            {space.owner.displayName || space.owner.username}
          </span>
        </div>
        <div>
          <span className="text-slate-500">Members: </span>
          <span className="text-slate-300">{space.memberCount}</span>
        </div>
        <div>
          <span className="text-slate-500">Articles: </span>
          <span className="text-slate-300">{space.articleCount}</span>
        </div>
      </div>

      {space.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {space.tags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 text-sm bg-slate-800/50 text-slate-400 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {isMember && (
        <div className="mt-4 text-sm text-slate-400">
          Your role: {' '}
          <span className="text-slate-300">
            {memberRole === 'owner' && '👑 Owner'}
            {memberRole === 'moderator' && '⚡ Moderator'}
            {memberRole === 'member' && '✓ Member'}
          </span>
        </div>
      )}
    </div>
  );
}