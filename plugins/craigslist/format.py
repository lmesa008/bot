from datetime import timezone

import discord

from hyacinth.models import DiscordMessage, Listing


def format_listing(listing: Listing) -> DiscordMessage:
    match (listing.location.city, listing.location.state):
        case (None, None):
            location_part = ""
        case (city, None):
            location_part = f" - {city}"
        case (None, state):
            location_part = f" - {state}"
        case (city, state):
            location_part = f" - {city}, {state}"
    distance_part = ""
    if listing.distance_miles is not None:
        distance_part = f" ({int(listing.distance_miles)} mi."
    description = f"**${int(listing.price)}{location_part}{distance_part} away)**\n\n{listing.body}"

    embed = discord.Embed(
        title=listing.title,
        url=listing.url,
        description=description[:2048],
        timestamp=listing.updated_at.astimezone(timezone.utc),
    )
    if listing.image_urls:
        embed.set_image(url=listing.thumbnail_url)

    return DiscordMessage(embed=embed)
