import json
from typing import Dict, List

from llm_sdk.llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition


class TokenTrie:
    def __init__(self, words: List[str]) -> None:
        self.root: dict = {}
        for word in words:
            node = self.root
            for ch in word:
                node = node.setdefault(ch, {})
            node["$"] = True

    def is_prefix(self, text: str) -> bool:
        node = self.root
        for ch in text:
            if ch not in node:
                return False
            node = node[ch]
        return True

    def is_complete(self, text: str) -> bool:
        node = self.root
        for ch in text:
            if ch not in node:
                return False
            node = node[ch]
        return "$" in node


class ConstrainedDecoder:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        self.vocab = self._load_vocab()

    def _load_vocab(self) -> Dict[int, str]:
        try:
            with open(self.model.get_path_to_vocab_file(), "r", encoding="utf-8") as f:
                vocab: Dict[str, int] = json.load(f)
            return {v: k for k, v in vocab.items()}
        except (OSError, json.JSONDecodeError):
            return {}

    def select_function(self, prompt: str, functions: List[FunctionDefinition]) -> FunctionDefinition:
        if len(functions) == 1:
            return functions[0]
        trie = TokenTrie([fn.name for fn in functions])
        text = ""
        try:
            input_ids = list(self.model.encode(f"Prompt: {prompt}\nFunction name:").tolist()[0])
        except Exception:
            return functions[0]
        for _ in range(32):
            try:
                logits = self.model.get_logits_from_input_ids(input_ids)
            except Exception:
                break
            ranked = sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)
            next_id = None
            for token_id in ranked:
                token_str = self.vocab.get(token_id)
                if token_str is not None and trie.is_prefix(text + token_str):
                    next_id = token_id
                    break
            if next_id is None:
                break
            text += self.vocab[next_id]
            input_ids.append(next_id)
            if trie.is_complete(text):
                break
        return next((fn for fn in functions if fn.name == text), functions[0])
