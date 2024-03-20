"""
This code is the Markdown-specific part of the homegrown sphinx documentation.
FIXME: Ditch home-grown and lame parsing and hook into sphinx.
"""
import hashlib
import re
from pathlib import Path
from subprocess import Popen
from typing import Optional

from mathics.doc.doc_entries import (
    CONSOLE_RE,
    DL_ITEM_RE,
    DL_RE,
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
    DocTest,
    DocTests,
    DocText,
    DocumentationEntry,
    get_results_by_test,
    post_sub,
    pre_sub,
)
from mathics.doc.structure import (
    SUBSECTION_END_RE,
    SUBSECTION_RE,
    DocChapter,
    DocGuideSection,
    DocPart,
    DocSection,
    DocSubsection,
    Documentation,
    MathicsMainDocumentation,
    sorted_chapters,
)

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
# Markdown parameter (for instance ```\includegraphics[width=5cm]{...}```)
# the space before the number must be avoided. For example,
# ```\includegraphics[width= 5cm]{...}``` must be rewritten as
# \includegraphics[width=\allowbreak{}5\allowbreak{}cm]{...} which is not a valid
# Markdown command.
NUMBER_RE = re.compile(r"([ -])(\d*(?<!\.)\.\d+|\d+\.(?!\.)\d*|\d+)")
OUTSIDE_ASY_RE = re.compile(r"(?s)((?:^|\\end\{asy\}).*?(?:$|\\begin\{asy\}))")


# TeXForm produces \includeimage
LATEX_OUTPUT_IMAGE = re.compile(
    r"\\includegraphics\[(?P<imgparms>.*?)\]\{(?P<imgpath>.*?)\}"
)


ASY_GRAPHICS = re.compile(
    r"\\begin\{asy\}\n(?P<asycode>.*?)\\end\{asy\}", re.DOTALL | re.MULTILINE
)


def escape_markdown_code(text) -> str:
    """Escape verbatim Mathics input"""
    # TODO: see what to do here.
    return text


def escape_markdown(text):
    """Escape documentation text"""
    # By now, do nothing.
    return text


def escape_markdown_output(text) -> str:
    """Escape Mathics output"""
    return text
    text = replace_all(
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
    """Detect which escaped char is in a text"""
    for escape_char in ("'", "~", "@"):
        if escape_char not in text:
            return escape_char
    raise ValueError


def include_graphics_to_md(text):
    """Convert included pictures into a markdown format"""

    def repl_includegraphics(match):
        parms = match.group("imgparms").split(",")
        parms = [param.split("=") for param in parms]
        parms = [f"{parm}='{val}'" for parm, val in parms]

        path = match.group("imgpath")
        if parms:
            parms_str = " ".join(parms)
            return f"<img {parms_str} src='images/{path}' alt='Image'>"

        return f"![Image](images/{path})"

    text = LATEX_OUTPUT_IMAGE.sub(repl_includegraphics, text)

    def repl_asy_graph(match) -> str:
        global next_asy_number
        next_asy_number += 1
        content = match.group("asycode")
        asy_picture = png_from_asy(content, next_asy_number)
        if content.startswith("import three;"):
            return f"![Graphics3D](images/{asy_picture})"
        return f"![Graphics](images/{asy_picture})"

    text = ASY_GRAPHICS.sub(repl_asy_graph, text).strip()
    print(text)
    if not (
        text.startswith("<img ")
        or text.startswith("![Graphics")
        or text.startswith("![Image]")
    ):
        text = f"${text.strip()}$"

    return text


def markdown_label_safe(s: str) -> str:
    s = s.replace("\\$", "dollar-")
    s = s.replace("$", "dollar-")
    return s


def png_from_asy(code, number, IMAGENAMES_CODE={}):
    """Export an asy graphics into a png file.
    The filename is build from the code, so two images
    with the same code are identical, and has the same filename.
    If the filename already exists, the image is not generated again.
    """
    # FIXME: Implement the export
    folder = Path("images")
    strip_code = code.replace(" ", "").replace("\n", "")
    number_str = str(hashlib.sha256(strip_code.encode()).hexdigest())[:6]
    asy_filename = f"result-{number_str}.asy"
    png_filename = f"result-{number_str}.png"

    # Check if the same code was already generated.
    if code == IMAGENAMES_CODE.get(number_str, ""):
        return png_filename
    assert number_str not in IMAGENAMES_CODE
    IMAGENAMES_CODE[number_str] = code

    # If the image was already generated, just return
    # the filename.
    if folder.joinpath(png_filename).exists():
        return png_filename
    # This generates the image by calling asymptote
    with open(folder.joinpath(asy_filename), "w") as f:
        f.write(code)
    cmline = [
        "asy",
        "-cd",
        str(folder),
        "-render",
        "8",
        # "-quiet",
        "-tex",
        "xelatex",
        # "-render=0",
        # "-nosafe",
        # "-noprc",
        # "--gsOptions='-P'",
        "-o",
        png_filename,
        "-f",
        "png",
        asy_filename,
    ]
    with Popen(cmline):
        pass
    return png_filename


def post_process_markdown(result):
    """
    Some post-processing hacks of generated LaTeX code to handle linebreaks
    """
    return result

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


def replace_all(text, pairs):
    for i, j in pairs:
        text = text.replace(i, j)
    return text


def strip_system_prefix(name):
    if name.startswith("System`"):
        stripped_name = name[len("System`") :]
        # don't return Private`sym for System`Private`sym
        if "`" not in stripped_name:
            return stripped_name
    return name


class MarkdownDocTest(DocTest):
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

    def __str__(self):
        return self.test

    def markdown(self, doc_data: dict) -> str:
        """
        Produces the Markdown-formatted fragment that corresponds the
        test sequence and results for a single Builtin that has been run.

        The key for doc_data is the part/chapter/section{/subsection} test number
        and the value contains Result object data turned into a dictionary.

        In particular, each test in the test sequence includes the, input test,
        the result produced and any additional error output.
        The Markdown-formatted string fragment is returned.
        """
        if self.key is None:
            return ""
        output_for_key = doc_data.get(self.key, None)
        if output_for_key is None:
            output_for_key = get_results_by_test(self.test, self.key, doc_data)
        text = "\n::: {.test}\n" f"    >> {self.test}\n" ":::\n"

        results = output_for_key.get("results", [])
        for result in results:
            for out in result["out"]:
                kind = "{.message}" if out["message"] else "{.print}"
                out_text = escape_markdown_output(out["text"])
                text += f"\n::: {kind}\n    {out_text}\n:::\n"

            test_text = result["result"]
            if test_text:  # is not None and result['result'].strip():
                test_text = include_graphics_to_md(test_text)
                text += "\n" + test_text + "\n"
        return text


class MarkdownDocumentationEntry(DocumentationEntry):
    """A class to hold our internal markdown-like format data.
    The `latex()` method can turn this into Markdown.

    Mathics core also uses this in getting usage strings (`??`).
    """

    def __init__(self, doc_str: str, title: str, section: Optional[DocSection]):
        super().__init__(doc_str, title, section)

    def markdown(self, doc_data: dict) -> str:
        """
        Return a Markdown string representation for this object.
        """
        if len(self.items) == 0:
            if hasattr(self, "rawdoc") and len(self.rawdoc) != 0:
                # We have text but no tests
                return escape_markdown(self.rawdoc)

        return "\n".join(
            item.markdown(doc_data) for item in self.items if not item.is_private()
        )

    def _set_classes(self):
        """
        Tells to the initializator of DocumentationEntry
        the classes to be used to build the items.
        """
        self.docTest_collection_class = MarkdownDocTests
        self.docTest_class = MarkdownDocTest
        self.docText_class = MarkdownDocText


class MarkdownMathicsDocumentation(MathicsMainDocumentation):
    """
    Subclass of MathicsMainDocumentation which is able to
    produce a the documentation in Markdown format.
    """

    def __init__(self):
        super().__init__()
        self.load_documentation_sources()

    def _set_classes(self):
        """
        This function tells to the initializator of
        MathicsMainDocumentation which classes must be used to
        create the different elements in the hierarchy.
        """
        self.chapter_class = MarkdownDocChapter
        self.doc_class = MarkdownDocumentationEntry
        self.guide_section_class = MarkdownDocGuideSection
        self.part_class = MarkdownDocPart
        self.section_class = MarkdownDocSection
        self.subsection_class = MarkdownDocSubsection

    def markdown(
        self,
        doc_data: dict,
        quiet=False,
        filter_parts: Optional[str] = None,
        filter_chapters: Optional[str] = None,
        filter_sections: Optional[str] = None,
    ) -> str:
        """Render self as a Markdown string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        seen_parts = set()
        parts_set = None
        if filter_parts is not None:
            parts_set = set(filter_parts.split(","))
        parts = []
        appendix = False
        for part in self.parts:
            if filter_parts:
                if part.title not in filter_parts:
                    continue
            seen_parts.add(part.title)
            text = part.markdown(
                doc_data,
                quiet,
                filter_chapters=filter_chapters,
                filter_sections=filter_sections,
            )
            if part.is_appendix and not appendix:
                appendix = True
                text = "\n\\appendix\n" + text
            parts.append(text)
            if parts_set == seen_parts:
                break

        result = "\n\n".join(parts)
        result = post_process_markdown(result)
        return result


class MarkdownDocChapter(DocChapter):
    def markdown(
        self,
        doc_data: dict,
        quiet=False,
        filter_sections: Optional[str] = None,
    ) -> str:
        """Render this Chapter object as Markdown string and return that.

        ``output`` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            print(f"Formatting Chapter {self.title}")
        intro = self.doc.markdown(doc_data).strip()
        slug = f"/{self.part.slug}/{self.slug}"
        slug = "{#" f"{markdown_label_safe(slug)}" "}"
        slug = ""

        chapter_sections = [
            (f"\n\n## {self.title} {slug}\n\n" f"{intro}\n\n"),
            # ####################
            "\n\n".join(
                section.markdown(doc_data, quiet)
                # Here we should use self.all_sections, but for some reason
                # guidesections are not properly loaded, duplicating
                # the load of subsections.
                for section in sorted(self.guide_sections)
                if not filter_sections or section.title in filter_sections
            ),
            # ###################
            "\n\n".join(
                section.markdown(doc_data, quiet)
                # Here we should use self.all_sections, but for some reason
                # guidesections are not properly loaded, duplicating
                # the load of subsections.
                for section in sorted(self.sections)
                if not filter_sections or section.title in filter_sections
            ),
        ]
        return "".join(chapter_sections)


class MarkdownDocPart(DocPart):
    def markdown(
        self,
        doc_data: dict,
        quiet=False,
        filter_chapters=None,
        filter_sections=None,
    ) -> str:
        """Render this Part object as Markdown string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if self.is_reference:
            chapter_fn = sorted_chapters
        else:
            chapter_fn = lambda x: x

        title = self.title
        # len_title = len(title)
        # left_indent = max(0, (80 - len_title) // 2)
        # title = left_indent * " " + title + "\n"
        title = f"# {title}\n\n\n"

        result = title + (
            "\n\n".join(
                chapter.markdown(doc_data, quiet, filter_sections=filter_sections)
                for chapter in chapter_fn(self.chapters)
                if not filter_chapters or chapter.title in filter_chapters
            )
        )
        return result


class MarkdownDocSection(DocSection):
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
        super().__init__(
            chapter, title, text, operator, installed, in_guide, summary_text
        )

    def markdown(self, doc_data: dict, quiet=False) -> str:
        """Render this Section object as Markdown string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter level.
            print(f"  Formatting Section {self.title}")
        title = self.title
        if self.operator:
            title += " (\\code{%s})" % escape_markdown_code(self.operator)

        slug = f"{self.chapter.part.slug}/{self.chapter.slug}/{self.slug}"
        slug = "{." f"{markdown_label_safe(slug)}" "}"
        slug = ""
        content = self.doc.markdown(doc_data)
        sections = "\n\n".join(
            section.markdown(doc_data) for section in self.subsections
        )
        section_string = f"\n\n### {title} {slug} \n\n" + f"{content}" + sections
        return section_string


class MarkdownDocGuideSection(DocGuideSection):
    """An object for a Documented Guide Section.
    A Guide Section is part of a Chapter. "Colors" or "Special Functions"
    are examples of Guide Sections, and each contains a number of Sections.
    like NamedColors or Orthogonal Polynomials.
    """

    def __init__(
        self,
        chapter: MarkdownDocChapter,
        title: str,
        text: str,
        submodule,
        installed: bool = True,
    ):
        super().__init__(chapter, title, text, submodule, installed)

    def markdown(self, doc_data: dict, quiet=False) -> str:
        """Render this Section object as Markdown string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter level.
            print(f"  Formatting Section {self.title}")
        title = self.title
        if self.operator:
            title += " (\\code{%s})" % escape_markdown_code(self.operator)
        slug = f"{self.chapter.part.slug}/{self.chapter.slug}/{self.slug}"
        slug = "{." f"{markdown_label_safe(slug)}" "}"
        slug = ""
        content = self.doc.markdown(doc_data)
        sections = "\n\n".join(
            section.markdown(doc_data) for section in self.subsections
        )
        section_string = f"\n\n### {title} {slug} \n\n" + f"{content}" + sections
        return section_string

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


class MarkdownDocSubsection(DocSubsection):
    """An object for a Documented Subsection.
    A Subsection is part of a Section.
    """

    def markdown(self, doc_data: dict, quiet=False, chapters=None) -> str:
        """Render this Subsection object as Markdown string and return that.

        `output` is not used here but passed along to the bottom-most
        level in getting expected test results.
        """
        if not quiet:
            # The leading spaces help show chapter, and section nesting level.
            print(f"    Formatting Subsection Section {self.title}")

        title = self.title
        if self.operator:
            title += " (\\code{%s})" % escape_markdown_code(self.operator)

        slug = f"{self.chapter.part.slug}/{self.chapter.slug}/{self.section.slug}/{self.slug}"
        slug = "{." f"{markdown_label_safe(slug)}" "}"
        slug = ""
        content = self.doc.markdown(doc_data)

        section_string = (
            f"\n\n#### {title} {slug} \n\n"
            + content
            + "\n\n".join(
                section.markdown(doc_data, quiet) for section in self.subsections
            )
            + "\n\n"
        )
        return section_string


class MarkdownDocTests(DocTests):
    def markdown(self, doc_data: dict) -> str:
        if len(self.tests) == 0:
            return "\n"

        testMDStrings = [
            test.markdown(doc_data) for test in self.tests if not test.private
        ]
        testMDStrings = [t for t in testMDStrings if len(t) > 1]
        if len(testMDStrings) == 0:
            return "\n"

        tests_md = "\n".join(testMDStrings)
        return "\n\n:::::: {.Tests}\n" f"{tests_md}\n\n::::::\n\n"


class MarkdownDocText(DocText):
    """
    Class to hold some (non-test) Markdown text.
    """

    def markdown(self, doc_data: dict) -> str:
        """Escape the text as Markdown and return that string."""
        return escape_markdown(self.text)
