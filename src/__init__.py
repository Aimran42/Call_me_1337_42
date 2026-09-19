"""Package initializer of callmemaybe project.

Notes
-----
Re-exports the primary classes and exceptions from the ``models``,
``parsing``, ``constrained_decoding``, and ``pipeline`` submodules so
they can be imported directly from ``src``.
"""

from src.models import FunctionDefinition, FunctionParameter, TestPrompt
from src.constrained_decoding import ConstrainedDecoder, TokenTrie
from src.parsing import Parser, ParsingErr
from src.models import FunctionCallResult
from src.pipeline import Pipeline

__all__ = [
    "FunctionCallResult",
    "FunctionDefinition",
    "FunctionParameter",
    "TestPrompt",
    "ParsingErr",
    "Parser",
    "ConstrainedDecoder",
    "TokenTrie",
    "Pipeline",
]
