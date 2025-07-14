import { describe, it, expect, beforeEach } from 'vitest';
import { createNavigation, renderNavigation } from '../../../components/navigation';
import { BRANDING } from '../../../js/constants';

describe('navigation', () => {
  describe('createNavigation', () => {
    it('should create navigation HTML with no active page', () => {
      const html = createNavigation();

      expect(html).toContain('navbar navbar-expand-lg');
      expect(html).toContain(BRANDING.homeUrl);
      expect(html).toContain(BRANDING.logoUrl);
      expect(html).toContain('Project Home');
      expect(html).toContain('Job Access by Wage Level');
      expect(html).toContain('Job Access by Occupation');
      expect(html).not.toContain('active');
    });

    it('should mark wage page as active', () => {
      const html = createNavigation('wage');

      expect(html).toContain('Job Access by Wage Level');
      expect(html).toContain('nav-link active');
      expect(html).toContain('href="access_wagelvl.html"');
      // Check that the active class is on the wage link
      const wageMatch = html.match(/nav-link[^>]*href="access_wagelvl.html"/);
      expect(wageMatch?.[0]).toContain('active');
    });

    it('should mark occupation page as active', () => {
      const html = createNavigation('occupation');

      expect(html).toContain('Job Access by Occupation');
      expect(html).toMatch(/nav-link\s+active[^>]*>[\s\S]*?Job Access by Occupation/);
      expect(html).not.toMatch(/nav-link\s+active[^>]*>[\s\S]*?Job Access by Wage Level/);
    });

    it('should include all navigation links', () => {
      const html = createNavigation();

      expect(html).toContain('href="index.html"');
      expect(html).toContain('href="access_wagelvl.html"');
      expect(html).toContain('href="access_occupation.html"');
      // These should be proper links, not placeholders
      expect(html).toContain('href="access_school_of_study.html"');
      expect(html).toContain('href="travel_time.html"');
      expect(html).toContain('Job Access by School of Study');
      expect(html).toContain('Travel Time Analysis');
      // Should NOT contain the old placeholder text
      expect(html).not.toContain('(in progress)');
    });

    it('should mark school page as active', () => {
      const html = createNavigation('school');

      expect(html).toContain('Job Access by School of Study');
      expect(html).toMatch(/nav-link\s+active[^>]*>[\s\S]*?Job Access by School of Study/);
      expect(html).not.toMatch(/nav-link\s+active[^>]*>[\s\S]*?Job Access by Wage Level/);
    });

    it('should mark travel page as active', () => {
      const html = createNavigation('travel');

      expect(html).toContain('Travel Time Analysis');
      expect(html).toMatch(/nav-link\s+active[^>]*>[\s\S]*?Travel Time Analysis/);
      expect(html).not.toMatch(/nav-link\s+active[^>]*>[\s\S]*?Job Access by Wage Level/);
    });

    it('should include bootstrap collapse functionality', () => {
      const html = createNavigation();

      expect(html).toContain('data-bs-toggle="collapse"');
      expect(html).toContain('data-bs-target="#bannertoggle"');
      expect(html).toContain('navbar-toggler');
      expect(html).toContain('id="bannertoggle"');
    });
  });

  describe('renderNavigation', () => {
    beforeEach(() => {
      document.body.innerHTML = '';
    });

    it('should render navigation into container', () => {
      const container = document.createElement('div');
      container.id = 'nav-container';
      document.body.appendChild(container);

      renderNavigation('nav-container', 'wage');

      expect(container.innerHTML).toContain('navbar');
      expect(container.innerHTML).toContain(BRANDING.logoUrl);
      expect(container.innerHTML).toMatch(
        /nav-link\s+active[^>]*>[\s\S]*?Job Access by Wage Level/
      );
    });

    it('should handle missing container gracefully', () => {
      // Should not throw when container doesn't exist
      expect(() => renderNavigation('non-existent', 'wage')).not.toThrow();
    });

    it('should render with no active page when not specified', () => {
      const container = document.createElement('div');
      container.id = 'nav-container';
      document.body.appendChild(container);

      renderNavigation('nav-container');

      expect(container.innerHTML).toContain('navbar');
      expect(container.innerHTML).not.toContain('active');
    });
  });
});
