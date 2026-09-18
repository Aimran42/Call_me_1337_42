from src.models import FunctionDefinition, TestPrompt
from pydantic import ValidationError
from typing import List, Any
from pathlib import Path

import argparse
import json


class ParsingErr(Exception):
    pass


class Parser:
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog="src",
            description="Run function-calling tests against function definitions.",
        )
        parser.add_argument(
            "--functions_definition",
            type=str,
            default="data/input/functions_definition.json",
            help="Path to the functions definition JSON file.",
        )
        parser.add_argument(
            "--input",
            type=str,
            default="data/input/function_calling_tests.json",
            help="Path to the function calling tests JSON file.",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="data/output/function_calls.json",
            help="Path to write the output JSON file.",
        )
        return parser.parse_args()


    @staticmethod
    def load_json_file(path: str) -> Any:
        try:
            file_path = Path(path)
            if not file_path.is_file():
                raise ParsingErr(f"File not found: {path}")
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ParsingErr(f"Invalid JSON in {path}: {e}") from e
        except OSError as e:
            raise ParsingErr(f"Could not read {path}: {e}") from e

    @staticmethod
    def parse_functions_definition(path: str) -> List[FunctionDefinition]:
        try:
            raw_data = Parser.load_json_file(path)
            if not isinstance(raw_data, list):
                raise ParsingErr(f"{path} must contain a JSON array")
            return [FunctionDefinition(**item) for item in raw_data]
        except ValidationError as err:
            raise ParsingErr(f"Invalid function definition in {path}: {err}") from err

    @staticmethod
    def parse_function_calling_tests(path: str) -> List[TestPrompt]:
        try:
            raw_data = Parser.load_json_file(path)
            if not isinstance(raw_data, list):
                raise ParsingErr(f"{path} must contain a JSON array")
            return [TestPrompt(**item) for item in raw_data]
        except ValidationError as e:
            raise ParsingErr(f"Invalid test prompt in {path}: {e}") from e


    def parsing() -> List:
        args = Parser.parse_args()

        try:
            functions = Parser.parse_functions_definition(args.functions_definition)
            tests = Parser.parse_function_calling_tests(args.input)
        except ParsingErr as e:
            print(f"Error: {e}")
            return []

        results = []
        for test in tests:
            results.append(test.model_dump())

        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        except OSError as e:
            print(f"Error in output file :\n{e}")
            return []

        return [functions, tests, output_path]