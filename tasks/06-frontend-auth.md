# Task 06: Frontend Authentication Flow

## Objective
Implement the complete authentication flow in the Next.js frontend, including GitHub OAuth callback handling, JWT token management, and protected routes.

## Current State
- Homepage has GitHub sign-in button linking to `/api/auth/login/github`
- Backend OAuth endpoints will be implemented (Task 01)
- No auth state management in frontend

## Acceptance Criteria
- [ ] GitHub OAuth flow completes end-to-end
- [ ] JWT tokens stored and managed properly
- [ ] Protected routes redirect to login
- [ ] User context available throughout app
- [ ] Sign out functionality works
- [ ] Auth state persists on refresh

## Implementation Details

### 0. Check Existing Codebase
Before implementing, verify current state:

```bash
# Check existing page structure
ls -la apps/web/src/app/
cat apps/web/src/app/page.tsx

# Check for existing auth components
find apps/web/src -name "*.tsx" -o -name "*.ts" | xargs grep -l "auth\|Auth"

# Check for contexts folder
ls -la apps/web/src/contexts/ 2>/dev/null

# Check for existing hooks
ls -la apps/web/src/hooks/ 2>/dev/null

# Check layout file
cat apps/web/src/app/layout.tsx

# Check for auth callback route
ls -la apps/web/src/app/auth/ 2>/dev/null

# Check installed dependencies
grep -E "next-auth|jose|js-cookie" apps/web/package.json

# Check for existing components
ls -la apps/web/src/components/

# Check environment variables
cat apps/web/.env.example 2>/dev/null || cat .env.example | grep NEXT
```

### 1. Auth Context Provider
Create `apps/web/src/contexts/auth-context.tsx`:

```tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  username: string;
  name: string;
  avatar_url?: string;
  bio?: string;
  expertise_tags: string[];
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: () => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check auth status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const response = await fetch('/api/me', {
        credentials: 'include',
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      setError('Failed to check authentication');
    } finally {
      setLoading(false);
    }
  }

  async function refreshUser() {
    await checkAuth();
  }

  function login() {
    // Redirect to GitHub OAuth
    window.location.href = '/api/auth/login/github';
  }

  async function logout() {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        setUser(null);
        router.push('/');
      }
    } catch (err) {
      console.error('Logout failed:', err);
      setError('Failed to logout');
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### 2. Auth Callback Page
Create `apps/web/src/app/auth/callback/page.tsx`:

```tsx
'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    async function handleCallback() {
      const error = searchParams.get('error');
      const error_description = searchParams.get('error_description');

      if (error) {
        // Handle error
        console.error('OAuth error:', error, error_description);
        router.push(`/?auth_error=${encodeURIComponent(error_description || error)}`);
        return;
      }

      // Success - cookie should be set by backend
      // Redirect to feed or intended destination
      const returnTo = searchParams.get('return_to') || '/feed';
      router.push(returnTo);
    }

    handleCallback();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-slate-300"></div>
        <p className="mt-4 text-slate-300">Completing authentication...</p>
      </div>
    </div>
  );
}
```

### 3. Root Layout with Auth Provider
Update `apps/web/src/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/auth-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Collective Hub",
  description: "Connect, Learn, Build Together",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### 4. Protected Route Component
Create `apps/web/src/components/auth/protected-route.tsx`:

```tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  redirectTo = '/'
}: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push(redirectTo);
    }
  }, [user, loading, router, redirectTo]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-300"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
```

### 5. Navigation Component with Auth
Create `apps/web/src/components/layout/navigation.tsx`:

```tsx
'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function Navigation() {
  const { user, login, logout } = useAuth();

  return (
    <nav className="border-b border-slate-800 bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-semibold text-slate-100">
              AI Collective
            </Link>

            {user && (
              <div className="hidden md:flex items-center gap-6">
                <Link href="/feed" className="text-sm text-slate-300 hover:text-slate-100">
                  Feed
                </Link>
                <Link href="/articles/new" className="text-sm text-slate-300 hover:text-slate-100">
                  Write
                </Link>
                <Link href="/spaces" className="text-sm text-slate-300 hover:text-slate-100">
                  Spaces
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar_url} alt={user.name} />
                      <AvatarFallback>{user.name.charAt(0).toUpperCase()}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <DropdownMenuItem asChild>
                    <Link href={`/users/${user.username}`}>
                      <div className="flex flex-col">
                        <span className="font-medium">{user.name}</span>
                        <span className="text-xs text-slate-500">@{user.username}</span>
                      </div>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/settings/profile">Settings</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/articles/drafts">My Drafts</Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout} className="text-red-600">
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button onClick={login} size="sm">
                Sign in with GitHub
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
```

### 6. Update Homepage for Auth State
Update `apps/web/src/app/page.tsx`:

```tsx
'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function Home() {
  const { user, loading, login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const authError = searchParams.get('auth_error');

  useEffect(() => {
    // Redirect to feed if already authenticated
    if (!loading && user) {
      router.push('/feed');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-300"></div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <div className="mx-auto flex w-full max-w-xl flex-1 flex-col justify-center gap-10 px-6 py-16">
        <header className="space-y-3">
          <h1 className="text-4xl font-semibold tracking-tight">
            AI Collective Hub
          </h1>
          <p className="text-base text-slate-300">
            Connect with AI practitioners, share knowledge, and collaborate on cutting-edge projects.
          </p>
        </header>

        {authError && (
          <Alert variant="destructive">
            <AlertDescription>
              Authentication failed: {authError}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          <Button
            onClick={login}
            size="lg"
            className="w-full"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" className="mr-2 h-5 w-5 fill-current">
              <path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58l-.02-2.26c-3.34.73-4.04-1.61-4.04-1.61-.55-1.41-1.35-1.79-1.35-1.79-1.1-.77.09-.76.09-.76 1.22.09 1.86 1.27 1.86 1.27 1.08 1.86 2.82 1.32 3.5 1.01.11-.79.42-1.32.76-1.62-2.67-.3-5.47-1.34-5.47-5.98 0-1.32.47-2.39 1.24-3.23-.13-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.46 11.46 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.66 1.65.25 2.87.12 3.17.77.84 1.23 1.91 1.23 3.23 0 4.65-2.81 5.68-5.49 5.98.44.38.82 1.12.82 2.26l-.01 3.35c0 .32.21.7.83.58A12 12 0 0 0 12 .5Z" />
            </svg>
            Sign in with GitHub
          </Button>
        </div>
      </div>
    </main>
  );
}
```

### 7. Feed Page (Protected)
Create `apps/web/src/app/feed/page.tsx`:

```tsx
'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { Navigation } from '@/components/layout/navigation';

export default function FeedPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950">
        <Navigation />
        <main className="mx-auto max-w-7xl px-4 py-8">
          <h1 className="text-2xl font-semibold text-slate-100">Feed</h1>
          <p className="mt-2 text-slate-300">
            Welcome to your personalized feed. Articles will appear here.
          </p>
        </main>
      </div>
    </ProtectedRoute>
  );
}
```

## Testing Steps

1. **Test GitHub OAuth Flow**
   - Click "Sign in with GitHub" on homepage
   - Should redirect to GitHub authorization
   - After approval, should redirect back to `/feed`
   - User data should be available in context

2. **Test Protected Routes**
   - Try accessing `/feed` without authentication
   - Should redirect to homepage
   - After login, should access protected pages

3. **Test Logout**
   - Click user dropdown → Sign out
   - Should clear session and redirect to homepage
   - Protected routes should no longer be accessible

4. **Test Persistence**
   - Login successfully
   - Refresh the page
   - Should remain logged in
   - User data should persist

## Success Metrics
- OAuth flow completes in < 3 seconds
- Auth state available immediately
- Protected routes properly secured
- No flickering during auth checks

## Dependencies
- Task 01 (Backend OAuth) must be complete
- shadcn/ui components installed
- Next.js 14 with App Router

## Common Issues

### Issue: Cookie not being set
- Solution: Ensure CORS credentials are enabled
- Check SameSite and Secure cookie settings

### Issue: Auth state lost on refresh
- Solution: Check cookie persistence
- Ensure `/api/me` endpoint works

### Issue: Redirect loop
- Solution: Check protected route logic
- Ensure proper redirect paths

## Notes for AI Agents
- Use client components for auth state
- Keep auth logic simple for MVP
- Don't implement refresh tokens yet
- Focus on cookie-based sessions