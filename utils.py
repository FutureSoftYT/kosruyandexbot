import asyncio
import os
import pathlib

import aiofiles
import aiohttp


async def download_video(url: str):
    file_path = pathlib.Path(__file__).parent
    fname = url.split("/")[-1].split("?")[0]

    if os.path.isfile(file_path / fname):
        return file_path / fname
    print('Downloading ....')
    sema = asyncio.BoundedSemaphore(5)

    async with sema, aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.read()

    async with aiofiles.open(
            os.path.join(file_path, fname), "wb"
    ) as outfile:
        await outfile.write(data)

    return file_path / fname
