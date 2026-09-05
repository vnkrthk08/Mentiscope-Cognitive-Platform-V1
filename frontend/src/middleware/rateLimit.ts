// src/middleware/rateLimit.ts
import rateLimit from 'express-rate-limit';

export const apiRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000, // Increased for development and testing
  standardHeaders: true,
  legacyHeaders: false,
});
