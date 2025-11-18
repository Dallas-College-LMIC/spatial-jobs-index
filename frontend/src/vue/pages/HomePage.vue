<template>
  <div class="container-fluid g-0">
    <div class="row justify-content-start">
      <div class="col-lg-6 col-md-10 ps-4">
        <h1>Dallas-Ft. Worth Spatial Jobs Index</h1>
        <h3>A Web-based Tool for Understanding Spatial Access to Employment</h3>
        <p>
          It can be difficult for economic planners, public officials, faculty, students, and the general public to access high quality information about the quality, availability, and accessibility of employment.
          This project provides a general overview of the DFW economy through use of travelshed analysis and geographical analysis.
        </p>

        <h3>About the Pages</h3>
        <p>This project is divided into 4 main pages:</p>

        <h5>Job Access by Wage Level</h5>
        <div class="col-lg-10 col-md-10 ps-3">
          <p>
            Which Census tracts have the best access to jobs? What about jobs that pay a Living Wage? Or a Community Prosperity Wage? How has that changed?
          </p>
          <p>
            This map presents summary data for all jobs, including jobs at or above key wage benchmarks. It also permits a query of previous years data, or a visualization of change from 2014 to 2024.
          </p>
          <RouterLink to="/wage" class="btn btn-primary">View Wage Map</RouterLink>
        </div>

        <h5>Job Access by Occupation</h5>
        <div class="col-lg-10 col-md-10 ps-3">
          <p>
            Which Census tracts have the best access to specific occupations? This interactive map allows you to search and explore employment accessibility by detailed occupation categories.
          </p>
          <p>
            The occupation map features a searchable dropdown with hundreds of occupation types, from healthcare and education to technology and manufacturing, showing how transit connectivity affects access to different career paths.
          </p>
          <RouterLink to="/occupation" class="btn btn-primary">View Occupation Map</RouterLink>
        </div>

        <h5>Job Access by School of Study</h5>
        <div class="col-lg-10 col-md-10 ps-3">
          <p>
            Which Census tracts have the best access to jobs for specific educational backgrounds? This interactive map allows you to explore employment accessibility based on different fields of study and educational requirements.
          </p>
          <p>
            The school of study map features detailed educational categories, from STEM fields and healthcare programs to business and liberal arts, showing how educational pathways connect to employment opportunities across the DFW region.
          </p>
          <RouterLink to="/school-of-study" class="btn btn-primary">View School of Study Map</RouterLink>
        </div>

        <h5>Travel Time Analysis</h5>
        <div class="col-lg-10 col-md-10 ps-3">
          <p>
            Click on any census tract to see the travel time isochrones - areas reachable within specific time intervals using public transit.
          </p>
          <p>
            This interactive visualization shows how far you can travel from any selected census tract in 5-minute increments, from under 5 minutes to over 45 minutes, helping understand transit accessibility patterns across the DFW region.
          </p>
          <RouterLink to="/travel-time" class="btn btn-primary">View Travel Time Map</RouterLink>
        </div>

        <h3>Credits and Methodology</h3>
        <p>
          This project draws extensively from the NYC Department of Planning and their "Transit Travelshed" project, which can be found
          <a href="https://github.com/NYCPlanning/td-travelshed" target="_blank">here</a>.
        </p>
        <p>
          The Spatial Jobs Index Project is developed through Mapbox Travel Time API, data from Lightcast, and more. More info about coming soon.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.btn {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

h5 {
  margin-top: 1.5rem;
}
</style>
