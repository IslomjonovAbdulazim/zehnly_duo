from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..services.analytics_service import AnalyticsService
from ..services.cache import cache
from ..models.analytics import AnalyticsResponse
import logging

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

# Cache key for analytics data
ANALYTICS_CACHE_KEY = "analytics:full_report"
CACHE_TTL = 6 * 60 * 60  # 6 hours in seconds


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    background_tasks: BackgroundTasks,
    force_refresh: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics data with 6-hour caching
    
    - **force_refresh**: Force regeneration of analytics (admin use)
    - Returns cached data if available, otherwise generates fresh data
    - Automatically refreshes cache in background when near expiry
    """
    try:
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = cache.get(ANALYTICS_CACHE_KEY)
            if cached_data:
                logger.info("Analytics served from cache")
                
                # Update cache info for response
                cached_data["cache_info"] = {
                    "is_cached": True,
                    "cache_hit": True,
                    "generation_time_ms": 0,
                    "data_freshness": "6_hours"
                }
                
                # Check if we need background refresh (5 hours after generation)
                generated_at = datetime.fromisoformat(cached_data["generated_at"].replace("Z", "+00:00"))
                if datetime.now() - generated_at > timedelta(hours=5):
                    background_tasks.add_task(refresh_analytics_cache, db)
                    logger.info("Scheduled background cache refresh")
                
                return AnalyticsResponse(**cached_data)
        
        # Generate fresh analytics data
        logger.info("Generating fresh analytics data")
        analytics_service = AnalyticsService(db)
        analytics_data = analytics_service.generate_analytics_data()
        
        # Cache the data for 6 hours
        cache_success = cache.set(ANALYTICS_CACHE_KEY, analytics_data, CACHE_TTL)
        
        if cache_success:
            logger.info("Analytics data cached successfully")
            analytics_data["cache_info"]["is_cached"] = True
        else:
            logger.warning("Failed to cache analytics data")
            analytics_data["cache_info"]["is_cached"] = False
        
        return AnalyticsResponse(**analytics_data)
        
    except Exception as e:
        logger.error(f"Analytics generation error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate analytics: {str(e)}"
        )


@router.post("/refresh")
async def refresh_analytics(db: Session = Depends(get_db)):
    """
    Force refresh analytics cache (admin endpoint)
    
    - Clears existing cache
    - Generates fresh analytics data
    - Updates cache with new data
    """
    try:
        # Clear existing cache
        cache.delete(ANALYTICS_CACHE_KEY)
        logger.info("Analytics cache cleared")
        
        # Generate fresh data
        analytics_service = AnalyticsService(db)
        analytics_data = analytics_service.generate_analytics_data()
        
        # Cache the new data
        cache_success = cache.set(ANALYTICS_CACHE_KEY, analytics_data, CACHE_TTL)
        
        return {
            "message": "Analytics cache refreshed successfully",
            "cached": cache_success,
            "generated_at": analytics_data["generated_at"],
            "expires_at": analytics_data["cache_expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Analytics refresh error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to refresh analytics: {str(e)}"
        )


@router.get("/cache/status")
async def get_cache_status():
    """
    Get analytics cache status
    
    - Shows if cache exists
    - Cache expiry information
    - Data freshness status
    """
    try:
        cached_data = cache.get(ANALYTICS_CACHE_KEY)
        
        if cached_data:
            generated_at = datetime.fromisoformat(cached_data["generated_at"].replace("Z", "+00:00"))
            expires_at = datetime.fromisoformat(cached_data["cache_expires_at"].replace("Z", "+00:00"))
            now = datetime.now()
            
            time_until_expiry = expires_at - now
            age = now - generated_at
            
            return {
                "cache_exists": True,
                "generated_at": generated_at,
                "expires_at": expires_at,
                "age_minutes": int(age.total_seconds() / 60),
                "expires_in_minutes": int(time_until_expiry.total_seconds() / 60) if time_until_expiry.total_seconds() > 0 else 0,
                "is_expired": time_until_expiry.total_seconds() <= 0,
                "needs_refresh": age > timedelta(hours=5)
            }
        else:
            return {
                "cache_exists": False,
                "message": "No cached analytics data found"
            }
            
    except Exception as e:
        logger.error(f"Cache status check error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to check cache status: {str(e)}"
        )


async def refresh_analytics_cache(db: Session):
    """
    Background task to refresh analytics cache
    Used for proactive cache warming
    """
    try:
        logger.info("Starting background analytics cache refresh")
        
        analytics_service = AnalyticsService(db)
        analytics_data = analytics_service.generate_analytics_data()
        
        cache_success = cache.set(ANALYTICS_CACHE_KEY, analytics_data, CACHE_TTL)
        
        if cache_success:
            logger.info("Background analytics cache refresh completed successfully")
        else:
            logger.warning("Background analytics cache refresh failed")
            
    except Exception as e:
        logger.error(f"Background analytics refresh error: {str(e)}")


@router.delete("/cache")
async def clear_analytics_cache():
    """
    Clear analytics cache (admin endpoint)
    
    - Removes cached analytics data
    - Next request will generate fresh data
    """
    try:
        cache.delete(ANALYTICS_CACHE_KEY)
        return {"message": "Analytics cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to clear cache: {str(e)}"
        )