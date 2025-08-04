from fastapi import FastAPI, HTTPException, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import cast, Any
from .database import DatabaseConfig, init_database, get_db_session
from .logging_config import CorrelationIdMiddleware
from .models import (
    OccupationsResponse,
    OccupationItem,
    GeoJSONFeatureCollection,
    OccupationGeoJSONFeatureCollection,
    IsochroneFeatureCollection,
    SchoolOfStudyIdsResponse,
    SchoolOfStudyGeoJSONFeatureCollection,
)
from .services import (
    OccupationService,
    SpatialService,
    IsochroneService,
    SchoolOfStudyService,
)

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Spatial Jobs Index API",
    description="""
    A comprehensive API for accessing spatial job market data, including:

    ## Features
    * **Occupation Data**: Get occupation IDs and spatial GeoJSON data for job market analysis
    * **School of Study**: Access educational program data mapped to job opportunities
    * **Travel Time Analysis**: Isochrone data for commute time analysis
    * **Spatial Visualization**: GeoJSON responses ready for map visualization

    ## Rate Limiting
    All endpoints are rate-limited to 30 requests per minute to ensure fair usage.

    ## Data Sources
    Data includes z-scored job openings and employment statistics for spatial analysis.
    """,
    version="1.0.0",
    contact={
        "name": "Dallas College Labor Market Intelligence Center",
        "url": "https://github.com/Dallas-College-LMIC/spatial-jobs-index",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/Dallas-College-LMIC/spatial-jobs-index/blob/master/LICENSE",
    },
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(Any, _rate_limit_exceeded_handler))  # type: ignore[arg-type]


origins = [
    "https://dallas-college-lmic.github.io",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=CorrelationIdMiddleware(app).dispatch)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on application startup"""
    import os

    # Only initialize database if not in testing mode
    if not os.getenv("TESTING"):
        db_config = DatabaseConfig.from_env()
        init_database(db_config)


@app.get("/occupation_ids", response_model=OccupationsResponse, tags=["Occupations"])
@limiter.limit("30/minute")
def get_occupation_ids(
    request: Request, session: Session = Depends(get_db_session)
) -> OccupationsResponse:
    """
    Get all occupation IDs and names from the database.

    Returns a comprehensive list of occupation codes with human-readable names
    for job market analysis and spatial data visualization.
    """
    try:
        service = OccupationService(session)
        occupations = service.get_occupations_with_names()
        occupation_items = [OccupationItem(**occ) for occ in occupations]
        return OccupationsResponse(occupations=occupation_items)
    except Exception as e:
        error_detail = {
            "message": f"Internal server error: {str(e)}",
            "error_code": "INTERNAL_SERVER_ERROR",
            "context": {},
        }
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/geojson")
@limiter.limit("10/minute")
def get_geojson(
    request: Request, session: Session = Depends(get_db_session)
) -> Response:
    try:
        service = SpatialService(session)
        features = service.get_geojson_features()

        geojson_collection = GeoJSONFeatureCollection(features=features)

        return Response(
            content=geojson_collection.model_dump_json(),
            media_type="application/geo+json",
            headers={"Content-Disposition": "inline"},
        )
    except Exception as e:
        error_detail = {
            "message": f"Internal server error: {str(e)}",
            "error_code": "INTERNAL_SERVER_ERROR",
            "context": {},
        }
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/occupation_data/{category}")
@limiter.limit("30/minute")
def get_occupation_spatial_data(
    category: str, request: Request, session: Session = Depends(get_db_session)
) -> Response:
    """Get spatial data for a specific occupation category"""
    try:
        service = OccupationService(session)
        features = service.get_occupation_spatial_data(category)

        if not features:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for occupation category: {category}",
            )

        geojson_collection = OccupationGeoJSONFeatureCollection(features=features)

        return Response(
            content=geojson_collection.model_dump_json(),
            media_type="application/geo+json",
            headers={"Content-Disposition": "inline"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/isochrones/{geoid}")
@limiter.limit("30/minute")
def get_isochrones(
    geoid: str, request: Request, session: Session = Depends(get_db_session)
) -> Response:
    """Get isochrone travel time bands for a specific census tract"""
    try:
        # Validate geoid format (should be numeric)
        if not geoid.isdigit():
            raise HTTPException(
                status_code=400, detail="Invalid geoid format. Must be numeric."
            )

        service = IsochroneService(session)
        features = service.get_isochrones_by_geoid(geoid)

        if not features:
            raise HTTPException(
                status_code=404, detail=f"No isochrone data found for geoid: {geoid}"
            )

        geojson_collection = IsochroneFeatureCollection(features=features)

        return Response(
            content=geojson_collection.model_dump_json(),
            media_type="application/geo+json",
            headers={"Content-Disposition": "inline"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/school_of_study_ids",
    response_model=SchoolOfStudyIdsResponse,
    tags=["School of Study"],
)
@limiter.limit("30/minute")
def get_school_of_study_ids(
    request: Request, session: Session = Depends(get_db_session)
) -> SchoolOfStudyIdsResponse:
    """
    Get all available school of study categories.

    Returns a comprehensive list of educational program categories mapped to job market data.
    Each category represents a major field of study with associated employment opportunities.

    ## School Categories
    * **BHGT**: Business, Hospitality, Governance & Tourism
    * **CAED**: Creative Arts, Entertainment & Design
    * **CE**: Construction & Engineering
    * **EDU**: Education
    * **ETMS**: Energy, Technology, Manufacturing & Science
    * **HS**: Health Services
    * **LPS**: Legal & Public Services
    * **MIT**: Management & Information Technology

    ## Response Format
    Returns a dictionary mapping category codes to human-readable names.
    """
    try:
        service = SchoolOfStudyService(session)
        school_ids = service.get_school_ids()
        return SchoolOfStudyIdsResponse(school_ids=school_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/school_of_study_data/{category}", tags=["School of Study"])
@limiter.limit("30/minute")
def get_school_of_study_spatial_data(
    category: str, request: Request, session: Session = Depends(get_db_session)
) -> Response:
    """
    Get spatial GeoJSON data for a specific school of study category.

    Returns employment and job opening data for geographic areas associated with
    the specified educational program category.

    ## Parameters
    * **category**: School of study category code (BHGT, CAED, CE, EDU, ETMS, HS, LPS, MIT)

    ## Response Data
    * **Z-scores**: Standardized metrics for openings_2024_zscore and jobs_2024_zscore
    * **Color coding**: Pre-calculated color values for data visualization
    * **GeoJSON format**: Ready for mapping libraries like Mapbox GL JS or Leaflet

    ## Example Categories
    * `BHGT` - Business, Hospitality, Governance & Tourism programs
    * `EDU` - Education and teaching programs
    * `HS` - Health Services and medical programs

    ## Error Handling
    Returns 404 if category is not found or has no associated spatial data.
    """
    try:
        service = SchoolOfStudyService(session)
        features = service.get_school_spatial_data(category)

        if not features:
            raise HTTPException(
                status_code=404, detail=f"No data found for school category: {category}"
            )

        geojson_collection = SchoolOfStudyGeoJSONFeatureCollection(features=features)

        return Response(
            content=geojson_collection.model_dump_json(),
            media_type="application/geo+json",
            headers={"Content-Disposition": "inline"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
