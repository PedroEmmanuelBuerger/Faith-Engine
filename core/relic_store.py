"""
Meta-progressão persistente: Fragmentos de Relíquia (ganhos na morte) e bónus de run.
Ficheiro JSON ao lado do projeto: relic_meta.json
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.game_state import GameState
    from entities.player import Player

_PATH = Path(__file__).resolve().parent.parent / "relic_meta.json"


@dataclass
class RelicMeta:
    shards: int = 0
    starting_hp_ranks: int = 0  # cada rank: +4 HP máx. (máx. 6)
    starting_faith_ranks: int = 0  # cada rank: +14 Fé inicial (máx. 5)


def _default_dict() -> Dict[str, Any]:
    return asdict(RelicMeta())


def load_meta() -> RelicMeta:
    if not _PATH.is_file():
        return RelicMeta()
    try:
        raw = json.loads(_PATH.read_text(encoding="utf-8"))
        return RelicMeta(
            shards=int(raw.get("shards", 0)),
            starting_hp_ranks=int(raw.get("starting_hp_ranks", 0)),
            starting_faith_ranks=int(raw.get("starting_faith_ranks", 0)),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return RelicMeta()


def save_meta(meta: RelicMeta) -> None:
    try:
        _PATH.write_text(json.dumps(asdict(meta), indent=2), encoding="utf-8")
    except OSError:
        pass


def grant_shards_from_run(state: GameState) -> int:
    """Converte parte da Fé e progresso em fragmentos. Devolve quanto foi creditado."""
    meta = load_meta()
    gain = int(min(420, state.faith * 0.1 + state.wave * 4 + state.level * 3))
    gain = max(4, gain)
    meta.shards += gain
    save_meta(meta)
    return gain


def apply_starting_bonuses_to_player(player: Player, state: GameState) -> None:
    """Aumenta HP inicial e Fé base conforme ranks comprados."""
    meta = load_meta()
    hp_r = max(0, min(6, meta.starting_hp_ranks))
    fa_r = max(0, min(5, meta.starting_faith_ranks))
    player.max_hp += hp_r * 4
    player.hp = player.max_hp
    state.faith += fa_r * 14.0


def try_buy_hp_rank() -> tuple[bool, str]:
    meta = load_meta()
    if meta.starting_hp_ranks >= 6:
        return False, "HP inicial no máximo"
    cost = 32 + meta.starting_hp_ranks * 24
    if meta.shards < cost:
        return False, f"Faltam fragmentos (custo {cost})"
    meta.shards -= cost
    meta.starting_hp_ranks += 1
    save_meta(meta)
    return True, f"+4 HP máx. inicial (rank {meta.starting_hp_ranks})"


def try_buy_faith_rank() -> tuple[bool, str]:
    meta = load_meta()
    if meta.starting_faith_ranks >= 5:
        return False, "Fé inicial no máximo"
    cost = 28 + meta.starting_faith_ranks * 20
    if meta.shards < cost:
        return False, f"Faltam fragmentos (custo {cost})"
    meta.shards -= cost
    meta.starting_faith_ranks += 1
    save_meta(meta)
    return True, f"+14 Fé ao começar (rank {meta.starting_faith_ranks})"


def shard_count() -> int:
    return load_meta().shards
