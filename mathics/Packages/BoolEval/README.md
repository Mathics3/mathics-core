[![GitHub (pre-)release](https://img.shields.io/github/release/szhorvat/BoolEval/all.svg)](https://github.com/szhorvat/BoolEval/releases)
[![Github All Releases](https://img.shields.io/github/downloads/szhorvat/BoolEval/total.svg)](https://github.com/szhorvat/BoolEval/releases)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/szhorvat/BoolEval/issues)

# BoolEval

`BoolEval` is a Mathematica package that helps evaluate conditional expressions on numerical arrays, or filter numerical arrays based on conditions.  Is does this without unpacking packed arrays and offers a significant speedup over `Select` and `Cases` while maintaining convenient notation.  It is particularly useful in conjunction with `Listable` functions.

After installing, search the Documentation Center for "BoolEval" to see usage examples. 

BoolEval was inspired by the question [Does Mathematica have advanced indexing?](http://mathematica.stackexchange.com/q/2821/12) on the *Mathematica* StackExchange.

A preview of this package is available as [the `BoolEval` function in the Wolfram Function Repository](https://resources.wolframcloud.com/FunctionRepository/resources/BoolEval).

### Installation

BoolEval requires Mathematica 10.0 or later.

Download the `.paclet` file from [the GitHub release pages](https://github.com/szhorvat/BoolEval/releases), then install it using the `PacletInstall` function.

    Needs["PacletManager`"]
    PacletInstall["/path/to/BoolEval.paclet"]

For more information, see [*How can I install packages distributed as .paclet files?*](https://mathematica.stackexchange.com/q/141887/12)

The Wolfram Language will always use the latest installed version of BoolEval. Installed versions can be enumerated using the command:

    PacletFind["BoolEval"]
    
To uninstall all versions, use

    PacletUninstall["BoolEval"]

### Getting started

Go to Help → Wolfram Documentation and search for BoolEval or paste `BoolEval/tutorial/IntroductionToBoolEval` into the address bar of the documentation browser.
