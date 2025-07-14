import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

describe('access_school_of_study.html', () => {
  describe('Build configuration', () => {
    it('should have schoolOfStudy entry point in vite.config.ts', () => {
      const viteConfigPath = path.join(process.cwd(), 'vite.config.ts');
      const viteConfigContent = fs.readFileSync(viteConfigPath, 'utf-8');
      expect(viteConfigContent).toContain("schoolOfStudy: 'access_school_of_study.html'");
    });
  });

  describe('HTML structure', () => {
    it('should have school of study HTML file that exists', () => {
      // This test will fail initially until we create the HTML file
      const htmlPath = path.join(process.cwd(), 'access_school_of_study.html');
      const fileExists = fs.existsSync(htmlPath);
      expect(fileExists).toBe(true);
    });

    it('should have correct page title', () => {
      const htmlPath = path.join(process.cwd(), 'access_school_of_study.html');
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      expect(htmlContent).toContain(
        '<title>LMIC DFW Employment Access Index - Job Access by School of Study</title>'
      );
    });

    it('should have school-select dropdown with correct ID and placeholder', () => {
      const htmlPath = path.join(process.cwd(), 'access_school_of_study.html');
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      expect(htmlContent).toContain('id="school-select"');
      expect(htmlContent).toContain('Select a school of study...');
    });
  });

  describe('Navigation integration', () => {
    it('should have school of study link marked as active in navigation', () => {
      const htmlPath = path.join(process.cwd(), 'access_school_of_study.html');
      const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
      expect(htmlContent).toContain('class="nav-link active" href="access_school_of_study.html"');
      expect(htmlContent).toContain('Job Access by School of Study');
    });
  });
});
