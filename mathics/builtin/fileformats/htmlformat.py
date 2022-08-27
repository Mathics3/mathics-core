# -*- coding: utf-8 -*-


"""
HTML

Basic implementation for a HTML importer

"""


from mathics.builtin.base import Builtin, MessageException
from mathics.builtin.files_io.files import MathicsOpen
from mathics.core.atoms import String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule

from io import BytesIO
import platform
import re

try:
    import lxml.html as lhtml
except ImportError:
    pass

SymbolXMLElement = Symbol("XMLElement")
SymbolXMLObject = Symbol("XMLObject")


def node_to_xml_element(node, strip_whitespace=True):
    def children():
        text = node.text
        if text:
            if strip_whitespace:
                text = text.strip()
            if text:
                yield String(text)
        for child in node:
            for element in node_to_xml_element(child, strip_whitespace):
                yield element
        tail = node.tail
        if tail:
            if strip_whitespace:
                tail = tail.strip()
            if tail:
                yield String(tail)

    def attributes():
        for name, value in node.attrib.items():
            yield Expression(SymbolRule, from_python(name), from_python(value))

    return [
        Expression(
            SymbolXMLElement,
            String(node.tag),
            to_mathics_list(*list(attributes())),
            to_mathics_list(*list(children())),
        )
    ]


def xml_object(tree):
    declaration = [
        Expression(
            Expression(SymbolXMLObject, String("Declaration")),
            to_expression(
                SymbolRule, String("Version"), String(tree.docinfo.xml_version or "1.0")
            ),
            Expression(
                SymbolRule,
                String("Standalone"),
                String("yes") if tree.docinfo.standalone else String("no"),
            ),
            Expression(SymbolRule, String("Encoding"), String(tree.docinfo.encoding)),
        )
    ]

    return Expression(
        Expression(SymbolXMLObject, String("Document")),
        to_mathics_list(*declaration),
        *node_to_xml_element(tree.getroot())
    )


class ParseError(Exception):
    pass


if platform.python_implementation() == "PyPy":

    def parse_html_stream(f):
        parser = lhtml.HTMLParser(encoding="utf8")
        return lhtml.parse(f, parser)

else:

    def parse_html_stream(f):
        return lhtml.parse(f)


def parse_html_file(filename):
    with MathicsOpen(filename, "rb") as f:
        return parse_html_stream(f)


def parse_html(parse, text, evaluation):
    try:
        return parse(text.get_string_value())
    except IOError:
        evaluation.message("General", "noopen", text.get_string_value())
        return Symbol("$Failed")
    except MessageException as e:
        e.message(evaluation)
        return Symbol("$Failed")


class _HTMLBuiltin(Builtin):
    context = "HTML`"

    requires = ("lxml",)


class _TagImport(_HTMLBuiltin):
    def _import(self, tree):
        raise NotImplementedError

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        tree = parse_html(parse_html_file, text, evaluation)
        if isinstance(tree, Symbol):  # $Failed?
            return tree
        return ListExpression(
            to_expression(SymbolRule, self.tag_name, self._import(tree))
        )


class _Get(_HTMLBuiltin):
    context = "HTML`Parser`"

    messages = {
        "prserr": "``.",
    }

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        root = parse_html(self._parse, text, evaluation)
        if isinstance(root, Symbol):  # $Failed?
            return root
        else:
            return xml_object(root)


class HTMLGet(_Get):
    """
    <dl>
    <dd>HTMLGet['str']
    <dt>Parses 'str' as HTML code.
    </dl>
    """

    summary_text = "parse HTML code"

    def _parse(self, text):
        return parse_html_file(text)


class HTMLGetString(_Get):
    """
    <dl>
    <dt>'HTML`Parser`HTMLGetString["string"]'
    <dd> parses HTML code contained in "string".
    </dl>
    #> Head[HTML`Parser`HTMLGetString["<a></a>"]]
     = XMLObject[Document]

    #> Head[HTML`Parser`HTMLGetString["<a><b></a>"]]
     = XMLObject[Document]
    """

    summary_text = "parse HTML code"

    def _parse(self, text):
        with BytesIO() as f:
            f.write(text.encode("utf8"))
            f.seek(0)
            return parse_html_stream(f)


class _DataImport(_TagImport):
    def _import(self, tree):
        full_data = self.full_data

        if full_data:

            def add_data(data_list, x):
                data_list.append(x)
                return data_list

        else:

            def add_data(data_list, x):
                if x is None:
                    return data_list
                if data_list is None:
                    return [x]
                elif len(x) == 1:
                    data_list.extend(x)
                elif x:
                    data_list.append(to_mathics_list(*x))
                return data_list

        newline = re.compile(r"\s+")

        def add_text(data_list, node):
            deep_data = traverse(node)
            if deep_data:  # if there's data, we ignore any text
                add_data(data_list, deep_data)
            else:
                t = []
                for s in node.xpath(".//text()"):
                    t.append(s)
                if t or full_data:
                    data_list.append(String(newline.sub(" ", " ".join(t))))

        def traverse(parent):
            if full_data:
                data = []
            else:
                data = None

            for node in parent:
                tag = node.tag
                if tag == "table":
                    row_data = []
                    for tr in node.xpath("tr"):
                        col_data = []
                        for td in tr.xpath("th|td"):
                            add_text(col_data, td)
                        add_data(row_data, col_data)
                    data = add_data(data, row_data)
                elif tag in ("ul", "ol"):
                    list_data = []
                    for child in node:
                        deep_data = traverse(child)
                        if deep_data:
                            add_data(list_data, deep_data)
                        elif child.tag == "li":
                            add_text(list_data, child)
                    data = add_data(data, list_data)
                else:
                    data = add_data(data, traverse(node))

            if data and len(data) == 1:
                data = data[0]

            return data

        result = traverse(tree.getroot())
        if result is None:
            result = []

        return to_mathics_list(*result)


class DataImport(_DataImport):
    """
    <dl>
    <dt>'HTML`DataImport["filename"]'
    <dd> imports data from a HTML file.
    </dl>
    >> Import["ExampleData/PrimeMeridian.html", "Data"][[1, 1, 2, 3]]
     = {Washington, D.C., 77...03′56.07″ W (1897) or 77...04′02.24″ W (NAD 27) or 77...04′01.16″ W (NAD 83), New Naval Observatory meridian}

    #> Length[Import["ExampleData/PrimeMeridian.html", "Data"]]
     = 3
    """

    summary_text = "import data from a HTML file"
    full_data = False
    tag_name = "Data"


class FullDataImport(_DataImport):
    """
    <dl>
    <dt>'HTML`FullDataImport["filename"]'
    <dd> imports data from a HTML file.
    </dl>
    """

    summary_text = "import data from a HTML file"
    full_data = True
    tag_name = "FullData"


class _LinksImport(_TagImport):
    def _links(self, root):
        raise NotImplementedError

    def _import(self, tree):
        return to_mathics_list(*list(self._links(tree)))


class HyperlinksImport(_LinksImport):
    """
    <dl>
    <dt>'HTML`HyperlinksImport["filename"]'
    <dd> imports hyperlinks from a HTML file.
    </dl>

    >> Import["ExampleData/PrimeMeridian.html", "Hyperlinks"][[1]]
     = /wiki/Prime_meridian_(Greenwich)
    """

    summary_text = "import hyperlinks from a HTML file"
    tag_name = "Hyperlinks"

    def _links(self, tree):
        for link in tree.xpath("//a"):
            href = link.get("href")
            if href and not href.startswith("#"):
                yield href


class ImageLinksImport(_LinksImport):
    """
    <dl>
    <dt>'HTML`ImageLinksImport["filename"]'
    <dd> imports links to the images included in a HTML file.
    </dl>
    >> Import["ExampleData/PrimeMeridian.html", "ImageLinks"][[6]]
     = //upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Prime_meridian.jpg/180px-Prime_meridian.jpg
    """

    summary_text = "import images from a HTML file"
    tag_name = "ImageLinks"

    def _links(self, tree):
        for link in tree.xpath("//img"):
            src = link.get("src")
            if src:
                yield src


class PlaintextImport(_TagImport):
    """
    <dl>
    <dt>'HTML`PlaintextImport["filename"]'
    <dd> imports plane text from a HTML file.
    </dl>
    >> DeleteDuplicates[StringCases[Import["ExampleData/PrimeMeridian.html"], RegularExpression["Wiki[a-z]+"]]]
     = {Wikipedia, Wikidata, Wikibase, Wikimedia}
    """

    summary_text = "import plane text from a HTML file"
    tag_name = "Plaintext"

    def _import(self, tree):
        def lines():
            for s in tree.xpath("//text()"):
                t = s.strip()
                if t:
                    yield t

        return String("\n".join(lines()))


class SourceImport(_HTMLBuiltin):
    """
    <dl>
    <dt>'HTML`SourceImport["filename"]'
    <dd> imports source code from a HTML file.
    </dl>
    >> DeleteDuplicates[StringCases[Import["ExampleData/PrimeMeridian.html", "Source"], RegularExpression["<t[a-z]+>"]]]
     = {<title>, <tr>, <th>, <td>}
    """

    summary_text = "import source code from a HTML file"

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""

        def source(filename):
            with MathicsOpen(filename, "r", encoding="UTF-8") as f:
                return ListExpression(
                    Expression(SymbolRule, String("Source"), String(f.read()))
                )

        return parse_html(source, text, evaluation)


class TitleImport(_TagImport):
    """
    <dl>
    <dt>'HTML`TitleImport["filename"]'
    <dd> imports the title string from a HTML file.
    </dl>
    >> Import["ExampleData/PrimeMeridian.html", "Title"]
     = Prime meridian - Wikipedia
    """

    summary_text = "import title string from a HTML file"
    tag_name = "Title"

    def _import(self, tree):
        for node in tree.xpath("//title"):
            return String(node.text_content())
        return String("")


class XMLObjectImport(_HTMLBuiltin):
    """
    <dl>
    <dt>'HTML`XMLObjectImport["filename"]'
    <dd> imports XML objects from a HTML file.
    </dl>
    >> Part[Import["ExampleData/PrimeMeridian.html", "XMLObject"], 2, 3, 1, 3, 2]
     = XMLElement[title, {}, {Prime meridian - Wikipedia}]
    """

    summary_text = "import XML objects from a HTML file"

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        xml = to_expression("HTML`Parser`HTMLGet", text).evaluate(evaluation)
        return ListExpression(Expression(SymbolRule, String("XMLObject"), xml))
