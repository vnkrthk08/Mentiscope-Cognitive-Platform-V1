import { Router, Request, Response } from 'express';
import { query } from '../../db';

export const analyticsRouter = Router();

// GET /api/v1/analytics/summary – aggregate usage stats per module
analyticsRouter.get('/summary', async (req: Request, res: Response) => {
  try {
    const result = await query(
      `SELECT module_id, COUNT(*) AS usage_count, AVG((metric->>'completion_time')::float) AS avg_completion_time
       FROM analytics
       GROUP BY module_id`
    );
    res.json({ summary: result.rows });
  } catch (err: any) {
    console.error('Analytics summary error', err);
    res.status(500).json({ error: 'Failed to fetch analytics summary' });
  }
});

// GET /api/v1/analytics/user/:id – per‑user performance history
analyticsRouter.get('/user/:id', async (req: Request, res: Response) => {
  const userId = req.params.id;
  try {
    const result = await query(
      `SELECT * FROM analytics WHERE user_id = $1 ORDER BY created_at DESC`,
      [userId]
    );
    res.json({ userId, records: result.rows });
  } catch (err: any) {
    console.error('User analytics error', err);
    res.status(500).json({ error: 'Failed to fetch user analytics' });
  }
});
