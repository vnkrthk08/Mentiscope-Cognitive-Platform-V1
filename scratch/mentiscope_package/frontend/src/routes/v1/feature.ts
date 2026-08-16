import { Router, Request, Response } from 'express';

const router = Router();

// In‑memory feature flag store per user (demo only)
const userFeatures: Record<string, Record<string, boolean>> = {};

// Get feature flags for a user
router.get('/:userId', (req: Request, res: Response) => {
  const { userId } = req.params;
  const features = userFeatures[userId] || {};
  res.json({ userId, features });
});

// Update/enable a feature flag for a user
router.post('/:userId/:featureName', (req: Request, res: Response) => {
  const { userId, featureName } = req.params;
  const { enabled } = req.body as { enabled: boolean };
  if (typeof enabled !== 'boolean') {
    return res.status(400).json({ error: 'enabled must be boolean' });
  }
  if (!userFeatures[userId]) userFeatures[userId] = {};
  userFeatures[userId][featureName] = enabled;
  res.json({ userId, feature: featureName, enabled });
});

export default router;
