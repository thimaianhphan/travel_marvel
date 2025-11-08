from poi_lookup import resolve_one, batch_resolve

if __name__ == "__main__":
    import json
    demo = [
        {"name": "Königssee", "hint": "lake"},
        {"name": "Kvernufoss", "hint": "waterfall"},
        {"name": "Chiemsee", "hint": "lake"},
    ]
    print(json.dumps(batch_resolve(demo), indent=2, ensure_ascii=False))
