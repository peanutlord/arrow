import os
import string
import token
import typing
from enum import Enum


class Tokens(Enum):
    STRING = "STRING"
    LEFT_ARROW = "LEFT_ARROW"
    RIGHT_ARROW = "RIGHT_ARROW"
    LITERAL = "LITERAL"
    NEWLINE = "NEWLINE"
    HASHTAG = "HASHTAG"
    # NOT_EQUALS = "NOT_EQUALS"
    # EXCLAIM = "EXCLAIM"
    # QUOTE = '"'
    EOF = "EOF"


class Scanner:

    def __init__(self, source: typing.IO):
        self._source = source

        # We need the size of the file, we assume we are at position 0
        self._source.seek(0, os.SEEK_END)
        self._source_size = self._source.tell()
        self._source.seek(0)

        self._current = -1  # We call advance in _scan_tokens, moving the initial -1 to 0 for reading from the file
        self._start = 0

        # Test
        self._function_pattern = "_" + string.ascii_letters

    def _is_eof(self) -> bool:
        """Returns if we are at the end of the file"""
        return self._current >= self._source_size

    def _advance(self) -> str:
        """Moves the scanner one token forward"""
        self._current += 1
        self._source.seek(self._current)
        return self._source.read(1)

    def _peek(self) -> str:
        self._source.seek(self._current + 1)
        char = self._source.read(1)
        self._source.seek(self._current)

        return char

    def _match(self, expected) -> bool:
        """Helps us identify two character tokens"""
        if self._is_eof():
            return False

        if self._peek() != expected:
            return False

        self._advance()  # ignore the character
        return True

    def _scan_string(self):
        s = ""

        # Drain the string
        while (char := self._advance()) != '"':
            s += char

        return s

    def _scan_token(self) -> typing.Tuple[Tokens, str]:
        char = self._advance()

        if char == " ":  # ignore all whitespace in code
            char = self._advance()  # TODO only ignores one whitespace

        if char in self._function_pattern:
            f = char
            while (char := self._advance()) in self._function_pattern:
                f += char

                # TODO why?
                if not char:
                    break

            return Tokens.LITERAL, f

        # Do we have a string?
        if char == '"':
            s = self._scan_string()
            return Tokens.STRING, s

        # Right arrow?
        if char == "-" and self._peek() == ">":
            self._advance()
            return Tokens.RIGHT_ARROW, "->"

        # Left arrow
        if char == "<" and self._peek() == "-":
            self._advance()
            return Tokens.LEFT_ARROW, "<-"

    def scan_tokens(self) -> list[typing.Tuple[Tokens, str]]:
        tokens = []
        while not self._is_eof():
            self._start = self._current
            tokens.append(self._scan_token())

        tokens.append((Tokens.EOF, ""))
        return tokens
