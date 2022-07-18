# -*- coding: utf-8 -*-

"""
Drawing Options and Option Values

The various common Plot and Graphics options, along with the meaning of specific option values are described here.

"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.drawing-options-and-option-values"

# Until we have a better documentation system in place, we define classes for
# options. They are Builtins, even though they largely aren't.
#
# Our documentation system extracts, indexes, and provides doctests for
# builtins.


from mathics.builtin.base import Builtin


class Automatic(Builtin):
    """
    <dl>
      <dt>'Automatic'
      <dd>is used to specify an automatically computed option value.
    </dl>

    'Automatic' is the default for 'PlotRange', 'ImageSize', and other
    graphical options:

    >> Cases[Options[Plot], HoldPattern[_ :> Automatic]]
     = {Background :> Automatic, Exclusions :> Automatic, ImageSize :> Automatic, MaxRecursion :> Automatic, PlotRange :> Automatic, PlotRangePadding :> Automatic}
    """

    summary_text = "graph option value to choose parameters automatically"


class Axes(Builtin):
    """
    <dl>
      <dt>'Axes'
      <dd>is an option for charting and graphics functions that specifies whether axes should be drawn.
    </dl>

    <ul>
      <li> 'Axes->True' draws all axes.
      <li> 'Axes->False' draws no axes.
      <li> 'Axes->{False,True}' draws an axis $y$ but no $x$ axis in two dimensions.
    </ul>

    >> Graphics[Circle[], Axes -> True]
     = -Graphics-
    """

    summary_text = "graph option which determines whether axes are shown"


class Axis(Builtin):
    """
    <dl>
      <dt>'Axis'
      <dd>is a possible value for the 'Filling' option.
    </dl>

    >> ListLinePlot[Table[Sin[x], {x, -5, 5, 0.2}], Filling->Axis]
     = -Graphics-
    """

    summary_text = "graph option value to fill plot from curve to the axis"


class Bottom(Builtin):
    """
    <dl>
      <dt>'Bottom'
      <dd>is a possible value for the 'Filling' option.
    </dl>

    >> ListLinePlot[Table[Sin[x], {x, -5, 5, 0.2}], Filling->Bottom]
     = -Graphics-
    """

    summary_text = "graph option value to fill plot from curve to bottom"


class ChartLabels(Builtin):
    """
    <dl>
      <dt>'ChartLabels'
      <dd>is a charting option that specifies what labels should be used for chart elements.
    </dl>

    >> PieChart[{30, 20, 10}, ChartLabels -> {Dogs, Cats, Fish}]
     = -Graphics-
    """

    summary_text = "charting option specifying whether to label chart"


class ChartLegends(Builtin):
    """
    <dl>
      <dt>'ChartLegends'
      <dd>is an option for charting functions that specifies the legends to be used for chart elements.
    </dl>
    """

    summary_text = "chart option giving legends to a chart"


class Filling(Builtin):
    """
    <dl>
      <dt>'Filling -> [Top | Bottom| Axis]'
      <dd>'Filling' is a an option to 'ListPlot', 'Plot' or 'Plot3D', and related functions that indicates what filling to add under point, curves, and surfaces.
    </dl>

    >> ListLinePlot[Table[Sin[x], {x, -5, 5, 0.2}], Filling->Axis]
     = -Graphics-
    """

    summary_text = "Plot option for filling regions around its curve"


class Full(Builtin):
    """
    <dl>
      <dt>'Full'
      <dd>is a possible value for the 'Mesh' and 'PlotRange' options.
    </dl>
    """

    summary_text = "graph option value for Mesh and PlotRange"


class ImageSize(Builtin):
    """
    <dl>
      <dt>'ImageSize'
      <dd>is an option that specifies the overall size of an image to display.
    </dl>

    Specifications for both width and height can be any of the following:
    <dl>
      <dt>Automatic
      <dd>determined by location or other dimension (default)
      <dt>Tiny, Small, Medium, Large
      <dd>pre defined absolute sizes
    </dl>


    >> Plot[Sin[x], {x, 0, 10}, ImageSize -> Small]
     = -Graphics-
    """

    summary_text = "image option specifying the size of the final picture"


class Joined(Builtin):
    """
    <dl>
      <dt>'Joined $boolean$'
      <dd>is an option for 'Plot' that gives whether to join points to make lines.
    </dl>

    >> ListPlot[Table[n ^ 2, {n, 10}], Joined->True]
     = -Graphics-
    """

    summary_text = (
        "plot option indicating whether the data points are joined to make lines"
    )


class MaxRecursion(Builtin):
    """
    <dl>
      <dt>'MaxRecursion'
      <dd>is an option for functions like NIntegrate and Plot that specifies how many recursive subdivisions can be made.
    </dl>

    >> NIntegrate[Exp[-10^8 x^2], {x, -1, 1}, Method->"Internal", MaxRecursion -> 3]
     =  0.0777778
    >> NIntegrate[Exp[-10^8 x^2], {x, -1, 1}, Method->"Internal", MaxRecursion -> 6]
     =  0.00972222
    """

    summary_text = "function option specifying the maximum number of recursive subdivisions the function can perform"


class Mesh(Builtin):
    """
    <dl>
       <dt>'Mesh'
      <dd>is a charting option, such as for 'Plot', 'BarChart', 'PieChart', etc. that specifies the mesh to be drawn. The default is 'Mesh->None'.
     </dl>

    >> Plot[Sin[Cos[x^2]],{x,-4,4},Mesh->All]
     = -Graphics-

    >> Plot[Sin[x], {x,0,4 Pi}, Mesh->Full]
     = -Graphics-

    >> DensityPlot[Sin[x y], {x, -2, 2}, {y, -2, 2}, Mesh->Full]
     = -Graphics-

    >> Plot3D[Sin[x y], {x, -2, 2}, {y, -2, 2}, Mesh->Full]
     = -Graphics3D-
    """

    messages = {
        "ilevels": "`1` is not a valid mesh specification.",
    }
    summary_text = "charting option to indicate whether a mesh is shown"


class PlotPoints(Builtin):
    """
    <dl>
      <dt>'PlotPoints $n$'
      <dd>A number specifies how many initial sample points to use.
     </dl>

    >> Plot[Sin[Cos[x^2]],{x,-4,4}, PlotPoints->22]
     = -Graphics-
    """

    summary_text = "plot option given the initial size for the set of sample points"


class PlotRange(Builtin):
    """
    <dl>
      <dt>'PlotRange'
      <dd>is a charting option, such as for 'Plot', 'BarChart', 'PieChart', etc. that gives the range of coordinates to include in a plot.
    </dl>
    <ul>
      <li>All all points are included.
      <li>Automatic - outlying points are dropped.
      <li>$max$ - explicit limit for each function.
      <li>{$min$, $max$} - explicit limits for $y$ (2D), $z$ (3D), or array values.
      <li>{{$x$_$min$, $x$_$max$}, {{$y_min}, {$y_max}} - explit limits for $x$ and $y$.
    </ul>

    >> Plot[Sin[Cos[x^2]],{x,-4,4}, PlotRange -> All]
     = -Graphics-

    >> Graphics[Disk[], PlotRange -> {{-.5, .5}, {0, 1.5}}]
     = -Graphics-
    """

    summary_text = "plot option giving the range to be plotted"


class TicksStyle(Builtin):
    """
    <dl>
      <dt>'TicksStyle'
      <dd>is an option for graphics functions which specifies how ticks should be rendered.
    </dl>

    <ul>
    <li>TicksStyle gives styles for both tick marks and tick labels.
    <li>TicksStyle can be used in both two  and three-dimensional graphics.
    <li>TicksStyle->$list$ specifies the colors of each of the axes.
    </ul>

    >> Graphics[Circle[], Axes-> True, TicksStyle -> {Blue, Red}]
     = -Graphics-
    """

    summary_text = "graph option specifying the format of tick marks on axes"


class Top(Builtin):
    """
     <dl>
       <dt>'Top'
       <dd>is a possible value for the 'Filling' option.
     </dl>

    >> ListLinePlot[Table[Cos[x], {x, -5, 5, 0.2}], Filling->Top]
      = -Graphics-
    """

    summary_text = "graph option value to fill plot from curve to top"
