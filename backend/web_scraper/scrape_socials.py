from __future__ import annotations
from models.user import User
from typing import Optional

def scrapeSocials(urls: list[str], userId: str) -> Optional[dict[str, str]]:
	"""If the user's socials are already filled in DB, return them; otherwise continue later.

	Args:
		urls: A list of URL strings to process (not used when returning cached socials).
		userId: The user's document ID in the database.

	Returns:
		A dict with keys githubUrl, linkedInUrl, leetcodeUrl, xUrl if all are present; otherwise None.
	"""
	# Lookup user by id. MongoEngine will coerce a hex string to ObjectId.
	user = User.objects(id=userId).first()
	if not user or not getattr(user, "socials", None):
		return None

	socials = user.socials

	values = {
		"githubUrl": (socials.githubUrl or "").strip(),
		"linkedInUrl": (socials.linkedInUrl or "").strip(),
		"leetcodeUrl": (socials.leetcodeUrl or "").strip(),
		"xUrl": (socials.xUrl or "").strip(),
	}

	# If all fields are non-empty, return them as-is.
	if all(values.values()):
		return values

	# Otherwise, not all socials are filled; return None for now. Scraping to be implemented later.
	return None

