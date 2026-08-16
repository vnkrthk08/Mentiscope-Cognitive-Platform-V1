// src/middleware/securityHeaders.ts
import type { Request, Response, NextFunction } from 'express';

// Helmet‑style security headers for production environments
export const securityHeaders = (req: Request, res: Response, next: NextFunction) => {
  // Content Security Policy – relaxed in dev mode for Vite HMR / WebSockets, restricted in prod
  if (process.env.NODE_ENV !== 'production') {
    res.setHeader(
      'Content-Security-Policy',
      "default-src 'self' 'unsafe-inline' 'unsafe-eval' ws: wss:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; font-src https://fonts.gstatic.com; connect-src 'self' ws: wss:; frame-ancestors 'none';"
    );
  } else {
    res.setHeader(
      'Content-Security-Policy',
      "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; font-src https://fonts.gstatic.com; connect-src 'self'; frame-ancestors 'none';"
    );
  }
  // Disable MIME sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');
  // Click‑jacking protection
  res.setHeader('X-Frame-Options', 'DENY');
  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  // HSTS – enforce HTTPS if request is secure
  if (req.secure) {
    res.setHeader('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  }
  next();
};
