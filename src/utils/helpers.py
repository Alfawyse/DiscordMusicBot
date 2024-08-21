import asyncio

def safe_call(coro, loop):
    """
    Safely executes an asynchronous coroutine, catching exceptions.

    Args:
        coro (coroutine): The coroutine to be executed.
        loop (asyncio.AbstractEventLoop): The event loop to run the coroutine in.
    """
    try:
        asyncio.run_coroutine_threadsafe(coro, loop)
    except Exception as e:
        print(f"Error in safe_call: {e}")

def format_duration(seconds):
    """
    Converts seconds into a formatted duration string.

    Args:
        seconds (int): The number of seconds to be converted.

    Returns:
        str: The formatted duration string in "HH:MM:SS" format.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"
