import json
from typing import Any, Dict, List, Optional

from llm_sdk import Small_LLM_Model


class ConstrainedDecoder:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        self.vocab = self.build_vocab_map()
        self.inverse_vocab = self.build_inverse_vocab(self.vocab)

    def build_vocab_map(self) -> Dict[str, int]:
        try:
            with open(self.model.get_path_to_vocab_file(), "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def build_inverse_vocab(self, vocab: Dict[str, int]) -> Dict[int, str]:
        return {v: k for k, v in vocab.items()}

    def is_structurally_valid(self, partial: str) -> bool:
        depth = 0
        in_string = False
        escape = False
        for ch in partial:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
                if depth < 0:
                    return False
        return True

    def is_schema_valid(self, partial: str, schema: Dict[str, str]) -> bool:
        depth = 0
        in_string = False
        escape = False
        for ch in partial:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
        completed = partial + "}" * max(depth, 0)
        try:
            parsed = json.loads(completed)
        except json.JSONDecodeError:
            return True
        if not isinstance(parsed, dict):
            return False
        return all(key in schema for key in parsed)

    def is_token_valid(self, partial: str, candidate: str, schema: Dict[str, str]) -> bool:
        text = partial + candidate
        return self.is_structurally_valid(text) and self.is_schema_valid(text, schema)

    def pick_next_token(self, input_ids: List[int], partial: str, schema: Dict[str, str]) -> Optional[int]:
        try:
            logits = self.model.get_logits_from_input_ids(input_ids)
        except Exception:
            return None
        best_id = None
        best_score = float("-inf")
        for token_id, token_str in self.inverse_vocab.items():
            if token_id >= len(logits) or logits[token_id] <= best_score:
                continue
            if self.is_token_valid(partial, token_str, schema):
                best_id = token_id
                best_score = logits[token_id]
        return best_id

    def generate(self, prompt: str, schema: Dict[str, str], max_steps: int = 200) -> Dict[str, Any]:
        partial = "{"
        try:
            input_ids = list(self.model.encode(prompt).tolist()[0])
        except Exception:
            return {}
        for _ in range(max_steps):
            next_id = self.pick_next_token(input_ids, partial, schema)
            if next_id is None:
                break
            token_str = self.inverse_vocab[next_id]
            partial += token_str
            input_ids.append(next_id)
            if partial.strip().endswith("}") and partial.count("{") <= partial.count("}"):
                break
        try:
            result = json.loads(partial)
        except json.JSONDecodeError:
            result = {}
        return result if isinstance(result, dict) else {}