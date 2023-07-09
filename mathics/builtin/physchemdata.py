#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Physical and Chemical data
"""

import os
from csv import reader as csvreader

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer, String
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, strip_context

SymbolMissing = Symbol("Missing")


class NoElementDataFile(Exception):
    pass


def load_element_data():
    try:
        import mathics_scanner

        datadir = mathics_scanner.__file__[:-11]
        element_file = open(os.path.join(datadir, "data/element.csv"), "r")
    except Exception:
        raise NoElementDataFile("data/elements.csv is not available.")

    reader = csvreader(element_file, delimiter="\t")
    element_data = []
    for row in reader:
        element_data.append([value for value in row])
    element_file.close()
    return element_data


_ELEMENT_DATA = load_element_data()


class ElementData(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ElementData.html</url>

    <dl>
    <dt>'ElementData["$name$", "$property$"]'
        <dd>gives the value of the $property$ for the chemical
        specified by $name$.
    <dt>'ElementData[$n$, "$property$"]'
        <dd>gives the value of the $property$ for the $n$th chemical element.
    </dl>

    >> ElementData[74]
     = Tungsten

    >> ElementData["He", "AbsoluteBoilingPoint"]
     = 4.22

    >> ElementData["Carbon", "IonizationEnergies"]
     = {1086.5, 2352.6, 4620.5, 6222.7, 37831, 47277.}

    >> ElementData[16, "ElectronConfigurationString"]
     = [Ne] 3s2 3p4

    >> ElementData[73, "ElectronConfiguration"]
     = {{2}, {2, 6}, {2, 6, 10}, {2, 6, 10, 14}, {2, 6, 3}, {2}}

    The number of known elements:
    >> Length[ElementData[All]]
     = 118

    Some properties are not appropriate for certain elements:
    >> ElementData["He", "ElectroNegativity"]
     = Missing[NotApplicable]

    Some data is missing:
    >> ElementData["Tc", "SpecificHeat"]
     = Missing[NotAvailable]

    All the known properties:
    >> ElementData["Properties"]
     = {Abbreviation, AbsoluteBoilingPoint, AbsoluteMeltingPoint, AtomicNumber, AtomicRadius, AtomicWeight, Block, BoilingPoint, BrinellHardness, BulkModulus, CovalentRadius, CrustAbundance, Density, DiscoveryYear, ElectroNegativity, ElectronAffinity, ElectronConfiguration, ElectronConfigurationString, ElectronShellConfiguration, FusionHeat, Group, IonizationEnergies, LiquidDensity, MeltingPoint, MohsHardness, Name, Period, PoissonRatio, Series, ShearModulus, SpecificHeat, StandardName, ThermalConductivity, VanDerWaalsRadius, VaporizationHeat, VickersHardness, YoungModulus}

    >> ListPlot[Table[ElementData[z, "AtomicWeight"], {z, 118}]]
     = -Graphics-

    ## Ensure all data parses #664
    #> Outer[ElementData, Range[118], ElementData["Properties"]];
    """

    messages = {
        "noent": (
            "`1` is not a known entity, class, or tag for ElementData. "
            "Use ElementData[] for a list of entities."
        ),
        "noprop": (
            "`1` is not a known property for ElementData. "
            'Use ElementData["Properties"] for a list of properties.'
        ),
    }

    rules = {
        "ElementData[n_]": 'ElementData[n, "StandardName"]',
        "ElementData[]": "ElementData[All]",
        'ElementData["Properties"]': 'ElementData[All, "Properties"]',
    }

    summary_text = "Data about chemical elements"

    def eval_all(self, evaluation: Evaluation):
        "ElementData[All]"
        iprop = _ELEMENT_DATA[0].index("StandardName")
        return from_python([element[iprop] for element in _ELEMENT_DATA[1:]])

    def eval_all_properties(self, evaluation: Evaluation):
        'ElementData[All, "Properties"]'
        return from_python(sorted(_ELEMENT_DATA[0]))

    def eval_name(self, expr, prop, evaluation: Evaluation):
        "ElementData[expr_, prop_]"

        if isinstance(expr, String):
            py_name = expr.to_python(string_quotes=False)
            names = ["StandardName", "Name", "Abbreviation"]
            iprops = [_ELEMENT_DATA[0].index(s) for s in names]

            indx = None
            for iprop in iprops:
                try:
                    indx = [element[iprop] for element in _ELEMENT_DATA[1:]].index(
                        py_name
                    ) + 1
                except ValueError:
                    pass

            if indx is None:
                evaluation.message("ElementData", "noent", expr)
                return

            # Enter in the next if, but with expr being the index
            expr = Integer(indx)
        if isinstance(expr, Integer):
            py_n = expr.value
            py_prop = prop.to_python()

            # Check element specifier n or "name"
            if isinstance(py_n, int):
                if not 1 <= py_n <= 118:
                    evaluation.message("ElementData", "noent", expr)
                    return
            else:
                evaluation.message("ElementData", "noent", expr)
                return

            # Check property specifier
            if isinstance(py_prop, str):
                py_prop = str(py_prop)

            if py_prop == '"Properties"':
                result = []
                for i, p in enumerate(_ELEMENT_DATA[py_n]):
                    if p not in ["NOT_AVAILABLE", "NOT_APPLICABLE", "NOT_KNOWN"]:
                        result.append(_ELEMENT_DATA[0][i])
                return from_python(sorted(result))

            if not (
                isinstance(py_prop, str)
                and py_prop[0] == py_prop[-1] == '"'
                and py_prop.strip('"') in _ELEMENT_DATA[0]
            ):
                evaluation.message("ElementData", "noprop", prop)
                return

            iprop = _ELEMENT_DATA[0].index(py_prop.strip('"'))
            result = _ELEMENT_DATA[py_n][iprop]

            if result == "NOT_AVAILABLE":
                return Expression(SymbolMissing, String("NotAvailable"))

            if result == "NOT_APPLICABLE":
                return Expression(SymbolMissing, String("NotApplicable"))

            if result == "NOT_KNOWN":
                return Expression(SymbolMissing, String("Unknown"))

            result = evaluation.parse(result)
            if isinstance(result, Symbol):
                result = String(strip_context(result.get_name()))
            return result
