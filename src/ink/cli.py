import sys
from .lexer import LexerError
from .parser import parse_program, ParseError
from .interpreter import eval_program

def main():
    if len(sys.argv) != 2:
        print("Usage: ink <file.ink>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    try:
        ast = parse_program(source)
        eval_program(ast)
    except LexerError as e:
        print(f"Lexer error: {e}")
        sys.exit(1)
    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
