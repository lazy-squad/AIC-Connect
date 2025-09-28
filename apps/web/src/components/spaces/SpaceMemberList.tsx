"use client";

import { useState, useEffect } from "react";
import { SpaceMember } from "@/types/space";

interface SpaceMemberListProps {
  spaceId: string;
  canManage: boolean;
  onRoleChange?: (userId: string, role: string) => void;
}

export function SpaceMemberList({ spaceId, canManage, onRoleChange }: SpaceMemberListProps) {
  const [members, setMembers] = useState<SpaceMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await fetch(`/api/spaces/${spaceId}/members`, {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch members");
        }

        const data = await response.json();
        setMembers(data.members);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load members");
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [spaceId]);

  const handleRoleChange = async (userId: string, newRole: string) => {
    if (!onRoleChange) return;

    try {
      const response = await fetch(`/api/spaces/${spaceId}/members/${userId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ role: newRole }),
      });

      if (response.ok) {
        onRoleChange(userId, newRole);
        // Update local state
        setMembers(members.map(m =>
          m.user.id === userId ? { ...m, role: newRole as any } : m
        ));
      }
    } catch (err) {
      console.error("Failed to update member role:", err);
    }
  };

  if (loading) {
    return <div className="text-slate-400">Loading members...</div>;
  }

  if (error) {
    return <div className="text-red-400">Error: {error}</div>;
  }

  if (members.length === 0) {
    return <div className="text-slate-400">No members yet</div>;
  }

  return (
    <div className="space-y-4">
      {members.map((member) => (
        <div
          key={member.user.id}
          className="flex items-center justify-between p-4 bg-slate-900/50 border border-slate-800 rounded-lg"
        >
          <div className="flex items-center gap-4">
            {member.user.avatarUrl ? (
              <img
                src={member.user.avatarUrl}
                alt={member.user.displayName || member.user.username}
                className="w-10 h-10 rounded-full"
              />
            ) : (
              <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center">
                <span className="text-slate-400 text-sm">
                  {(member.user.displayName || member.user.username || '?')[0].toUpperCase()}
                </span>
              </div>
            )}
            <div>
              <div className="text-slate-200 font-medium">
                {member.user.displayName || member.user.username}
              </div>
              <div className="text-xs text-slate-500">
                Joined {new Date(member.joinedAt).toLocaleDateString()}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {member.role === 'owner' && (
              <span className="px-3 py-1 text-sm bg-yellow-900/20 text-yellow-400 rounded">
                👑 Owner
              </span>
            )}
            {member.role === 'moderator' && (
              <span className="px-3 py-1 text-sm bg-purple-900/20 text-purple-400 rounded">
                ⚡ Moderator
              </span>
            )}
            {member.role === 'member' && (
              <span className="px-3 py-1 text-sm bg-slate-800 text-slate-400 rounded">
                Member
              </span>
            )}

            {canManage && member.role !== 'owner' && (
              <select
                value={member.role}
                onChange={(e) => handleRoleChange(member.user.id, e.target.value)}
                className="ml-2 px-2 py-1 text-sm bg-slate-800 text-slate-200 rounded border border-slate-700"
              >
                <option value="member">Member</option>
                <option value="moderator">Moderator</option>
              </select>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}