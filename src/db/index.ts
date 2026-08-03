// src/db/index.ts
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

export const pool = new Pool({
  connectionString: process.env.PG_CONNECTION_STRING,
});

export const query = (text: string, params?: any[]) => {
  return pool.query(text, params);
};
