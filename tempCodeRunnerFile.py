    money_bm = next((bm for bm in money["bookmakers"] if bm["key"] == "paddypower"), None)
        spread_bm = next((bm for bm in spreads["bookmakers"] if bm["key"] == "paddypower"), None)

        # skip if not found
        if not money_bm or not spread_bm:
            continue

        # make sure markets exist
        if not money_bm.get("markets") or not spread_bm.get("markets"):
            continue

        # pick first market (h2h or spreads)
        money_market = money_bm["markets"][0]
        spread_market = spread_bm["markets"][0]