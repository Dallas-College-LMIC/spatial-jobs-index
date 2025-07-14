import { BRANDING } from '../js/constants';

export function createNavigation(activePageTitle: string = ''): string {
  return `
        <nav class="navbar navbar-expand-lg navbar-dark g-0 p-0 m-0" id="banner">
            <a class="navbar-brand p-0" href="${BRANDING.homeUrl}">
                <img src="${BRANDING.logoUrl}" id="dc_logo" alt="Dallas College Logo" />
            </a>
            <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#bannertoggle"
            >
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse p-0 justify-content-start" id="bannertoggle">
                <ul class="navbar-nav p-0">
                    <a class="nav-link" href="index.html">Project Home</a>
                    <a class="nav-link ${activePageTitle === 'wage' ? 'active' : ''}" href="access_wagelvl.html">
                        Job Access by Wage Level
                    </a>
                    <a class="nav-link ${activePageTitle === 'occupation' ? 'active' : ''}" href="access_occupation.html">
                        Job Access by Occupation
                    </a>
                    <a class="nav-link ${activePageTitle === 'school' ? 'active' : ''}" href="access_school_of_study.html">
                        Job Access by School of Study
                    </a>
                    <a class="nav-link ${activePageTitle === 'travel' ? 'active' : ''}" href="travel_time.html">
                        Travel Time Analysis
                    </a>
                </ul>
            </div>
        </nav>
    `;
}

export function renderNavigation(containerId: string, activePageTitle: string = ''): void {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = createNavigation(activePageTitle);
  }
}
