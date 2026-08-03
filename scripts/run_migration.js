const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const sqlPath = path.join(__dirname, '..', 'src', 'db', 'migrations', '001_create_analytics_table.sql');
const sql = fs.readFileSync(sqlPath, { encoding: 'utf8' });

const pool = new Pool({ connectionString: process.env.PG_CONNECTION_STRING });

(async () => {
  try {
    const res = await pool.query(sql);
    console.log('Migration applied successfully');
  } catch (err) {
    console.error('Migration failed:', err);
    process.exit(1);
  } finally {
    await pool.end();
  }
})();
