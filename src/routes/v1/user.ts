import { Router, Request, Response } from 'express';
import { pool } from '../../db';

const router = Router();

// Get current user profile (requires auth middleware that sets req.user)
router.get('/me', async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ message: 'Unauthenticated' });
  }
  try {
    const result = await pool.query(
      'SELECT id, email, name, role FROM users WHERE id = $1',
      [userId]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json({ user: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Database error' });
  }
});

// Update user profile (allow name change for demo)
router.put('/me', async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  const { name } = req.body;
  if (!userId || !name) {
    return res.status(400).json({ message: 'Missing fields' });
  }
  try {
    await pool.query('UPDATE users SET name = $1 WHERE id = $2', [name, userId]);
    res.json({ message: 'Profile updated' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Database error' });
  }
});

export default router;
