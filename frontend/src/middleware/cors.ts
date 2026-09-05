import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const allowedOrigin = process.env.FRONTEND_ORIGIN || '*';

export const corsMiddleware = cors({
  origin: allowedOrigin,
  credentials: true,
});
