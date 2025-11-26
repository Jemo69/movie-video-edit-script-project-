"""Unit tests for logger module."""
import pytest
from pathlib import Path
from logger import get_logger
import logging
import os

def test_get_logger_creates_log_directory(temp_dir):
    """Test that get_logger creates log directory."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        logger = get_logger('test_logger')

        assert (temp_dir / 'log').exists()
        assert isinstance(logger, logging.Logger)
    finally:
        os.chdir(original_cwd)

def test_get_logger_adds_handlers(temp_dir):
    """Test that get_logger adds appropriate handlers."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        # We need to use a unique name for each test to ensure handlers are re-added
        logger = get_logger('test_logger_2')

        # In the new logger implementation, handlers are not re-added if they exist.
        # To test this, we need to reset the logger's handlers.
        logger.handlers = []
        logger = get_logger('test_logger_2_reconfig')

        # Should have 2 handlers: console and file
        assert len(logger.handlers) >= 2

        handler_types = [type(h).__name__ for h in logger.handlers]
        assert 'StreamHandler' in handler_types
        assert 'FileHandler' in handler_types
    finally:
        os.chdir(original_cwd)
        # Clean up logger instance to avoid state leakage between tests
        logging.getLogger('test_logger_2').handlers = []
        logging.getLogger('test_logger_2_reconfig').handlers = []


def test_get_logger_prevents_duplicate_handlers(temp_dir):
    """Test that calling get_logger twice doesn't duplicate handlers."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        logger1 = get_logger('test_logger_3')
        initial_handler_count = len(logger1.handlers)

        logger2 = get_logger('test_logger_3')

        assert logger1 is logger2
        assert len(logger2.handlers) == initial_handler_count
    finally:
        os.chdir(original_cwd)
        logging.getLogger('test_logger_3').handlers = []