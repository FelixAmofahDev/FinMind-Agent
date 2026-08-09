from app.graph.nodes.update_state import merge_entities


def test_entity_merge_replaces_existing_entity_instead_of_appending():
    existing = {
        "entities": {
            "profit": {
                "value": 4500,
                "currency": "GHS",
                "period": {"start": "2026-01-01", "end": "2026-03-31"},
            }
        }
    }
    incoming = {"entities": {"profit": {"value": 1200, "currency": "USD"}}}

    merged = merge_entities(existing, incoming)

    assert merged["entities"]["profit"]["value"] == 1200
    assert merged["entities"]["profit"]["currency"] == "USD"
    assert "period" not in merged["entities"]["profit"]
