"""
Specifying max distance in Craigslist search was removed in favor of specifying using a notifier
filter.

This migration changes all craigslist search_specs to no longer include max distance/home lat+long.
"""

import json

from hyacinth.db.models import DbDiscordNotifier, DbListing
from hyacinth.db.session import Session


def update_notifiers() -> None:
    updated_search_count = 0
    with Session() as session:
        db_notifiers: list[DbDiscordNotifier] = session.query(DbDiscordNotifier).all()
        for db_notifier in db_notifiers:
            notifier_json = json.loads(db_notifier.config_json)  # type: ignore
            updated = False
            for search in notifier_json["active_searches"]:
                if search["spec"].get("source") != "craigslist":
                    continue

                params: dict = search["spec"]["search_params"]
                if "home_lat_long" in params or "max_distance_miles" in params:
                    params.pop("home_lat_long", "")
                    params.pop("max_distance_miles", "")
                    updated = True
                    updated_search_count += 1

            if updated:
                db_notifier.config_json = json.dumps(notifier_json)

        session.commit()

    print(f"Updated {updated_search_count} searches")


def update_listings() -> None:
    updated_listing_count = 0
    with Session() as session:
        db_listings: list[DbListing] = session.query(DbListing).all()
        for db_listing in db_listings:
            search_spec_json = json.loads(db_listing.search_spec_json)  # type: ignore
            if search_spec_json.get("source") != "craigslist":
                continue

            params: dict = search_spec_json["search_params"]
            if "home_lat_long" in params or "max_distance_miles" in params:
                params.pop("home_lat_long", "")
                params.pop("max_distance_miles", "")
                updated_listing_count += 1
                db_listing.search_spec_json = json.dumps(search_spec_json)

        session.commit()

    print(f"Updated {updated_listing_count} listings")


def main() -> None:
    update_notifiers()
    update_listings()


if __name__ == "__main__":
    main()
