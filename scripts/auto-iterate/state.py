import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class State:
    state_file: str = ""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())

    phase0_complete: bool = False

    phase1_converged: bool = False
    phase1_iterations: int = 0
    phase1_final_score: dict = field(default_factory=dict)

    phase2_converged: bool = False
    phase2_iterations: int = 0
    phase2_final_score: dict = field(default_factory=dict)

    converged_modules: list = field(default_factory=list)
    unconverged_modules: list = field(default_factory=list)
    completed_modules: list = field(default_factory=list)  # all evaluated (converged or not)
    current_module: str = ""
    current_iteration: int = 0

    history: dict = field(default_factory=dict)

    def add_history(self, key: str, entry: dict):
        """Add an entry to the history for a given key."""
        self.history.setdefault(key, []).append(entry)

    def best_score(self, key: str) -> float:
        """Get the best (maximum) score for a given key."""
        entries = self.history.get(key, [])
        if not entries:
            return 0.0
        return max(e.get("score", 0.0) for e in entries)

    def save(self):
        """Persist state to JSON file."""
        Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
        d = asdict(self)
        Path(self.state_file).write_text(
            json.dumps(d, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )


def load_or_init(state_file: str) -> State:
    """Load state from file, or initialize new State if file doesn't exist."""
    if not Path(state_file).exists():
        return State(state_file=state_file)
    data = json.loads(Path(state_file).read_text(encoding='utf-8'))
    data["state_file"] = state_file  # override in case path moved
    return State(**data)
