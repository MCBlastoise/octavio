from contextlib import contextmanager
import sys
import os

# Suppress stderr temporarily
def suppress_import_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    original_stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(original_stderr_fd)
    os.dup2(devnull, original_stderr_fd)
    os.close(devnull)
    return saved_stderr_fd

def restore_import_stderr(saved_fd):
    os.dup2(saved_fd, sys.stderr.fileno())
    os.close(saved_fd)

@contextmanager
def no_stderr():
    saved = suppress_import_stderr()
    try:
        yield
    finally:
        restore_import_stderr(saved)
