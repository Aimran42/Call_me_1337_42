Phase 2: Data Validation & Parsing[ ]
Create Pydantic models to parse and validate functions_definition.json.  [ ]
Create CLI argument parser supporting --functions_definition, --input, and --output.  [ ]
Implement robust file loader with exception handling for missing or malformed JSON files.  

Phase 3: Core Constrained Decoding Engine[ ]
Build vocabulary lookup map from llm_sdk's vocab file to map token IDs to string representations.  [ ]
Implement a Finite State Machine (FSM) or state tracking logic to determine valid JSON tokens at each generation step.  [ ]
Implement logit masking algorithm (setting invalid token logits to -inf) based on schema parameter types (string, number, boolean).  [ ]
Build the token generation loop consuming get_logits_from_input_ids().  

Phase 4: Output Processing & Formatting[ ]
Create Pipeline runner to iterate over each prompt in function_calling_tests.json.  [ ]
Format extracted outputs into strict JSON output array (prompt, name, parameters).  [ ]
Save results to target directory (data/output/function_calling_results.json).  

Phase 5: Quality, Documentation & Testing[ ]
Add NumPy-style docstrings and strict type annotations across all functions and classes.  [ ]
Pass flake8 linter without warnings.  [ ]
Pass mypy static type checker without errors.  [ ]
Create unit tests (pytest or unittest) covering edge cases (malformed inputs, empty strings, large numbers).  [ ]
Write README.md including the mandatory 42 curriculum header sentence, algorithm explanation, and performance analysis.  