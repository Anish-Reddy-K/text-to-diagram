import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import diagrammer

SNAP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
UPDATE = os.environ.get("UPDATE_SNAPSHOTS") == "1"

SPECS = {
    "box":      {"nodes": [{"id": "a", "type": "box", "label": "box"}]},
    "circle":   {"nodes": [{"id": "a", "type": "circle", "label": "c"}]},
    "text":     {"nodes": [{"id": "a", "type": "text", "label": "hello"}]},
    "database": {"nodes": [{"id": "a", "type": "database", "label": "db"}]},
    "stack":    {"nodes": [{"id": "a", "type": "stack", "label": "stk", "count": 3}]},
    "note":     {"nodes": [{"id": "a", "type": "note", "label": "note"}]},
    "group": {
        "nodes": [
            {"id": "a", "type": "box", "label": "a"},
            {"id": "b", "type": "box", "label": "b"},
            {"id": "g", "type": "group", "label": "g", "children": ["a", "b"]},
        ]
    },
    "custom": {
        "nodes": [{
            "id": "a", "type": "custom", "w": 60, "h": 60, "label": "x",
            "svg": "<rect width='60' height='60' fill='none' stroke='black' stroke-width='1.5'/>",
        }]
    },
}


def _path(name):
    return os.path.join(SNAP_DIR, f"{name}.svg")


def _make(name):
    def test(self):
        actual = diagrammer.render(SPECS[name])
        path = _path(name)
        if UPDATE or not os.path.exists(path):
            os.makedirs(SNAP_DIR, exist_ok=True)
            with open(path, "w") as f:
                f.write(actual)
            return
        with open(path) as f:
            expected = f.read()
        self.assertEqual(
            actual, expected,
            f"snapshot mismatch for {name!r}; rerun with UPDATE_SNAPSHOTS=1 to refresh",
        )
    test.__name__ = f"test_{name}"
    return test


class SnapshotTests(unittest.TestCase):
    pass


for _name in SPECS:
    setattr(SnapshotTests, f"test_{_name}", _make(_name))


if __name__ == "__main__":
    unittest.main()
