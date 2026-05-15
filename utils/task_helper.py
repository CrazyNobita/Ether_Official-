# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/Ether_Update
#
#  License:       Open Source (Keep Credits)
# =============================================================================

import asyncio
from typing import Coroutine, Any, Optional
from utils.logger import get_logger

logger = get_logger("TaskHelper")

def safe_run(coro: Coroutine[Any, Any, Any], name: Optional[str] = None) -> asyncio.Task:
    """
    Safely run a coroutine as a background task with exception logging.
    
    Args:
        coro: The coroutine to run.
        name: An optional name for the task (used in logs).
        
    Returns:
        The created asyncio.Task instance.
    """
    task = asyncio.create_task(coro, name=name)
    
    def task_done_callback(t: asyncio.Task):
        try:
            # Check if task raised an exception
            exception = t.exception()
            if exception:
                task_name = name or t.get_name()
                logger.error(f"Task '{task_name}' failed with error: {exception}", exc_info=True)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in task callback: {e}")

    task.add_done_callback(task_done_callback)
    return task
