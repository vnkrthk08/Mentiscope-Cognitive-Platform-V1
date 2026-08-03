import { readFile } from 'fs/promises';
import { Pool } from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sqlPath = path.join(__dirname, '..', 'src', 'db', 'migrations', '001_create_analytics_table.sql');

async function run() {
  try {
    const sql = await readFile(sqlPath, { encoding: 'utf8' });
    const pool = new Pool({ connectionString: process.env.PG_CONNECTION_STRING });
    await pool.query(sql);
    console.log('Migration applied successfully');
    await pool.end();
  } catch (err) {
    console.error('Migration failed:', err);
    process.exit(1);
  }
}

run();
