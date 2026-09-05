import { Router, Request, Response } from 'express';

const router = Router();

// Simple i18n endpoint returning translation strings (mock implementation)
router.get('/locale/:lang', (req: Request, res: Response) => {
  const { lang } = req.params;
  // In a real app, you would load language files. Here we return a static example.
  const messages = {
    en: { welcome: 'Welcome to Mentiscope', logout: 'Logout' },
    es: { welcome: 'Bienvenido a Mentiscope', logout: 'Cerrar sesión' },
    hi: { welcome: 'मेंटिस्कोप में आपका स्वागत है', logout: 'लॉगआउट' },
  };
  const locale = messages[lang] || messages['en'];
  res.json({ lang, messages: locale });
});

export default router;
