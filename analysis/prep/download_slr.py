import asyncio
from pathlib import Path

import httpx


async def get_state_download_urls(client, state):
    url = f"https://coast.noaa.gov/slrdata/Sea_Level_Rise_Vectors/{state}/URLlist_{state}.txt"
    r = await client.get(url)
    r.raise_for_status()

    # drop the half-foot urls
    return [url for url in r.text.strip().split("\n") if not "halffoot" in url.lower()]


async def get_download_urls(states):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        tasks = [asyncio.ensure_future(get_state_download_urls(client, state)) for state in states]
        results = await asyncio.gather(*tasks)
        urls = []
        for result in results:
            urls.extend(result)

        return urls


async def download_state_chunk(client, url, out_dir):
    zipfile = url.rsplit("/", 1)[1]
    filename = out_dir / zipfile

    if filename.exists():
        print(f"Not downloading {zipfile} (exists locally)")
        return

    print(f"Downloading {zipfile}")
    r = await client.get(url)
    r.raise_for_status()

    with open(filename, "wb") as out:
        out.write(r.content)

    print(f"Downloaded {url} ({filename.stat().st_size >> 20} MB)")


async def download(urls, out_dir):
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=60.0), http2=True) as client:
        tasks = [asyncio.ensure_future(download_state_chunk(client, url, out_dir)) for url in urls]
        await asyncio.gather(*tasks)


out_dir = Path("source_data/slr")
out_dir.mkdir(parents=True, exist_ok=True)

coastal_states = ["AL", "FL", "GA", "LA", "MS", "NC", "SC", "TX", "PR", "VA", "VI"]
urls = asyncio.run(get_download_urls(coastal_states))
asyncio.run(download(urls, out_dir))

print("All done!")
