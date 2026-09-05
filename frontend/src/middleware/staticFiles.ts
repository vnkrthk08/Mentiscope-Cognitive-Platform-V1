import path from 'path';
import express from 'express';

export const staticFiles = express.static(path.join(process.cwd(), 'public', 'static'));
