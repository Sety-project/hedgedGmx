#!/usr/bin/env python3
import asyncio
import datetime
import functools
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

safe_gather_limit = 40


def myUtcNow(return_type='float'):
    result = datetime.datetime.utcnow()
    if return_type == 'datetime':
        return result
    result = result.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
    if return_type == 'float':
        return result
    result = int(result)
    if return_type == 'int':
        return result
    raise Exception(f'invalid return_type {return_type}')


def async_wrap(f):
    '''
    creates a coroutine that name is run
    '''
    @functools.wraps(f)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        p = functools.partial(f, *args, **kwargs)
        return await loop.run_in_executor(executor, p)
    return run


async def semaphore_safe_gather(tasks, n=safe_gather_limit, semaphore=None, return_exceptions=False):
    semaphore = semaphore if semaphore else asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks), return_exceptions=return_exceptions)


def reform_dict(dictionary, t=tuple(), reform={}):
    for key, val in dictionary.items():
        t = t + (key,)
        if isinstance(val, dict):
            reform_dict(val, t, reform)
        else:
            reform.update({t: val})
        t = t[:-1]
    return reform
