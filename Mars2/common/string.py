MAX_INT_DOUBLE = 7


def to_ascii(input_: str) -> int:
    chars = 0
    result = 0

    for i in range(len(input_)):
        c = input_[i]

        if c == "\\":
            if i + 1 >= len(input_):
                raise ValueError("Escape character at end of string")

            c = input_[i + 1]

        chars += 1

        if chars > MAX_INT_DOUBLE:
            raise ValueError("String is too long to convert")

        if not c.isascii():
            raise ValueError("String contains non-ASCII characters")

        result <<= 8
        result |= ord(c)

    return result
