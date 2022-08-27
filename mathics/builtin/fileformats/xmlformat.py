# -*- coding: utf-8 -*-

"""
XML
"""


from mathics.builtin.base import Builtin
from mathics.builtin.files_io.files import MathicsOpen
from mathics.core.atoms import String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolFailed

from mathics.builtin.base import MessageException

from io import BytesIO
import re

# use lxml, if available, as it has some additional features such as parsing XML
# versions, comments and cdata. fallback on python builtin xml parser otherwise.

try:
    from lxml import etree as ET

    lxml_available = True
except ImportError:
    import xml.etree.ElementTree as ET

    lxml_available = False


def xml_cdata(node):
    if lxml_available:
        return String("\n".join(node.itertext()))


def xml_comments(node):
    if lxml_available:
        return to_expression(
            "List", *[String(s.text) for s in node.xpath("//comment()")]
        )


_namespace_key = to_mathics_list(
    "http://www.w3.org/2000/xmlns/", "xmlns", elements_conversion_fn=String
)


def node_to_xml_element(node, parent_namespace=None, strip_whitespace=True):
    if lxml_available:
        if isinstance(node, ET._Comment):
            items = [
                Expression(
                    to_expression("XMLObject", String("Comment")), String(node.text)
                )
            ]
            if node.tail is not None:
                items.append(String(node.tail))
            return items

    # see https://reference.wolfram.com/language/XML/tutorial/RepresentingXML.html

    default_namespace = node.get("xmlns")
    if default_namespace is None:
        default_namespace = parent_namespace

    if lxml_available:
        tag = ET.QName(node.tag)
        localname = tag.localname
        namespace = tag.namespace
    else:
        tag = node.tag
        if not tag.startswith("{"):
            namespace = None
            localname = tag
        else:
            m = re.match(r"\{(.*)\}(.*)", node.tag)
            namespace = m.group(1)
            localname = m.group(2)

    def children():
        text = node.text
        if text:
            if strip_whitespace:
                text = text.strip()
            if text:
                yield String(text)
        for child in node:
            for element in node_to_xml_element(
                child, default_namespace, strip_whitespace
            ):
                yield element
        tail = node.tail
        if tail:
            if strip_whitespace:
                tail = tail.strip()
            if tail:
                yield String(tail)

    def attributes():
        for name, value in node.attrib.items():
            if name == "xmlns":
                name = _namespace_key
            else:
                name = String(name)
            yield to_expression("Rule", name, from_python(value))

    if namespace is None or namespace == default_namespace:
        name = String(localname)
    else:
        name = to_mathics_list(String(namespace), String(localname))

    return [
        to_expression(
            "XMLElement",
            name,
            to_mathics_list(*list(attributes())),
            to_mathics_list(*list(children())),
        )
    ]


def xml_object(root):
    if lxml_available:
        tree = root.getroottree()
        declaration = [
            Expression(
                to_expression("XMLObject", String("Declaration")),
                to_expression(
                    "Rule", String("Version"), String(tree.docinfo.xml_version)
                ),
                to_expression(
                    "Rule", String("Encoding"), String(tree.docinfo.encoding)
                ),
            )
        ]
    else:
        declaration = []

    return Expression(
        to_expression("XMLObject", String("Document")),
        to_mathics_list(*declaration),
        *node_to_xml_element(root)
    )


class ParseError(Exception):
    pass


def parse_xml_stream(f):
    def parse(iter):  # inspired by http://effbot.org/zone/element-namespaces.htm
        root = None
        namespace = None

        for event, elem in iter:
            if event == "start-ns":
                if not elem[0]:  # setting default namespace?
                    namespace = elem[1]
            elif event == "start":
                if root is None:
                    root = elem
                if namespace:
                    elem.set("xmlns", namespace)
                    namespace = None

        return root

    if lxml_available:
        iterparse = ET.iterparse(
            f,
            ("start", "start-ns"),
            remove_comments=False,
            strip_cdata=False,
            recover=False,
        )
        try:
            return parse(iterparse)
        except ET.XMLSyntaxError as e:
            # note: iterparse.error_log, e.g. iterparse.error_log[-1].type_name contains the exact error code. this
            # might be useful for further error handling in the future.
            msg = str(e)

            # Different versions of lxml include different suffixes so trim.
            m = re.search(r"line \d+, column \d+", msg)
            if m is not None:
                msg = msg[: m.end()]

            raise ParseError(msg)
    else:
        try:
            return parse(ET.iterparse(f, ("start", "start-ns")))
        except ET.ParseError as e:
            if e.code == 9:  # XML_ERROR_JUNK_AFTER_DOC_ELEMENT
                # for this specific error, we produce the error exactly as lxml would. useful for use in test cases.
                line, column = e.position
                raise ParseError(
                    "Extra content at the end of the document, line %d, column %d"
                    % (line, column + 1)
                )
            else:
                raise ParseError(str(e))


def parse_xml_file(filename):
    with MathicsOpen(filename, "rb") as f:
        root = parse_xml_stream(f)
    return root


def parse_xml(parse, text, evaluation):
    try:
        return parse(text.get_string_value())
    except ParseError as e:
        evaluation.message("XML`Parser`XMLGet", "prserr", str(e))
        return SymbolFailed
    except IOError:
        evaluation.message("General", "noopen", text.get_string_value())
        return SymbolFailed
    except MessageException as e:
        e.message(evaluation)
        return SymbolFailed


class XMLObject(Builtin):
    """
    <dl>
    <dt>'XMLObject["type"]'
    <dd> represents the head of an XML object in symbolic XML.
    </dl>
    """

    summary_text = "the head of an xml object"


class XMLElement(Builtin):
    """
    <dl>
    <dt>'XMLElement[$tag$, {$attr_1$, $val_1$, ...}, {$data$, ...}]'
    <dd>   represents an element in symbolic XML.
    </dl>
    """

    summary_text = "an xml element"


class _Get(Builtin):
    context = "XML`Parser`"

    messages = {
        "prserr": "``.",
    }

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        root = parse_xml(self._parse, text, evaluation)
        if isinstance(root, Symbol):  # $Failed?
            return root
        else:
            return xml_object(root)


class XMLGet(_Get):
    """
    <dl>
    <dt>'XMLGet[...]'
    <dd> Internal. Document me.
    </dl>
    """

    summary_text = ""

    def _parse(self, text):
        return parse_xml_file(text)


class XMLGetString(_Get):
    """
    <dl>
    <dt>'XML`Parser`XMLGetString["string"]'
    <dd>parses "string" as XML code, and returns an XMLObject.
    </dl>
    >> Head[XML`Parser`XMLGetString["<a></a>"]]
     = XMLObject[Document]

    #> XML`Parser`XMLGetString["<a></a>xyz"]
     = $Failed
     : Extra content at the end of the document, line 1, column 8.
    """

    summary_text = "parse a xml object"

    def _parse(self, text):
        with BytesIO() as f:
            f.write(text.encode("utf8"))
            f.seek(0)
            return parse_xml_stream(f)


class PlaintextImport(Builtin):
    """
    <dl>
    <dt>'XML`PlaintextImport["string"]'
    <dd>parses "string" as XML code, and returns it as plain text.
    </dl>
    >> StringReplace[StringTake[Import["ExampleData/InventionNo1.xml", "Plaintext"],31],FromCharacterCode[10]->"/"]
     = MuseScore 1.2/2012-09-12/5.7/40
    """

    summary_text = "import plain text from xml"
    context = "XML`"

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        root = parse_xml(parse_xml_file, text, evaluation)
        if isinstance(root, Symbol):  # $Failed?
            return root

        def lines():
            for line in root.itertext():
                s = line.strip()
                if s:
                    yield s

        plaintext = String("\n".join(lines()))
        return to_mathics_list(to_expression("Rule", "Plaintext", plaintext))


class TagsImport(Builtin):
    """
    <dl>
    <dt>'XML`TagsImport["string"]'
    <dd>parses "string" as XML code, and returns a list with the tags found.
    </dl>
    >> Take[Import["ExampleData/InventionNo1.xml", "Tags"], 10]
     = {accidental, alter, arpeggiate, articulations, attributes, backup, bar-style, barline, beam, beat-type}
    """

    summary_text = "import tags text from xml"
    context = "XML`"

    @staticmethod
    def _tags(root):
        tags = set()

        def gather(node):
            tags.add(node.tag)
            for child in node:
                gather(child)

        gather(root)
        return to_mathics_list(*[String(tag) for tag in sorted(list(tags))])

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        root = parse_xml(parse_xml_file, text, evaluation)
        if isinstance(root, Symbol):  # $Failed?
            return root
        return to_mathics_list(to_expression("Rule", "Tags", self._tags(root)))


class XMLObjectImport(Builtin):
    """
    <dl>
    <dt>'XML`XMLObjectImport["string"]'
    <dd>parses "string" as XML code, and returns a list of XMLObjects found.
    </dl>

    >> Part[Import["ExampleData/InventionNo1.xml", "XMLObject"], 2, 3, 1]
     = XMLElement[identification, {}, {XMLElement[encoding, {}, {XMLElement[software, {}, {MuseScore 1.2}], XMLElement[encoding-date, {}, {2012-09-12}]}]}]

    >> Part[Import["ExampleData/Namespaces.xml"], 2]
     = XMLElement[book, {{http://www.w3.org/2000/xmlns/, xmlns} -> urn:loc.gov:books}, {XMLElement[title, {}, {Cheaper by the Dozen}], XMLElement[{urn:ISBN:0-395-36341-6, number}, {}, {1568491379}], XMLElement[notes, {}, {XMLElement[p, {{http://www.w3.org/2000/xmlns/, xmlns} -> http://www.w3.org/1999/xhtml}, {This is a, XMLElement[i, {}, {funny, book!}]}]}]}]
    """

    summary_text = "import elements from xml"
    context = "XML`"

    def apply(self, text, evaluation):
        """%(name)s[text_String]"""
        xml = to_expression("XML`Parser`XMLGet", text).evaluate(evaluation)
        return to_mathics_list(to_expression("Rule", "XMLObject", xml))
