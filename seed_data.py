from db import get_emerging_risks


def seed_demo_data() -> list[dict]:
    return get_emerging_risks()
