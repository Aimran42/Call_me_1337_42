import src

def main()-> int:
    try:
        lst = src.Parser.parsing()

        if not lst:
            return 1

        pl = src.Pipeline(lst[0], lst[1], lst[2])

        print("\n_____________________SUMMARY_____________________\n")
        print(f"Loaded {len(lst[0])} function definitions")
        print(f"Loaded {len(lst[1])} test prompts")
        pl.run()

        print(f"Wrote results to {lst[2]}")
    except KeyboardInterrupt:
        print(" Please don' t kill terminal")

    return 0

if __name__ == "__main__":
    main()
