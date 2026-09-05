import { Router, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { pool } from '../../db'; // Assuming a pg pool is exported from src/db/index.ts

const router = Router();

// Helper to set HttpOnly JWT cookie
function setAuthCookie(res: Response, token: string) {
  res.cookie('auth_token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 1000, // 1 hour
  });
}

// Registration (student only as example)
router.post('/student/register', async (req: Request, res: Response) => {
  const { email, password, name } = req.body;
  if (!email || !password || !name) {
    return res.status(400).json({ message: 'Missing fields' });
  }
  const hash = await bcrypt.hash(password, 12);
  try {
    await pool.query(
      'INSERT INTO users (email, password_hash, name, role) VALUES ($1, $2, $3, $4)',
      [email, hash, name, 'student']
    );
    res.status(201).json({ message: 'User registered' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Database error' });
  }
});

// Login (student, intern, admin share same endpoint with role check)
router.post('/login', async (req: Request, res: Response) => {
  const { email, password, role } = req.body; // role should be one of 'student' | 'intern' | 'admin'
  if (!email || !password || !role) {
    return res.status(400).json({ message: 'Missing fields' });
  }
  const result = await pool.query('SELECT id, password_hash, role FROM users WHERE email=$1', [email]);
  if (result.rowCount === 0) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const user = result.rows[0];
  if (user.role !== role) {
    return res.status(403).json({ message: 'Role mismatch' });
  }
  const match = await bcrypt.compare(password, user.password_hash);
  if (!match) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const token = jwt.sign({ userId: user.id, role: user.role }, process.env.JWT_SECRET || 'secret', {
    expiresIn: '1h',
  });
  setAuthCookie(res, token);
  res.json({ message: 'Logged in' });
});

// Refresh token endpoint – generates a new short‑lived JWT and rewrites the HttpOnly cookie
router.post('/refresh', (req: Request, res: Response) => {
  const token = req.cookies?.auth_token;
  if (!token) {
    return res.status(401).json({ message: 'No token' });
  }
  try {
    const payload: any = jwt.verify(token, process.env.JWT_SECRET || 'secret');
    const newToken = jwt.sign({ userId: payload.userId, role: payload.role }, process.env.JWT_SECRET || 'secret', {
      expiresIn: '1h',
    });
    setAuthCookie(res, newToken);
    res.json({ message: 'Token refreshed' });
  } catch (e) {
    res.status(401).json({ message: 'Invalid token' });
  }
});

// Logout – clears the HttpOnly cookie
router.post('/logout', (_req: Request, res: Response) => {
  res.clearCookie('auth_token');
  res.json({ message: 'Logged out' });
});

export default router;
