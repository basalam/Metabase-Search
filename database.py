from brotli import decompress
from config import config


def add_filter(old_filter: str, filter_to_add: str, operator: str = "AND"):
    if old_filter.startswith("WHERE"):
        return f"{old_filter} {operator} {filter_to_add}"
    else:
        return f"WHERE {filter_to_add}"


def generate_query(
    q: str, limit: int, offset: int, archived: str, user_id: int, conditions: str
) -> str:
    return (
        decompress(config.db.search_query)
        .decode("utf-8")
        .replace("SEARCH_TERM", "'%" + q + "%'")
        .replace("QUERY_LIMIT", str(limit))
        .replace("QUERY_OFFSET", str(offset))
        .replace("SEARCH_ARCHIVED", archived)
        .replace("USER_ID", str(user_id))
        .replace("CONDITIONS", conditions)
    )
