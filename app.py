#!/usr/bin/env python

import json
import os
import sys
import time
from math import ceil
from dotenv import load_dotenv

from trade_client import ClientConfig, SearchConfig, TradeClient

load_dotenv()

def main():
    poesessid = os.getenv("POESESSID", "")
    if not poesessid:
        print("Please set POESESSID in your environment before running.")
        sys.exit(1)

    # Configure the client
    conf = ClientConfig("Standard", poesessid)
    client = TradeClient(conf)

    # Example search config: searching for "Tabula Rasa" "Simple Robe"
    search_cfg = SearchConfig(item_name="Obern's Bastion", item_type="Stacked Sabatons")

    # Perform the initial search
    search_res = client.search(search_cfg)
    if not search_res or "result" not in search_res or not search_res["result"]:
        print("No items found for the given search.")
        return


    # Check if 'id' is in search_res
    print(search_res)
    if 'id' not in search_res:
        print("No 'id' found in response. This looks like a fetch response rather than a search response.")
        # Handle the fetch response format here
        all_items = search_res.get("result", [])
        total = len(all_items)
        print(f"Found {total} items.")
        # Process all_items directly if this is what you intend to do
        return
    else:
        # This is a proper search response
        query_id = search_res["id"]
        all_result_ids = search_res["result"]
        total = len(all_result_ids)
        print(f"Found {total} items. Fetching them all...")
        # Proceed with fetching items by query_id


    # The API only returns up to 10 items per fetch request
    page_size = 10
    page_count = ceil(total / page_size)

    all_items = []
    for page_idx in range(page_count):
        # Get a slice of up to 10 IDs
        chunk = all_result_ids[page_idx*page_size : (page_idx+1)*page_size]
        if not chunk:
            break

        fetch_res = client._fetch(client._build_fetch_url(chunk), query_id)
        if "result" in fetch_res:
            all_items.extend(fetch_res["result"])
        else:
            print("No 'result' field in fetch response, stopping.")
            break

        # A brief delay to avoid potential rate limiting (optional)
        time.sleep(0.2)

    # Write all items to a JSON file
    with open("all_items.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"Fetched and saved {len(all_items)} items to all_items.json")

if __name__ == "__main__":
    sys.exit(main())
