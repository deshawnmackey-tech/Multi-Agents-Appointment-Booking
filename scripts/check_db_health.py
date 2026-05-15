#!/usr/bin/env python3
"""
Database health check script.

This script verifies database connectivity and displays connection pool status.
Useful for troubleshooting database connection issues and monitoring pool usage.

Usage:
    python scripts/check_db_health.py
    
Exit codes:
    0: Database connection successful
    1: Database connection failed
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.database.session import engine
from src.config import get_settings


def check_database_health() -> int:
    """
    Check database connection health and pool status.
    
    Returns:
        0 if successful, 1 if failed
    """
    settings = get_settings()
    
    print("=" * 60)
    print("DATABASE HEALTH CHECK")
    print("=" * 60)
    
    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            print("\n✓ Database connection successful")
            print(f"\nDatabase Information:")
            print(f"  URL: {settings.database_url_safe}")
            print(f"  Version: {version}")
            
            # Check pool status
            pool = engine.pool
            print(f"\nConnection Pool Status:")
            # Use getattr to safely access pool methods that may not be type-hinted
            print(f"  Pool size: {getattr(pool, 'size', lambda: 'N/A')()}")
            print(f"  Checked out: {getattr(pool, 'checkedout', lambda: 'N/A')()}")
            print(f"  Overflow: {getattr(pool, 'overflow', lambda: 'N/A')()}")
            print(f"  Max overflow: {settings.database_pool_max_overflow}")
            
            # Configuration details
            print(f"\nPool Configuration:")
            print(f"  Pool size: {settings.database_pool_size}")
            print(f"  Max overflow: {settings.database_pool_max_overflow}")
            print(f"  Timeout: {settings.database_pool_timeout}s")
            print(f"  Recycle: {settings.database_pool_recycle}s")
            print(f"  Pre-ping: Enabled")
            
            # Test a simple query
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                print("\n✓ Query execution successful")
            
            print("\n" + "=" * 60)
            print("HEALTH CHECK PASSED")
            print("=" * 60)
            return 0
            
    except Exception as e:
        print("\n✗ Database connection failed")
        print(f"\nError Details:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        print(f"\nConfiguration:")
        print(f"  URL: {settings.database_url_safe}")
        print("\n" + "=" * 60)
        print("HEALTH CHECK FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(check_database_health())

# Made with Bob
