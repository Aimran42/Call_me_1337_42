from src.models import FunctionDefinition, TestPrompt, FunctionCallResult
from typing  import Any, Dict, List, Optional
from llm_sdk.llm_sdk import Small_LLM_Model
from pathlib import Path

import json


class Pipeline:
    def __init__(self,
                functions: List[FunctionDefinition], 
                tests: List[TestPrompt], 
                output_path: Path) -> None:

        self.functions = functions
        self.tests = tests
        self.output_path = output_path

    def load_model(self) -> Small_LLM_Model:
        return Small_LLM_Model()

    def build_vocab_map(self, model: Small_LLM_Model) -> Dict[str, int]:
        try:
            with open(model.get_path_to_vocab_file(), "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def build_inverse_vocab(self, vocab: Dict[str, int]) -> Dict[int, str]:
        return {v: k for k, v in vocab.items()}

    def build_schema(self, function: FunctionDefinition) -> Dict[str, str]:
        return {name: param.type for name, param in function.parameters.items()}

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

    def pick_next_token(
        self,
        model: Small_LLM_Model,
        input_ids: List[int],
        partial: str,
        schema: Dict[str, str],
        inverse_vocab: Dict[int, str],
    ) -> Optional[int]:
        try:
            logits = model.get_logits_from_input_ids(input_ids)
        except Exception:
            return None
        best_id = None
        best_score = float("-inf")
        for token_id, token_str in inverse_vocab.items():
            if token_id >= len(logits) or logits[token_id] <= best_score:
                continue
            if self.is_token_valid(partial, token_str, schema):
                best_id = token_id
                best_score = logits[token_id]
        return best_id

    def generate_constrained(
        self,
        model: Small_LLM_Model,
        prompt: str,
        schema: Dict[str, str],
        inverse_vocab: Dict[int, str],
        max_steps: int = 200,
    ) -> Dict[str, Any]:
        partial = "{"
        try:
            input_ids = list(model.encode(prompt).tolist()[0])
        except Exception:
            return {}
        for _ in range(max_steps):
            next_id = self.pick_next_token(model, input_ids, partial, schema, inverse_vocab)
            if next_id is None:
                break
            token_str = inverse_vocab[next_id]
            partial += token_str
            input_ids.append(next_id)
            if partial.strip().endswith("}") and partial.count("{") <= partial.count("}"):
                break
        try:
            result = json.loads(partial)
        except json.JSONDecodeError:
            result = {}
        return result if isinstance(result, dict) else {}

    def select_function(
        self,
        model: Small_LLM_Model,
        prompt: str,
        inverse_vocab: Dict[int, str],
    ) -> Optional[FunctionDefinition]:
        schema = {"name": "string"}
        generated = self.generate_constrained(model, prompt, schema, inverse_vocab)
        candidate_name = str(generated.get("name", ""))
        for function in self.functions:
            if function.name == candidate_name:
                return function
        for function in self.functions:
            if function.name in candidate_name or candidate_name in function.name:
                return function
        return self.functions[0] if self.functions else None

    def write_results(self, results: List[FunctionCallResult]) -> None:
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in results], f, indent=2)
        except OSError as e:
            print(f"Error in output file:\n{e}")

    def run(self) -> List[FunctionCallResult]:
        results: List[FunctionCallResult] = []
        try:
            model = self.load_model()
            vocab = self.build_vocab_map(model)
            inverse_vocab = self.build_inverse_vocab(vocab)
        except Exception:
            return results
        for test in self.tests:
            function = self.select_function(model, test.prompt, inverse_vocab)
            if function is None:
                continue
            schema = self.build_schema(function)
            parameters = self.generate_constrained(model, test.prompt, schema, inverse_vocab)
            results.append(FunctionCallResult(prompt=test.prompt, name=function.name, parameters=parameters))
        self.write_results(results)
        return results
