# Production Deployment Guide

This guide covers the deployment process for the Vue 3 Spatial Jobs Index application.

## Prerequisites

- Node.js 18+ installed
- npm 9+ installed
- Access to production server/hosting platform
- Environment variables configured
- GitHub Actions secrets configured (for automated deployment)

## Environment Configuration

### Required Environment Variables

Create a `.env.production` file with:

```env
VITE_API_BASE_URL=https://api.your-domain.com
VITE_MAPBOX_TOKEN=your_production_mapbox_token
```

### Security Considerations

- Never commit `.env` files to version control
- Use environment-specific Mapbox tokens
- Ensure CORS is properly configured on the API server
- Enable HTTPS for production deployment

## Build Process

### 1. Install Dependencies

```bash
npm ci --production
```

### 2. Run Production Build

```bash
npm run build
```

This will:
- Run TypeScript type checking
- Bundle and minify all assets
- Generate optimized chunks for caching
- Create production-ready files in `dist/` directory

### 3. Verify Build Output

Expected output structure:
```
dist/
├── index.html
├── access_occupation.html
├── access_school_of_study.html
├── access_wagelvl.html
├── travel_time.html
├── chunks/
│   ├── vue-vendor-[hash].js (~90KB)
│   ├── state-vendor-[hash].js (~4KB)
│   ├── components-[hash].js
│   └── ...
└── assets/
    └── [static assets]
```

## Deployment Options

### Option 1: GitHub Pages

For GitHub Pages deployment:

```bash
npm run deploy
```

This will build and push to the `gh-pages` branch.

### Option 2: Static Hosting (Netlify, Vercel, etc.)

1. Connect your repository to the hosting platform
2. Configure build settings:
   - Build command: `npm run build`
   - Output directory: `dist`
   - Node version: 18+

### Option 3: Traditional Web Server (Apache/Nginx)

1. Build the application locally or in CI
2. Copy the `dist/` folder contents to your web server
3. Configure server for SPA routing:

**Nginx Configuration:**
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

**Apache Configuration (.htaccess):**
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

## Continuous Deployment

### GitHub Actions Workflow

The repository includes automated deployment via GitHub Actions:

1. Push to `master` branch triggers CI workflow
2. CI runs tests, linting, and type checking
3. On success, Build workflow creates production artifacts
4. Deploy workflow publishes to production

### Manual Deployment Checklist

- [ ] Run all tests: `npm run test:run`
- [ ] Check type safety: `npm run type-check`
- [ ] Run linting: `npm run lint`
- [ ] Build production bundle: `npm run build`
- [ ] Test production build locally: `npm run preview`
- [ ] Verify environment variables
- [ ] Deploy to staging environment first
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Verify production deployment

## Performance Monitoring

After deployment, monitor:

1. **Bundle Size**: Check that JavaScript chunks are properly cached
2. **Load Time**: Verify initial page load is under 3 seconds
3. **API Response**: Ensure backend endpoints are responsive
4. **Error Tracking**: Monitor browser console for runtime errors

### Recommended Monitoring Tools

- Google Lighthouse (performance audits)
- WebPageTest (detailed performance metrics)
- Sentry (error tracking)
- Google Analytics (user metrics)

## Rollback Procedure

If issues occur after deployment:

1. **GitHub Pages**: Revert to previous commit and redeploy
2. **Static Hosting**: Use platform's rollback feature or redeploy previous version
3. **Traditional Server**: Keep previous build directory and swap if needed

```bash
# Keep backup of current deployment
cp -r /var/www/html /var/www/html.backup

# If rollback needed
mv /var/www/html /var/www/html.failed
mv /var/www/html.backup /var/www/html
```

## Troubleshooting

### Common Issues

**1. Blank Page After Deployment**
- Check browser console for errors
- Verify API endpoints are accessible
- Ensure base URL is correctly configured

**2. Routing Not Working**
- Verify server is configured for SPA routing
- Check that all HTML files are present

**3. Map Not Loading**
- Verify Mapbox token is valid for production domain
- Check network tab for failed requests

**4. API Connection Issues**
- Verify CORS configuration
- Check API base URL in environment variables
- Ensure HTTPS is used in production

## Security Checklist

- [ ] Environment variables are properly secured
- [ ] API endpoints use HTTPS
- [ ] Sensitive data is not exposed in client bundle
- [ ] Content Security Policy headers configured
- [ ] Rate limiting implemented on API

## Support

For deployment issues:
1. Check deployment logs in GitHub Actions
2. Review browser console for client-side errors
3. Verify API health and availability
4. Contact the development team for assistance

---

Last Updated: 2025-08-28
