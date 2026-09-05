import { Router, Request, Response } from 'express';

export const webhooksRouter = Router();

// Endpoint to receive external event triggers (e.g. LMS sync)
webhooksRouter.post('/event', (req: Request, res: Response) => {
  const payload = req.body;
  console.log('[Webhook Event Received]:', payload);
  // Log event/action or store in database
  res.json({ status: 'success', received: true });
});
