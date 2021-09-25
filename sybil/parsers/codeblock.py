import re
import textwrap

from sybil import Region

CODEBLOCK_START = re.compile(
    r'^(?P<indent>[ \t]*)\.\.\s*(invisible-)?code(-block)?::?\s*(?P<language>[\w-]+)\b'
    r'(?:\s*\:[\w-]+\:.*\n)*'
    r'(?:\s*\n)*',
    re.MULTILINE)


def compile_codeblock(source, path):
    return compile(source, path, 'exec', dont_inherit=True)


def evaluate_code_block(example):
    code = compile_codeblock(example.parsed, example.document.path)
    exec(code, example.namespace)
    # exec adds __builtins__, we don't want it:
    del example.namespace['__builtins__']


class CodeBlockParser(object):
    """
    A class to instantiate and include when your documentation makes use of
    :ref:`codeblock-parser` examples.
     
    :param future_imports: 
        An optional list of strings that will be turned into
        ``from __future__ import ...`` statements and prepended to the code
        in each of the examples found by this parser.
    """

    _LANGUAGES = {
        'python': evaluate_code_block,
    }

    @classmethod
    def add_evaluator(cls, language, eval_function):
        """
        Adds (or overwrites) an evaluator function for the language.
        """
        cls._LANGUAGES[language] = eval_function

    def __init__(self, future_imports=()):
        self.future_imports = future_imports

    def __call__(self, document):
        for start_match in re.finditer(CODEBLOCK_START, document.text):
            language = start_match.group('language')
            try:
                evaluator_function = self._LANGUAGES[language]
            except KeyError:
                continue

            source_start = start_match.end()
            indent = str(len(start_match.group('indent')))
            end_pattern = re.compile(r'(\n\Z|\n[ \t]{0,'+indent+'}(?=\\S))')
            end_match = end_pattern.search(document.text, source_start)
            source_end = end_match.start()
            source = textwrap.dedent(document.text[source_start:source_end])
            # There must be a nicer way to get code.co_firstlineno
            # to be correct...
            line_count = document.text.count('\n', 0, source_start)
            if language == 'python' and self.future_imports:
                line_count -= 1
                source = 'from __future__ import {}\n{}'.format(
                    ', '.join(self.future_imports), source
                )
            line_prefix = '\n' * line_count
            source = line_prefix + source
            yield Region(
                start_match.start(),
                source_end,
                source,
                evaluator_function,
            )
