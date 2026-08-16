import swaggerUi from 'swagger-ui-express';
import yaml from 'yamljs';
import { Router } from 'express';
import path from 'path';

const router = Router();

// Load Swagger spec (assumes swagger.yaml exists at project root)
const swaggerDoc = yaml.load(path.join(process.cwd(), 'swagger.yaml'));

router.use('/swagger', swaggerUi.serve, swaggerUi.setup(swaggerDoc));

// Optional Redoc endpoint (if you prefer Redoc)
router.get('/redoc', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>API Docs</title>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
      </head>
      <body>
        <redoc spec-url="/api/v1/docs/swagger/swagger.json"></redoc>
      </body>
    </html>
  `);
});

export default router;
