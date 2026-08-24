import argparse

def parsing():
    print("I can do it !")    

def main():
    print("ようこそ 世界")
    parsing()

#example
# def parsing() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="LLM function calling via constrained decoding."
#     )
#     parser.add_argument(
#         "--functions_definition",
#         default=DEFAULT_FUNCTIONS_PATH,
#         help="Path to the functions_definition.json file.",
#     )
#     parser.add_argument(
#         "--input",
#         default=DEFAULT_INPUT_PATH,
#         help="Path to the function_calling_tests.json file.",
#     )
#     parser.add_argument(
#         "--output",
#         default=DEFAULT_OUTPUT_PATH,
#         help="Path for the output JSON file.",
#     )
#     return parser.parse_args()