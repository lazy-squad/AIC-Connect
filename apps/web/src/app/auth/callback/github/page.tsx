'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function GitHubCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      if (errorParam) {
        setError(errorDescription || 'Authentication failed');
        setIsLoading(false);
        return;
      }

      if (!code || !state) {
        setError('Missing required parameters');
        setIsLoading(false);
        return;
      }

      try {
        // Call the backend OAuth callback endpoint
        const response = await fetch(`/api/auth/github/callback?code=${code}&state=${state}`, {
          method: 'GET',
          credentials: 'include',
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Authentication failed');
        }

        const data = await response.json();

        // Store user data if needed
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
        }

        // Redirect to the dashboard or home page
        router.push('/');
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError(err instanceof Error ? err.message : 'Authentication failed');
        setIsLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Completing authentication...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h2 className="mt-4 text-lg font-medium text-gray-900">Authentication Failed</h2>
            <p className="mt-2 text-sm text-gray-600">{error}</p>
            <div className="mt-6">
              <button
                onClick={() => router.push('/auth/login')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}