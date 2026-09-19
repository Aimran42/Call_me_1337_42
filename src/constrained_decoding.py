import json
from typing import Any, Dict, List

from llm_sdk.llm_sdk import Small_LLM_Model
from src.models import FunctionDefinition


class TokenTrie:
    """Prefix trie over a finite set of candidate strings.

    Parameters
    ----------
    words : list of str
        Candidate strings the trie should accept.
    """

    def __init__(self, words: List[str]) -> None:
        """Build the trie from words.

        Parameters
        ----------
        words : list of str
            Candidate strings the trie should accept.
        """
        self.root: Dict[str, Any] = {}
        for word in words:
            node = self.root
            for ch in word:
                node = node.setdefault(ch, {})
            node["$"] = True

    def is_prefix(self, text: str) -> bool:
        """Check whether ``text`` is a prefix of at least one candidate.

        Parameters
        ----------
        text : str
            Text to test.

        Returns
        -------
        bool
            True if ``text`` is a valid prefix, False otherwise.
        """
        node = self.root
        for ch in text:
            if ch not in node:
                return False
            node = node[ch]
        return True

    def is_complete(self, text: str) -> bool:
        """Check whether ``text`` exactly matches one of the candidates.

        Parameters
        ----------
        text : str
            Text to test.

        Returns
        -------
        bool
            True if ``text`` is a complete candidate, False otherwise.
        """
        node = self.root
        for ch in text:
            if ch not in node:
                return False
            node = node[ch]
        return "$" in node


class ConstrainedDecoder:
    """Decodes LLM logits with strict schema constraints.

    Parameters
    ----------
    model : Small_LLM_Model
        Model instance used to encode prompts and produce logits.
    """

    def __init__(self, model: Small_LLM_Model) -> None:
        """Initialize the decoder with a model instance and its vocab.

        Parameters
        ----------
        model : Small_LLM_Model
            Model instance used to encode prompts and produce logits.
        """
        self.model = model
        self.vocab = self._load_vocab()

    def _load_vocab(self) -> Dict[int, str]:
        """Load and invert the model's vocabulary file.

        Returns
        -------
        dict of int to str
            Mapping from token id to token string. Empty on failure.
        """
        try:
            with open(self.model.get_path_to_vocab_file(),
                      "r", encoding="utf-8") as f:
                vocab: Dict[str, int] = json.load(f)
            return {v: k for k, v in vocab.items()}
        except (OSError, json.JSONDecodeError):
            return {}

    def select_function(
        self, prompt: str, functions: List[FunctionDefinition]
    ) -> FunctionDefinition:
        """Select the function whose name best matches the prompt.

        Parameters
        ----------
        prompt : str
            Natural language prompt to select a function for.
        functions : list of FunctionDefinition
            Candidate functions to choose from.

        Returns
        -------
        FunctionDefinition
            The selected function definition.
        """
        if len(functions) == 1:
            return functions[0]
        trie = TokenTrie([fn.name for fn in functions])
        text = ""
        try:
            input_text = f"Prompt: {prompt}\nFunction name:"
            input_ids = list(
                self.model.encode(input_text).tolist()[0]
            )
        except Exception:
            return functions[0]
        for _ in range(32):
            try:
                logits = self.model.get_logits_from_input_ids(input_ids)
            except Exception:
                break
            ranked = sorted(
                range(len(logits)), key=lambda i: logits[i], reverse=True
            )
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
