# -*- coding: utf-8 -*-

"""
Drawing Options and Option Values

The various common Plot and Graphics options, along with the meaning of specific \
option values are described here.

"""

# Until we have a better documentation system in place, we define classes for
# options. They are Builtins, even though they largely aren't.
#
# Our documentation system extracts, indexes, and provides doctests for
# builtins.


from mathics.core.builtin import Builtin

# This tells documentation how to sort this module
sort_order = "mathics.builtin.graphing-and-drawing.drawing-options-and-option-values"


class Automatic(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Automatic.html</url>

    <dl>
      <dt>'Automatic'
      <dd>is used to specify an automatically computed option value.
    </dl>

    'Automatic' is the default for 'PlotRange', 'ImageSize', and other
    graphical options:

    >> Cases[Options[Plot], HoldPattern[_ :> Automatic]]
     = {AxesOrigin :> Automatic, Background :> Automatic, BaselinePosition :> Automatic, ContentSelectable :> Automatic, CoordinatesToolOptions :> Automatic, Exclusions :> Automatic, FrameTicks :> Automatic, ImageSize :> Automatic, Method :> Automatic, PlotRange :> Automatic, PlotRangePadding :> Automatic, PlotRegion :> Automatic, PreserveImageOptions :> Automatic, Ticks :> Automatic}
    """

    summary_text = "graph option value to choose parameters automatically"


class Axes(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Axes.html</url>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/Axis.html</url>

    <dl>
      <dt>'Axis'
      <dd>is a possible value for the 'Filling' option.
    </dl>

    >> ListLinePlot[Table[Sin[x], {x, -5, 5, 0.2}], Filling->Axis]
     = -Graphics-
    """

    summary_text = "graph option value to fill plot from curve to the axis"


class Background(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Background.html</url>

    <dl>
      <dt>'Background'
      <dd>is an option that specifies the color of the background.
    </dl>

    The specification must be a Color specification or 'Automatic':

    >> Graphics3D[{Arrow[{{0,0,0},{1,0,1},{0,-1,0},{1,1,1}}]}, Background -> Red]
     = -Graphics3D-

    Notice that opacity cannot be specified by passing a 'List' containing 'Opacity' \
    together with a color specification like '{Red, Opacity[.1]}'. Use a color \
    directive with an alpha channel instead:

    >> Plot[{Sin[x], Cos[x], x / 3}, {x, -Pi, Pi}, Background -> RGBColor[0.5, .5, .5, 0.1]]
     = -Graphics-

    """

    summary_text = "graphic option for the color of the background"


class Bottom(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Bottom.html</url>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/ChartLabels.html</url>

    <dl>
      <dt>'ChartLabels'
      <dd>is a charting option that specifies what labels should be used for chart \
          elements.
    </dl>

    >> PieChart[{30, 20, 10}, ChartLabels -> {Dogs, Cats, Fish}]
     = -Graphics-
    """

    summary_text = "charting option for whether to label chart"


class ChartLegends(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ChartLegends.html</url>

    <dl>
      <dt>'ChartLegends'
      <dd>is an option for charting functions that specifies the legends to be used \
          for chart elements.
    </dl>

    """

    summary_text = "chart option for giving legends to a chart"


class Filling(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Filling.html</url>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/Full.html</url>

    <dl>
      <dt>'Full'
      <dd>is a possible value for the 'Mesh' and 'PlotRange' options.
    </dl>

    """

    summary_text = "graph option value for Mesh and PlotRange"


class ImageSize(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ImageSize.html</url>

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

    summary_text = "image option for the size of the final picture"


class Joined(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Joined.html</url>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/MaxRecursion.html</url>

    <dl>
      <dt>'MaxRecursion'
      <dd>is an option for functions like NIntegrate and Plot that specifies how many \
          recursive subdivisions can be made.
    </dl>

    >> NIntegrate[Exp[-10^8 x^2], {x, -1, 1}, Method->"Internal", MaxRecursion -> 3]
     =  0.0777778
    >> NIntegrate[Exp[-10^8 x^2], {x, -1, 1}, Method->"Internal", MaxRecursion -> 6]
     =  0.00972222
    """

    summary_text = (
        "function option for the maximum number of recursive "
        "subdivisions the function can perform"
    )


class Mesh(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Mesh.html</url>

    <dl>
       <dt>'Mesh'
      <dd>is a charting option, such as for 'Plot', 'BarChart', 'PieChart', etc. that \
          specifies the mesh to be drawn. The default is 'Mesh->None'.
     </dl>

    Options include:

    <ul>
      <li>None: No mesh is drawn
      <li>All: mesh divisions between elements
      <li>Full: mesh divisions between regular datapoints
    </ul>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/PlotPoints.html</url>

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
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PlotRange.html</url>

    <dl>
      <dt>'PlotRange'
      <dd>is a charting option, such as for 'Plot', 'BarChart', 'PieChart', \
          etc. that gives the range of coordinates to include in a plot.
    </dl>

    <ul>
      <li>All all points are included.
      <li>Automatic - outlying points are dropped.
      <li>$max$ - explicit limit for each function.
      <li>{$min$, $max$} - explicit limits for $y$ (2D), $z$ (3D), \
          or array values.
      <li>{{$x_{min}$, $x_{max}$}, {{$y_{min}$}, {$y_{max}$}} - explicit limits for \
          $x$ and $y$.
    </ul>

    >> Plot[Sin[Cos[x^2]],{x,-4,4}, PlotRange -> All]
     = -Graphics-

    >> Graphics[Disk[], PlotRange -> {{-.5, .5}, {0, 1.5}}]
     = -Graphics-
    """

    summary_text = "plot option giving the range to be plotted"


class TicksStyle(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TicksStyle.html</url>

    <dl>
      <dt>'TicksStyle'
      <dd>is an option for graphics functions which specifies how ticks should be \
          rendered.
    </dl>

    <ul>
    <li>TicksStyle gives styles for both tick marks and tick labels.
    <li>TicksStyle can be used in both two  and three-dimensional graphics.
    <li>TicksStyle->$list$ specifies the colors of each of the axes.
    </ul>

    >> Graphics[Circle[], Axes-> True, TicksStyle -> {Blue, Red}]
     = -Graphics-
    """

    summary_text = "graph option for the format of tick marks on axes"


class Top(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Top.html</url>

    <dl>
      <dt>'Top'
      <dd>is a possible value for the 'Filling' option.
    </dl>

    >> ListLinePlot[Table[Cos[x], {x, -5, 5, 0.2}], Filling->Top]
      = -Graphics-
    """

    summary_text = "graph option value to fill plot from curve to top"
