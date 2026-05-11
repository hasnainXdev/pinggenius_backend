/**
 * Utility functions for network connectivity and error handling
 */

/**
 * Checks if the user has network connectivity
 * @returns boolean indicating if online
 */
export function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

/**
 * Shows a user-friendly message when network connectivity is lost
 */
export function showOfflineNotification(): void {
  // Using toast notification to inform the user
  if (typeof window !== 'undefined') {
    // Dynamically import toast to avoid SSR issues
    import('sonner').then(({ toast }) => {
      toast.warning("Oh no! 🌐 You seem to be offline!", {
        description: "Please check your internet connection. Your work will be saved locally and can be synced when you're back online.",
        duration: 5000,
      });
    });
  }
}

/**
 * Handles network interruption during API calls
 * @param error The error object from the API call
 * @returns boolean indicating if it was a network error
 */
export function handleNetworkError(error: any): boolean {
  // Check if it's a network error (no internet, timeout, etc.)
  if (error?.isAxiosError) {
    if (!error.response) {
      // No response means network error (offline, timeout, etc.)
      showOfflineNotification();
      return true;
    }
  }
  
  // Also check for common network error indicators
  if (error?.message?.includes('Network Error') || 
      error?.message?.includes('Failed to fetch') ||
      error?.message?.includes('Load failed')) {
    showOfflineNotification();
    return true;
  }
  
  return false;
}