import sys


def greet(name: str) -> str:
    return f"Hello, {name}! Python {sys.version_info.major}.{sys.version_info.minor}"


if __name__ == "__main__":
    print(greet("Sudeepta"))
