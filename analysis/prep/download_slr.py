import asyncio
from pathlib import Path

import httpx

from analysis.constants import SE_STATES


# Data URLS are obtained by opening the Javascript console for
# https://coast.noaa.gov/slrdata/, then running

# [...document.querySelectorAll('li[ng-show="slr.slrurl"] a')].map(n => n.href)

URLS = [
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/AL/AL_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/AmericanSamoa_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/CNMI_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/CA/CA_EKA_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/CA/CA_LOX_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/CA/CA_MTR_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/CA/CA_SGX_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/CA/CA_ChannelIslands_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/CT_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/DE/DE_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/DC/DC_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_Pan_West_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_Pan_East_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_TLH3_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_JAX_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_MFL_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_MLB_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/FL/FL_TBW_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/GA/GA_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/Guam_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Hawaii_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Kauai_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Lanai_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Maui_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Molokai_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/Pacific/HI_Oahu_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_LP_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_Delta_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_Central_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_CentralEast_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_CentralNorth_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/LA/LA_West_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/ME_East_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/ME_West_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MD/MD_Southeast_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MD/MD_East_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MD/MD_North_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MD/MD_West_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MD/MD_Southwest_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/MA_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/MS/MS_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/NH_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NJ/NJ_Northern_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NJ/NJ_Middle_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NJ/NJ_Southern_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NY/NY_Hudson_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NY/NY_Metro_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NY/NY_Suffolk_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NC/NC_Northern_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NC/NC_Middle1_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NC/NC_Middle2_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NC/NC_Southern1_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NC/NC_Southern2_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/OR/OR_MFR_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/OR/OR_PQR_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/PA/PA_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/PR_USVI/PR_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/NewEngland/RI_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/SC/SC_North_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/SC/SC_Central_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/SC/SC_South_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_North1_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_North2_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_Central_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_South1_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/TX/TX_South2_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/PR_USVI/USVI_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/VA/VA_EasternShore_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/VA/VA_Northern_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/VA/VA_Middle_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/VA/VA_Southern_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/WA/WA_PQR_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/WA/WA_SEW_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/WA/WA_PugetNW_slr_data_dist.zip",
    "https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/WA/WA_PugetSW_slr_data_dist.zip",
]


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
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=60.0), http2=True
    ) as client:
        tasks = [
            asyncio.ensure_future(download_state_chunk(client, url, out_dir))
            for url in urls
        ]
        completed = await asyncio.gather(*tasks)


out_dir = Path("source_data/slr")
out_dir.mkdir(parents=True, exist_ok=True)

# filter to Southeast states
se_urls = [url for url in URLS if url.rsplit("/", 1)[1].split("_")[0] in SE_STATES]
asyncio.run(download(se_urls, out_dir))

print("All done!")
