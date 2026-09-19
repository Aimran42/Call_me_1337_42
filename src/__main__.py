"""Entry point of callmemaybe project aka src package.

Notes
-----
Parses the input files, runs the function-calling pipeline, and
writes the results to the configured output path.
"""

import src


def main() -> int:
    try:
        lst = src.Parser().parsing()
        if not lst:
            return 1

        functions, tests, output_path = lst
        pl = src.Pipeline(functions, tests, output_path)

        print("\n_____________________SUMMARY_____________________\n")
        print(f"Loaded {len(functions)} function definitions")
        print(f"Loaded {len(tests)} test prompts")

        results = pl.run()
        if not results:
            print("Error: no results were generated")
            return 1

        print(f"Wrote {len(results)} results to {output_path}")
    except KeyboardInterrupt:
        print("\nInterrupted, exiting.")

    return 0


if __name__ == "__main__":
    main()
