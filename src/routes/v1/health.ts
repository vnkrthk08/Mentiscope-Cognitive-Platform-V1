import { Router } from 'express';
import fs from 'fs';
import path from 'path';

export const healthRouter = Router();

healthRouter.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

healthRouter.get('/version', (req, res) => {
  let version = '0.0.0';
  try {
    const pkgPath = path.join(process.cwd(), 'package.json');
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    version = pkg.version;
  } catch (e) {
    console.error('Failed to read package.json version');
  }

  res.json({
    version: version,
    commit: process.env.COMMIT_HASH || 'none',
    buildDate: process.env.BUILD_DATE || new Date().toISOString()
  });
});
