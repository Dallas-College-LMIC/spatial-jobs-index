from fastapi import FastAPI, HTTPException, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import cast, Any
from .database import DatabaseConfig, init_database, get_db_session
from .models import OccupationIdsResponse, OccupationsResponse, OccupationItem, GeoJSONFeatureCollection, OccupationGeoJSONFeatureCollection
from .services import OccupationService, SpatialService

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
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


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    import os

    # Only initialize database if not in testing mode
    if not os.getenv("TESTING"):
        db_config = DatabaseConfig.from_env()
        init_database(db_config)


@app.get("/occupation_ids", response_model=OccupationsResponse)
@limiter.limit("30/minute")
def get_occupation_ids(request: Request, session: Session = Depends(get_db_session)):
    try:
        occupations = OccupationService.get_occupations_with_names(session)
        occupation_items = [OccupationItem(**occ) for occ in occupations]
        return OccupationsResponse(occupations=occupation_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/geojson")
@limiter.limit("10/minute")
def get_geojson(request: Request, session: Session = Depends(get_db_session)):
    try:
        features = SpatialService.get_geojson_features(session)

        geojson_collection = GeoJSONFeatureCollection(features=features)

        return Response(
            content=geojson_collection.model_dump_json(),
            media_type="application/geo+json",
            headers={"Content-Disposition": "inline"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/occupation_data/{category}")
@limiter.limit("30/minute")
def get_occupation_spatial_data(category: str, request: Request, session: Session = Depends(get_db_session)):
    """Get spatial data for a specific occupation category"""
    try:
        features = OccupationService.get_occupation_spatial_data(session, category)
        
        if not features:
            raise HTTPException(status_code=404, detail=f"No data found for occupation category: {category}")
        
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
