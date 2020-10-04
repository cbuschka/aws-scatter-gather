import asyncio
import logging
import sys

from aws_xray_sdk.core.context import Context
from aws_xray_sdk.core.recorder import Subsegment

log = logging.getLogger(__name__)


def _get_current_task(loop):
    _GTE_PY37 = sys.version_info.major >= 3 and sys.version_info.minor >= 7
    if _GTE_PY37:
        return asyncio.current_task(loop=loop)
    else:
        return asyncio.Task.current_task(loop=loop)


class AsyncContext(Context):
    """
    Async Context for storing segments.

    Inherits nearly everything from the main Context class.
    Replaces threading.local with a task based local storage class,
    Also overrides clear_trace_entities
    """

    def __init__(self, *args, loop=None, use_task_factory=True, **kwargs):
        super(AsyncContext, self).__init__(*args, **kwargs)

        self._loop = loop
        if loop is None:
            self._loop = asyncio.get_event_loop()

        if use_task_factory:
            orig_task_factory = self._loop.get_task_factory()
            self._loop.set_task_factory(TaskFactory(context=self, orig_task_factory=orig_task_factory))
        else:
            raise ValueError("use_task_factory must be true")

        self._local = TaskLocalStorage(loop=loop)

    def clear_trace_entities(self):
        """
        Clear all trace_entities stored in the task local context.
        """
        if self._local is not None:
            self._local.clear()


class TaskLocalStorage(object):
    """
    Simple task local storage
    """

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

    def __setattr__(self, name, value):
        if name in ('_loop',):
            # Set normal attributes
            object.__setattr__(self, name, value)

        else:
            # Set task local attributes
            task = _get_current_task(loop=self._loop)
            if task is None:
                return None

            if not hasattr(task, 'context'):
                task.context = {}

            task.context[name] = value

    def __getattribute__(self, item):
        if item in ('_loop', 'clear'):
            # Return references to local objects
            return object.__getattribute__(self, item)

        task = _get_current_task(loop=self._loop)
        if task is None:
            return None

        if hasattr(task, 'context') and item in task.context:
            return task.context[item]

        raise AttributeError('Task context does not have attribute {0}'.format(item))

    def clear(self):
        # If were in a task, clear the context dictionary
        task = _get_current_task(loop=self._loop)
        if task is not None and hasattr(task, 'context'):
            task.context.clear()


class TaskFactory(object):
    """
    Task factory function

    Fuction closely mirrors the logic inside of
    asyncio.BaseEventLoop.create_task. Then if there is a current
    task and the current task has a context then share that context
    with the new task
    """

    def __init__(self, context, orig_task_factory):
        self.context = context
        self.orig_task_factory = orig_task_factory

    def __call__(self, loop, coro, *args, **kwargs):
        traced_func = XRayTracedFunc(coro, self.context, loop=loop)

        if self.orig_task_factory:
            task = self.orig_task_factory(loop, traced_func, *args, **kwargs)
        else:
            task = asyncio.tasks.Task(traced_func, *args, loop=loop, **kwargs)

        trace_entity = self.context.get_trace_entity()
        if trace_entity:
            new_context = {"entities": [trace_entity]}
            setattr(task, 'context', new_context)

        return task


class XRayTracedFunc(object):
    def __init__(self, coro, context, loop):
        self.coro = coro
        self.context = context
        self.loop = loop

    async def __call__(self, *args, **kwargs):
        subsegment = self._open_subsegment()
        try:
            result = await self.coro
            return result
        finally:
            if subsegment is not None:
                self._close_subsegment()

    def _open_subsegment(self):
        segment = self._get_segment()
        if not segment:
            return None

        subsegment = Subsegment(self.coro.__name__, "local", segment)
        self.context.put_subsegment(subsegment)
        return subsegment

    def _close_subsegment(self):
        self.context.end_subsegment()

    def _get_segment(self):
        trace_entity = self.context.get_trace_entity()
        if not trace_entity:
            return None

        if self.context._is_subsegment(trace_entity):
            return trace_entity.parent_segment

        return trace_entity
