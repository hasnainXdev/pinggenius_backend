import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

// This function can be marked `async` if using `await` inside
export async function middleware(request: NextRequest) {
  // Check if the request is for the dashboard route
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    // Get the token from cookies
    const token = await getToken({ req: request, secret: process.env.AUTH_SECRET });
    
    // If no token exists, redirect to home page
    if (!token) {
      return NextResponse.redirect(new URL('/', request.url));
    }
  }
  
  // Continue with the request if no redirect is needed
  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: [
    '/dashboard/:path*', // Only match dashboard routes for auth protection
  ],
};