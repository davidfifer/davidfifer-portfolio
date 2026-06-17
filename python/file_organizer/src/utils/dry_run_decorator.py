import logging
import functools

logger = logging.getLogger(__name__)

def dry_run(action_desc=None, dry_run=False):
    """
    Decorator that adds optional dry‑run behavior to a function, allowing callers
    to simulate execution without performing the underlying action.

    When `dry_run` is True, the wrapped function is not executed. Instead, a
    log entry is emitted describing the intended action along with the provided
    arguments. When `dry_run` is False, the function executes normally with
    execution and error logs recorded.

    Parameters:
        action_desc (str, optional):
            Human‑readable description of the action being performed. If omitted,
            the wrapped function's name is used.
        dry_run (bool, optional):
            If True, the function call is simulated and not executed. Defaults to False.

    Returns:
        callable:
            A decorated function that either executes normally or performs a
            simulated dry‑run depending on the `dry_run` flag.

    Logging Behavior:
        - Logs a `[DRY-RUN]` message when simulating execution.
        - Logs an `[EXECUTING]` message before running the wrapped function.
        - Logs an `[ERROR]` message if the wrapped function raises an exception.

    Notes:
        - In dry‑run mode, the wrapped function is never invoked and `None` is returned.
        - On execution failure, the exception is logged and `None` is returned.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            desc = action_desc or func.__name__
            if dry_run:
                logger.info(f"[DRY-RUN] Would perform: {desc} with args={args}, kwargs={kwargs}")
                return None  # Simulate no result
            else:
                logger.info(f"[EXECUTING] {desc}")
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[ERROR] Failed to execute '{desc}': {e}")
                    return None
        return wrapper
    return decorator
