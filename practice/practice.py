import json
from typing import Dict
from pydantic import BaseModel

class function_def(BaseModel):
    prompt: str


class function_test(BaseModel):
    type: str

class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, function_test]
    returns: function_test


def main():
    with open("file1.json", "r") as f2:
        raw_data2 = json.load(f2)
    with open("file2.json", "r") as f1:
        raw_data = json.load(f1)


    out1 = [function_def(**item) for item in raw_data]

    out2 = [FunctionDefinition(**item) for item in raw_data2]

    for i in out1:
        print(f"{i}\n")

    for i in out2:
        print(f"{i}\n")

if __name__ == "__main__":
    main()
