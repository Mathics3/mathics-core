"""
This code is the LaTeX-specific part of the homegrown sphinx documentation.
FIXME: Ditch this and hook into sphinx.
"""

import re
from os import getenv

from mathics import settings
from mathics.core.evaluation import Message, Print
from mathics.doc.common_doc import (
    CONSOLE_RE,
    DL_ITEM_RE,
    DL_RE,
    END_LINE_SENTINAL,
    HYPERTEXT_RE,
    IMG_PNG_RE,
    IMG_RE,
    LATEX_RE,
    LIST_ITEM_RE,
    LIST_RE,
    MATHICS_RE,
    PYTHON_RE,
    QUOTATIONS_RE,
    REF_RE,
    SPECIAL_COMMANDS,
    SUBSECTION_END_RE,
    SUBSECTION_RE,
    TESTCASE_OUT_RE,
    DocChapter,
    DocPart,
    DocSection,
    DocTest,
    DocTests,
    DocText,
    Documentation,
    XMLDoc,
    _replace_all,
    gather_tests,
    get_results_by_test,
    post_sub,
    pre_sub,
    sorted_chapters,
)
from mathics.doc.utils import slugify

# We keep track of the number of \begin{asy}'s we see so that
# we can assocation asymptote file numbers with where they are
# in the document
next_asy_number = 1

ITALIC_RE = re.compile(r"(?s)<(?P<tag>i)>(?P<content>.*?)</(?P=tag)>")

LATEX_ARRAY_RE = re.compile(
    r"(?s)\\begin\{testresult\}\\begin\{array\}\{l\}(.*?)"
    r"\\end\{array\}\\end\{testresult\}"
)
LATEX_CHAR_RE = re.compile(r"(?<!\\)(\^)")
LATEX_CONSOLE_RE = re.compile(r"\\console\{(.*?)\}")
LATEX_INLINE_END_RE = re.compile(r"(?s)(?P<all>\\lstinline'[^']*?'\}?[.,;:])")

LATEX_TEXT_RE = re.compile(
    r"(?s)\\text\{([^{}]*?(?:[^{}]*?\{[^{}]*?(?:[^{}]*?\{[^{}]*?\}[^{}]*?)*?"
    r"[^{}]*?\}[^{}]*?)*?[^{}]*?)\}"
)
LATEX_TESTOUT_RE = re.compile(
    r"(?s)\\begin\{(?P<tag>testmessage|testprint|testresult)\}"
    r"(?P<content>.*?)\\end\{(?P=tag)\}"
)

LATEX_TESTOUT_DELIM_RE = re.compile(r", ")

# The goal of the following pattern is to enclose the numbers included in
# expressions produced by tests between ```\allowbreak{}```. The pattern matches
# with negative numbers or positive numbers preceded by a space character.
# To avoid applying the replacement, what is needed if the number is part of a
# LaTeX parameter (for instance ```\includegraphics[width=5cm]{...}```)
# the space before the number must be avoided. For example,
# ```\includegraphics[width= 5cm]{...}``` must be rewritten as
# \includegraphics[width=\allowbreak{}5\allowbreak{}cm]{...} which is not a valid
# LaTeX command.
NUMBER_RE = re.compile(r"([ -])(\d*(?<!\.)\.\d+|\d+\.(?!\.)\d*|\d+)")
OUTSIDE_ASY_RE = re.compile(r"(?s)((?:^|\\end\{asy\}).*?(?:$|\\begin\{asy\}))")


def escape_latex_code(text) -> str:
    """Escape verbatim Mathics input"""

    text = escape_latex_output(text)
    escape_char = get_latex_escape_char(text)
    return "\\lstinline%s%s%s" % (escape_char, text, escape_char)


def escape_latex(text):
    """Escape documentation text"""

    def repl_python(match):
        return (
            r"""\begin{lstlisting}[style=python]
%s
\end{lstlisting}"""
            % match.group(1).strip()
        )

    text, post_substitutions = pre_sub(PYTHON_RE, text, repl_python)

    text = _replace_all(
        text,
        [
            ("\\", "\\\\"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("~", "\\~{ }"),
            ("&", "\\&"),
            ("%", "\\%"),
            ("#", "\\#"),
        ],
    )

    def repl(match):
        text = match.group(1)
        if text:
            text = _replace_all(text, [("\\'", "'"), ("^", "\\^")])
            escape_char = get_latex_escape_char(text)
            text = LATEX_RE.sub(
                lambda m: "%s%s\\codevar{\\textit{%s}}%s\\lstinline%s"
                % (escape_char, m.group(1), m.group(2), m.group(3), escape_char),
                text,
            )
            if text.startswith(" "):
                text = r"\ " + text[1:]
            if text.endswith(" "):
                text = text[:-1] + r"\ "
            return "\\code{\\lstinline%s%s%s}" % (escape_char, text, escape_char)
        else:
            # treat double '' literaly
            return "''"

    text = MATHICS_RE.sub(repl, text)

    text = LATEX_RE.sub(
        lambda m: "%s\\textit{%s}%s" % (m.group(1), m.group(2), m.group(3)), text
    )

    text = text.replace("\\\\'", "'")

    def repl_dl(match):
        text = match.group(1)
        text = DL_ITEM_RE.sub(
            lambda m: "\\%(tag)s{%(content)s}\n" % m.groupdict(), text
        )
        return "\\begin{definitions}%s\\end{definitions}" % text

    text = DL_RE.sub(repl_dl, text)

    def repl_list(match):
        tag = match.group("tag")
        content = match.group("content")
        content = LIST_ITEM_RE.sub(lambda m: "\\item %s\n" % m.group(1), content)
        env = "itemize" if tag == "ul" else "enumerate"
        return "\\begin{%s}%s\\end{%s}" % (env, content, env)

    text = LIST_RE.sub(repl_list, text)

    # FIXME: get this from MathicsScanner
    text = _replace_all(
        text,
        [
            ("$", r"\$"),
            ("\00f1", r"\~n"),
            ("\u00e7", r"\c{c}"),
            ("\u00e9", r"\'e"),
            ("\u00ea", r"\^e"),
            ("\u03b3", r"$\gamma$"),
            ("\u03b8", r"$\theta$"),
            ("\u03bc", r"$\mu$"),
            ("\u03c0", r"$\pi$"),
            ("\u03d5", r"$\phi$"),
            ("\u2107", r"$\mathrm{e}$"),
            ("\u222b", r"\int"),
            ("\u2243", r"$\simeq$"),
            ("\u2026", r"$\dots$"),
            ("\u2260", r"$\ne$"),
            ("\u2264", r"$\le$"),
            ("\u2265", r"$\ge$"),
            ("\u22bb", r"$\oplus$"),  # The WL veebar-looking symbol isn't in AMSLaTeX
            ("\u22bc", r"$\barwedge$"),
            ("\u22bd", r"$\veebar$"),
            ("\u21d2", r"$\Rightarrow$"),
            ("\uf74c", r"d"),
        ],
    )

    def repl_char(match):
        char = match.group(1)
        return {
            "^": "$^\\wedge$",
        }[char]

    text = LATEX_CHAR_RE.sub(repl_char, text)

    def repl_img(match):
        src = match.group("src")
        title = match.group("title")
        label = match.group("label")
        return r"""\begin{figure*}[htp]
\centering
\includegraphics[width=\textwidth]{images/%(src)s}
\caption{%(title)s}
\label{%(label)s}
\end{figure*}""" % {
            "src": src,
            "title": title,
            "label": label,
        }

    text = IMG_RE.sub(repl_img, text)

    def repl_imgpng(match):
        src = match.group("src")
        return r"\includegraphics[scale=1.0]{images/%(src)s}" % {"src": src}

    text = IMG_PNG_RE.sub(repl_imgpng, text)

    def repl_ref(match):
        return r"figure \ref{%s}" % match.group("label")

    text = REF_RE.sub(repl_ref, text)

    def repl_quotation(match):
        return r"``%s''" % match.group(1)

    def repl_hypertext(match) -> str:
        tag = match.group("tag")
        content = match.group("content")
        #
        # Sometimes it happens that the URL does not
        # fit in 80 characters. Then, to avoid that
        # flake8 complains, and also to have a
        # nice and readable ASCII representation,
        # we would like to split the URL in several,
        # lines, having indentation spaces.
        #
        # The following line removes these extra
        # characters, which would spoil the URL,
        # producing a single line, space-free string.
        #
        content = content.replace(" ", "").replace("\n", "")
        if tag == "em":
            return r"\emph{%s}" % content
        elif tag == "url":
            text = match.group("text")
            if text is None:
                return "\\url{%s}" % content
            else:
                # If we have "/doc" as the beginning the URL link
                # then is is a link to a section
                # in this manual, so use "\ref" rather than "\href'.
                if content.find("/doc/") == 0:
                    slug = "/".join(content.split("/")[2:]).rstrip("/")
                    return "%s of section~\\ref{%s}" % (text, latex_label_safe(slug))
                else:
                    return "\\href{%s}{%s}" % (content, text)
                return "\\href{%s}{%s}" % (content, text)

    text = QUOTATIONS_RE.sub(repl_quotation, text)
    text = HYPERTEXT_RE.sub(repl_hypertext, text)

    def repl_console(match):
        tag = match.group("tag")
        content = match.group("content")
        content = content.strip()
        content = content.replace(r"\$", "$")
        if tag == "con":
            return "\\console{%s}" % content
        else:
            return "\\begin{lstlisting}\n%s\n\\end{lstlisting}" % content

    text = CONSOLE_RE.sub(repl_console, text)

    def repl_italic(match):
        content = match.group("content")
        return "\\emph{%s}" % content

    text = ITALIC_RE.sub(repl_italic, text)

    # def repl_asy(match):
    #     """
    #     Ensure \begin{asy} and \end{asy} are on their own line,
    #     but there shall be no extra empty lines
    #     """
    #     #tag = match.group(1)
    #     #return '\n%s\n' % tag
    #     #print "replace"
    #     return '\\end{asy}\n\\begin{asy}'
    # text = LATEX_BETWEEN_ASY_RE.sub(repl_asy, text)

    def repl_subsection(match):
        return "\n\\subsection*{%s}\n" % match.group(1)

    text = SUBSECTION_RE.sub(repl_subsection, text)
    text = SUBSECTION_END_RE.sub("", text)

    for key, (xml, tex) in SPECIAL_COMMANDS.items():
        # "\" has been escaped already => 2 \
        text = text.replace("\\\\" + key, tex)

    text = post_sub(text, post_substitutions)

    return text


def escape_latex_output(text) -> str:
    """Escape Mathics output"""

    text = _replace_all(
        text,
        [
            ("\\", "\\\\"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("~", "\\~"),
            ("&", "\\&"),
            ("%", "\\%"),
            ("$", r"\$"),
            ("_", "\\_"),
        ],
    )
    return text


def get_latex_escape_char(text):
    for escape_char in ("'", "~", "@"):
        if escape_char not in text:
            return escape_char
    raise ValueError


def latex_label_safe(s: str) -> str:
    s = s.replace("\\$", "dollar-")
    s = s.replace("$", "dollar-")
    return s


def post_process_latex(result):
    """
    Some post-processing hacks of generated LaTeX code to handle linebreaks
    """

    WORD_SPLIT_RE = re.compile(r"(\s+|\\newline\s*)")

    def wrap_word(word):
        if word.strip() == r"\newline":
            return word
        return r"\text{%s}" % word

    def repl_text(match):
        text = match.group(1)
        if not text:
            return r"\text{}"
        words = WORD_SPLIT_RE.split(text)
        assert len(words) >= 1
        if len(words) > 1:
            text = ""
            index = 0
            while index < len(words) - 1:
                text += "%s%s\\allowbreak{}" % (
                    wrap_word(words[index]),
                    wrap_word(words[index + 1]),
                )
                index += 2
            text += wrap_word(words[-1])
        else:
            text = r"\text{%s}" % words[0]
        if not text:
            return r"\text{}"
        text = text.replace("><", r">}\allowbreak\text{<")
        return text

    def repl_out_delim(match):
        return ",\\allowbreak{} "

    def repl_number(match):
        guard = r"\allowbreak{}"
        inter_groups_pre = r"\,\discretionary{\~{}}{\~{}}{}"
        inter_groups_post = r"\discretionary{\~{}}{\~{}}{}"
        number = match.group(1) + match.group(2)
        parts = number.split(".")
        if len(number) <= 3:
            return number
        assert 1 <= len(parts) <= 2
        pre_dec = parts[0]
        groups = []
        while pre_dec:
            groups.append(pre_dec[-3:])
            pre_dec = pre_dec[:-3]
        pre_dec = inter_groups_pre.join(reversed(groups))
        if len(parts) == 2:
            post_dec = parts[1]
            groups = []
            while post_dec:
                groups.append(post_dec[:3])
                post_dec = post_dec[3:]
            post_dec = inter_groups_post.join(groups)
            result = pre_dec + "." + post_dec
        else:
            result = pre_dec
        return guard + result + guard

    def repl_array(match):
        content = match.group(1)
        lines = content.split("\\\\")
        content = "".join(
            r"\begin{dmath*}%s\end{dmath*}" % line for line in lines if line.strip()
        )
        return r"\begin{testresultlist}%s\end{testresultlist}" % content

    def repl_out(match):
        tag = match.group("tag")
        content = match.group("content")
        content = LATEX_TESTOUT_DELIM_RE.sub(repl_out_delim, content)
        content = NUMBER_RE.sub(repl_number, content)
        content = content.replace(r"\left[", r"\left[\allowbreak{}")
        return "\\begin{%s}%s\\end{%s}" % (tag, content, tag)

    def repl_inline_end(match):
        """Prevent linebreaks between inline code and sentence delimeters"""

        code = match.group("all")
        if code[-2] == "}":
            code = code[:-2] + code[-1] + code[-2]
        return r"\mbox{%s}" % code

    def repl_console(match):
        code = match.group(1)
        code = code.replace("/", r"/\allowbreak{}")
        return r"\console{%s}" % code

    def repl_nonasy(match):
        result = match.group(1)
        result = LATEX_TEXT_RE.sub(repl_text, result)
        result = LATEX_TESTOUT_RE.sub(repl_out, result)
        result = LATEX_ARRAY_RE.sub(repl_array, result)
        result = LATEX_INLINE_END_RE.sub(repl_inline_end, result)
        result = LATEX_CONSOLE_RE.sub(repl_console, result)
        return result

    return OUTSIDE_ASY_RE.sub(repl_nonasy, result)


def strip_system_prefix(name):
    if name.startswith("System`"):
        stripped_name = name[len("System`") :]
        # don't return Private`sym for System`Private`sym
        if "`" not in stripped_name:
            return stripped_name
    return name


class LaTeXDocTest(DocTest):
    """
    DocTest formatting rules:

    * `>>` Marks test case; it will also appear as part of
           the documentation.
    * `#>` Marks test private or one that does not appear as part of
           the documentation.
    * `X>` Shows the example in the docs, but disables testing the example.
    * `S>` Shows the example in the docs, but disables testing if environment
           variable SANDBOX is set.
    * `=`  Compares the result text.
    * `:`  Compares an (error) message.
      `|`  Prints output.
    """

    def __init__(self, index, testcase, key_prefix=None):
        def strip_sentinal(line):
            """Remove END_LINE_SENTINAL from the end of a line if it appears.

            Some editors like to strip blanks at the end of a line.
            Since the line ends in END_LINE_SENTINAL which isn't blank,
            any blanks that appear before will be preserved.

            Some tests require some lines to be blank or entry because
            Mathics output can be that way
            """
            if line.endswith(END_LINE_SENTINAL):
                line = line[: -len(END_LINE_SENTINAL)]

            # Also remove any remaining trailing blanks since that
            # seems *also* what we want to do.
            return line.strip()

        self.index = index
        self.result = None
        self.outs = []

        # Private test cases are executed, but NOT shown as part of the docs
        self.private = testcase[0] == "#"

        # Ignored test cases are NOT executed, but shown as part of the docs
        # Sandboxed test cases are NOT executed if environment SANDBOX is set
        if testcase[0] == "X" or (testcase[0] == "S" and getenv("SANDBOX", False)):
            self.ignore = True
            # substitute '>' again so we get the correct formatting
            testcase[0] = ">"
        else:
            self.ignore = False

        self.test = strip_sentinal(testcase[1])

        self.key = None
        if key_prefix:
            self.key = tuple(key_prefix + (index,))
        outs = testcase[2].splitlines()
        for line in outs:
            line = strip_sentinal(line)
            if line:
                if line.startswith("."):
                    text = line[1:]
                    if text.startswith(" "):
                        text = text[1:]
                    text = "\n" + text
                    if self.result is not None:
                        self.result += text
                    elif self.outs:
                        self.outs[-1].text += text
                    continue

                match = TESTCASE_OUT_RE.match(line)
                if not match:
                    continue
                symbol, text = match.group(1), match.group(2)
                text = text.strip()
                if symbol == "=":
                    self.result = text
                elif symbol == ":":
                    out = Message("", "", text)
                    self.outs.append(out)
                elif symbol == "|":
                    out = Print(text)
                    self.outs.append(out)

    def __str__(self):
        return self.test

    def latex(self, doc_data: dict) -> str:
        """
        Produces the LaTeX-formatted fragment that corresponds the
        test sequence and results for a single Builtin that has been run.

        The key for doc_data is the part/chapter/section{/subsection} test number
        and the value contains Result object data turned into a dictionary.

        In particular, each test in the test sequence includes the, input test,
        the result produced and any additional error output.
        The LaTeX-formatted string fragment is returned.
        """
        if self.key is None:
            return ""
        output_for_key = doc_data.get(self.key, None)
        if output_for_key is None:
            output_for_key = get_results_by_test(self.test, self.key, doc_data)
        text = f"%% Test {'/'.join((str(x) for x in self.key))}\n"
        text += "\\begin{testcase}\n"
        text += "\\test{%s}\n" % escape_latex_code(self.test)

        results = output_for_key.get("results", [])
        for result in results:
            for out in result["out"]:
                kind = "message" if out["message"] else "print"
                text += "\\begin{test%s}%s\\end{test%s}" % (
                    kind,
                    escape_latex_output(out["text"]),
                    kind,
                )

            test_text = result["result"]
            if test_text:  # is not None and result['result'].strip():
                asy_count = test_text.count("\\begin{asy}")
                if asy_count >= 0:
                    global next_asy_number
                    text += f"%% mathics-{next_asy_number}.asy\n"
                    next_asy_number += asy_count

                text += "\\begin{testresult}%s\\end{testresult}" % result["result"]
        text += "\\end{testcase}"
        return text


class LaTeXDocumentation(Documentation):
    def __str__(self):
        return "\n\n\n".join(str(part) for part in self.parts)

    def get_section(self, part_slug, chapter_slug, section_slug):
        part = self.parts_by_slug.get(part_slug)
        if part:
            chapter = part.chapters_by_slug.get(chapter_slug)
            if chapter:
                return chapter.sections_by_slug.get(section_slug)
        return None

    def latex(
        self,
        doc_data: dict,
        quiet=False,
        filter_parts=None,
        filter_chapters=None,
        filter_sections=None,
    ) -> str:
        """Render self as a LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        parts = []
        appendix = False
        for part in self.parts:
            if filter_parts:
                if part.title not in filter_parts:
                    continue
            text = part.latex(
                doc_data,
                quiet,
                filter_chapters=filter_chapters,
                filter_sections=filter_sections,
            )
            if part.is_appendix and not appendix:
                appendix = True
                text = "\n\\appendix\n" + text
            parts.append(text)
        result = "\n\n".join(parts)
        result = post_process_latex(result)
        return result


class LaTeXDoc(XMLDoc):
    """A class to hold our internal XML-like format data.
    The `latex()` method can turn this into LaTeX.

    Mathics core also uses this in getting usage strings (`??`).
    """

    def __init__(self, doc, title, section):
        self.title = title
        if section:
            chapter = section.chapter
            part = chapter.part
            # Note: we elide section.title
            key_prefix = (part.title, chapter.title, title)
        else:
            key_prefix = None

        self.rawdoc = doc
        self.items = gather_tests(
            self.rawdoc, LaTeXDocTests, LaTeXDocTest, LaTeXDocText, key_prefix
        )
        return

    def latex(self, doc_data: dict):
        if len(self.items) == 0:
            if hasattr(self, "rawdoc") and len(self.rawdoc) != 0:
                # We have text but no tests
                return escape_latex(self.rawdoc)

        return "\n".join(
            item.latex(doc_data) for item in self.items if not item.is_private()
        )


class LaTeXMathicsDocumentation(Documentation):
    def __init__(self, want_sorting=False):
        self.doc_chapter_fn = LaTeXDocChapter
        self.doc_dir = settings.DOC_DIR
        self.doc_fn = LaTeXDoc
        self.doc_data_file = settings.get_doctest_latex_data_path(
            should_be_readable=True
        )
        self.doc_guide_section_fn = LaTeXDocGuideSection
        self.doc_part_fn = LaTeXDocPart
        self.doc_section_fn = LaTeXDocSection
        self.doc_subsection_fn = LaTeXDocSubsection
        self.doctest_latex_pcl_path = settings.DOCTEST_LATEX_DATA_PCL
        self.parts = []
        self.parts_by_slug = {}
        self.title = "Overview"

        self.gather_doctest_data()

    def latex(
        self,
        doc_data: dict,
        quiet=False,
        filter_parts=None,
        filter_chapters=None,
        filter_sections=None,
    ) -> str:
        """Render self as a LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        parts = []
        appendix = False
        for part in self.parts:
            if filter_parts:
                if part.title not in filter_parts:
                    continue
            text = part.latex(
                doc_data,
                quiet,
                filter_chapters=filter_chapters,
                filter_sections=filter_sections,
            )
            if part.is_appendix and not appendix:
                appendix = True
                text = "\n\\appendix\n" + text
            parts.append(text)
        result = "\n\n".join(parts)
        result = post_process_latex(result)
        return result


class LaTeXDocPart(DocPart):
    def latex(
        self, doc_data: dict, quiet=False, filter_chapters=None, filter_sections=None
    ) -> str:
        """Render this Part object as LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if self.is_reference:
            chapter_fn = sorted_chapters
        else:
            chapter_fn = lambda x: x
        result = "\n\n\\part{%s}\n\n" % escape_latex(self.title) + (
            "\n\n".join(
                chapter.latex(doc_data, quiet, filter_sections=filter_sections)
                for chapter in chapter_fn(self.chapters)
                if not filter_chapters or chapter.title in filter_chapters
            )
        )
        if self.is_reference:
            result = "\n\n\\referencestart" + result
        return result


class LaTeXDocChapter(DocChapter):
    def latex(self, doc_data: dict, quiet=False, filter_sections=None) -> str:
        """Render this Chapter object as LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            print(f"Formatting Chapter {self.title}")
        intro = self.doc.latex(doc_data).strip()
        if intro:
            short = "short" if len(intro) < 300 else ""
            intro = "\\begin{chapterintro%s}\n%s\n\n\\end{chapterintro%s}" % (
                short,
                intro,
                short,
            )
        chapter_sections = [
            ("\n\n\\chapter{%(title)s}\n\\chapterstart\n\n%(intro)s")
            % {"title": escape_latex(self.title), "intro": intro},
            "\\chaptersections\n",
            "\n\n".join(
                section.latex(doc_data, quiet)
                for section in sorted(self.sections)
                if not filter_sections or section.title in filter_sections
            ),
            "\n\\chapterend\n",
        ]
        return "".join(chapter_sections)


class LaTeXDocSection(DocSection):
    def __init__(
        self,
        chapter,
        title: str,
        text: str,
        operator,
        installed=True,
        in_guide=False,
        summary_text="",
    ):
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.operator = operator
        self.slug = slugify(title)
        self.subsections = []
        self.subsections_by_slug = {}
        self.summary_text = summary_text
        self.title = title

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )

        # Needs to come after self.chapter is initialized since
        # XMLDoc uses self.chapter.
        self.doc = LaTeXDoc(text, title, self)

        chapter.sections_by_slug[self.slug] = self

    def latex(self, doc_data: dict, quiet=False) -> str:
        """Render this Section object as LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter level.
            print(f"  Formatting Section {self.title}")
        title = escape_latex(self.title)
        if self.operator:
            title += " (\\code{%s})" % escape_latex_code(self.operator)
        index = (
            r"\index{%s}" % escape_latex(self.title)
            if self.chapter.part.is_reference
            else ""
        )
        content = self.doc.latex(doc_data)
        sections = "\n\n".join(section.latex(doc_data) for section in self.subsections)
        slug = f"{self.chapter.part.slug}/{self.chapter.slug}/{self.slug}"
        section_string = (
            "\n\n\\section*{%s}{%s}\n" % (title, index)
            + "\n\\label{%s}" % latex_label_safe(slug)
            + "\n\\sectionstart\n\n"
            + f"{content}"
            + ("\\addcontentsline{toc}{section}{%s}" % title)
            + sections
            + "\\sectionend"
        )
        return section_string


class LaTeXDocGuideSection(DocSection):
    """An object for a Documented Guide Section.
    A Guide Section is part of a Chapter. "Colors" or "Special Functions"
    are examples of Guide Sections, and each contains a number of Sections.
    like NamedColors or Orthogonal Polynomials.
    """

    def __init__(
        self, chapter: str, title: str, text: str, submodule, installed: bool = True
    ):
        self.chapter = chapter
        self.doc = LaTeXDoc(text, title, None)
        self.in_guide = False
        self.installed = installed
        self.section = submodule
        self.slug = slugify(title)
        self.subsections = []
        self.subsections_by_slug = {}
        self.title = title

        # FIXME: Sections never are operators. Subsections can have
        # operators though.  Fix up the view and searching code not to
        # look for the operator field of a section.
        self.operator = False

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )
        # print("YYY Adding section", title)
        chapter.sections_by_slug[self.slug] = self

    def get_tests(self):
        # FIXME: The below is a little weird for Guide Sections.
        # Figure out how to make this clearer.
        # A guide section's subsection are Sections without the Guide.
        # it is *their* subsections where we generally find tests.
        for section in self.subsections:
            if not section.installed:
                continue
            for subsection in section.subsections:
                # FIXME we are omitting the section title here...
                if not subsection.installed:
                    continue
                for doctests in subsection.items:
                    yield doctests.get_tests()

    def latex(self, doc_data: dict, quiet=False):
        """Render this Guide Section object as LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter level.
            print(f"  Formatting Guide Section {self.title}")
        intro = self.doc.latex(doc_data).strip()
        if intro:
            short = "short" if len(intro) < 300 else ""
            intro = "\\begin{guidesectionintro%s}\n%s\n\n\\end{guidesectionintro%s}" % (
                short,
                intro,
                short,
            )
        guide_sections = [
            (
                "\n\n\\section{%(title)s}\n\\sectionstart\n\n%(intro)s"
                "\\addcontentsline{toc}{section}{%(title)s}"
            )
            % {"title": escape_latex(self.title), "intro": intro},
            "\n\n".join(section.latex(doc_data) for section in self.subsections),
        ]
        return "".join(guide_sections)


class LaTeXDocSubsection:
    """An object for a Documented Subsection.
    A Subsection is part of a Section.
    """

    def __init__(
        self,
        chapter,
        section,
        title,
        text,
        operator=None,
        installed=True,
        in_guide=False,
        summary_text="",
    ):
        """
        Information that goes into a subsection object. This can be a written text, or
        text extracted from the docstring of a builtin module or class.

        About some of the parameters...

        Some subsections are contained in a grouping module and need special work to
        get the grouping module name correct.

        For example the Chapter "Colors" is a module so the docstring text for it is in
        mathics/builtin/colors/__init__.py . In mathics/builtin/colors/named-colors.py we have
        the "section" name for the class Read (the subsection) inside it.
        """

        self.doc = LaTeXDoc(text, title, section)
        self.chapter = chapter
        self.in_guide = in_guide
        self.installed = installed
        self.operator = operator

        self.section = section
        self.slug = slugify(title)
        self.subsections = []
        self.title = title

        if in_guide:
            # Tests haven't been picked out yet from the doc string yet.
            # Gather them here.
            self.items = gather_tests(text, LaTeXDocTests, LaTeXDocTest, LaTeXDocText)
        else:
            self.items = []

        if text.count("<dl>") != text.count("</dl>"):
            raise ValueError(
                "Missing opening or closing <dl> tag in "
                "{} documentation".format(title)
            )
        self.section.subsections_by_slug[self.slug] = self

    def latex(self, doc_data: dict, quiet=False, chapters=None):
        """Render this Subsection object as LaTeX string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter, and section nesting level.
            print(f"    Formatting Subsection Section {self.title}")

        title = escape_latex(self.title)
        if self.operator:
            title += " (\\code{%s})" % escape_latex_code(self.operator)
        index = (
            r"\index{%s}" % escape_latex(self.title)
            if self.chapter.part.is_reference
            else ""
        )
        content = self.doc.latex(doc_data)
        slug = f"{self.chapter.part.slug}/{self.chapter.slug}/{self.section.slug}/{self.slug}"

        section_string = (
            "\n\n\\subsection*{%(title)s}%(index)s\n"
            + "\n\\label{%s}" % latex_label_safe(slug)
            + "\n\\subsectionstart\n\n%(content)s"
            "\\addcontentsline{toc}{subsection}{%(title)s}"
            "%(sections)s"
            "\\subsectionend"
        ) % {
            "title": title,
            "index": index,
            "content": content,
            "sections": "\n\n".join(
                section.latex(doc_data, quiet) for section in self.subsections
            ),
        }
        return section_string


class LaTeXDocTests(DocTests):
    def latex(self, doc_data: dict):
        if len(self.tests) == 0:
            return "\n"

        testLatexStrings = [
            test.latex(doc_data) for test in self.tests if not test.private
        ]
        testLatexStrings = [t for t in testLatexStrings if len(t) > 1]
        if len(testLatexStrings) == 0:
            return "\n"

        return "\\begin{tests}%%\n%s%%\n\\end{tests}" % ("%\n".join(testLatexStrings))


class LaTeXDocText(DocText):
    def latex(self, doc_data):
        return escape_latex(self.text)
