"""
Logging utilities for the Trauma Desert project.

Provides consistent logging across all scripts with both console
and file output.
"""

import logging
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, Optional

from .paths import PATHS


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Get a configured logger for a script or module.
    
    Args:
        name: Name for the logger (typically __name__ or script name).
        level: Logging level. Default INFO.
        log_to_file: Whether to also write logs to file. Default True.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        log_dir = PATHS.logs
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dated log file
        log_file = log_dir / f"trauma_desert_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_step(step_name: str) -> Callable:
    """
    Decorator to log the start and completion of a processing step.
    
    Usage:
        @log_step("Clean shooting data")
        def clean_shootings():
            ...
    
    Args:
        step_name: Human-readable name for the step.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__ or "trauma_desert")
            logger.info(f"▶ Starting: {step_name}")
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"✓ Completed: {step_name} ({elapsed:.1f}s)")
                return result
            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.error(f"✗ Failed: {step_name} ({elapsed:.1f}s)")
                logger.error(f"  Error: {e}")
                raise
        
        return wrapper
    return decorator


class StepLogger:
    """
    Context manager for logging processing steps with timing.
    
    Usage:
        with StepLogger("Processing shootings", logger):
            process_data()
    """
    
    def __init__(
        self,
        step_name: str,
        logger: Optional[logging.Logger] = None,
    ):
        self.step_name = step_name
        self.logger = logger or get_logger("trauma_desert")
        self.start_time: Optional[datetime] = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"▶ Starting: {self.step_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if exc_type is None:
            self.logger.info(f"✓ Completed: {self.step_name} ({elapsed:.1f}s)")
        else:
            self.logger.error(f"✗ Failed: {self.step_name} ({elapsed:.1f}s)")
            self.logger.error(f"  Error: {exc_val}")
        return False  # Don't suppress exceptions


def log_dataframe_info(
    df,
    name: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Log summary information about a DataFrame.
    
    Args:
        df: pandas DataFrame or GeoDataFrame to summarize.
        name: Name to identify the DataFrame in logs.
        logger: Logger to use. Creates default if not provided.
    """
    if logger is None:
        logger = get_logger("trauma_desert")
    
    logger.info(f"  {name}: {len(df):,} rows, {len(df.columns)} columns")
    
    # Check for missing values
    missing = df.isnull().sum()
    cols_with_missing = missing[missing > 0]
    if len(cols_with_missing) > 0:
        logger.info(f"  {name} missing values: {dict(cols_with_missing)}")

