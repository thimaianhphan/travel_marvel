"""
Minimal sanity script exercising the alternatives workflow end-to-end.

Run with:

    python backend/tests/test_alternatives_workflow.py

The script prints the chosen alternative destinations and the scenic POIs that
the route discovery service finds on the way. It mirrors the prototype in
`alternative_poi/similarity.py` and `alternative_poi/poi_lookup.py`.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Ensure backend modules resolve when executed directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.alternatives_discovery import plan_alternative_routes  # noqa: E402

logging.basicConfig(level=logging.INFO)


def main() -> None:
    # Mannheim, Baden-Württemberg
    user_start = (49.4875, 8.4660)

    # Viral hotspot (outside the local area) – we look for closer alternatives
    target = {"name": "Neuschwanstein Castle", "hint": "castle"}

    regional_candidates = [
        {"name": "Heidelberg Castle", "hint": "castle"},
        {"name": "Hohenzollern Castle", "hint": "castle"},
        {"name": "Lichtenstein Castle", "hint": "castle"},
        {"name": "Blautopf", "hint": "lake"},
        {"name": "Triberg Waterfalls", "hint": "waterfall"},
        {"name": "Titisee", "hint": "lake"},
    ]

    results = plan_alternative_routes(
        user_start=user_start,
        target_poi=target,
        regional_candidates=regional_candidates,
        radius_km=200,
        topk_each=2,
        poi_discovery_kwargs={
            "search_radius_km": 40,
            "max_pois": 2,
            "prioritize_scenic": True,
        },
    )

    print(json.dumps(results, default=lambda o: o.__dict__, indent=2))


if __name__ == "__main__":
    main()

