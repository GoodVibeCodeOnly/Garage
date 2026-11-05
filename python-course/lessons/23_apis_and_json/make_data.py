"""Write the bundled offline sample for lesson 23. Run: python make_data.py

Mimics the World Bank API response shape for
  https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.KD.ZG?format=json
Values are rounded approximations for teaching, not an authoritative copy.
Split into two "pages" so pagination can be practised offline.
"""
import json
import pathlib

out = pathlib.Path(__file__).parent / "data"
out.mkdir(exist_ok=True)

values = {2024: None, 2023: 2.9, 2022: 2.5, 2021: 6.1, 2020: -2.2, 2019: 2.3,
          2018: 2.9, 2017: 2.5, 2016: 1.8, 2015: 2.9, 2014: 2.5, 2013: 2.1}
records = [{
    "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth (annual %)"},
    "country": {"id": "US", "value": "United States"},
    "countryiso3code": "USA",
    "date": str(y), "value": v, "unit": "", "obs_status": "", "decimal": 1,
} for y, v in values.items()]

per_page = 6
pages = [records[i:i + per_page] for i in range(0, len(records), per_page)]
for i, chunk in enumerate(pages, start=1):
    meta = {"page": i, "pages": len(pages), "per_page": per_page, "total": len(records),
            "sourceid": "2", "lastupdated": "2025-07-01"}
    (out / f"wb_us_gdp_page{i}.json").write_text(json.dumps([meta, chunk], indent=1))
print("wrote", len(pages), "pages to", out)
