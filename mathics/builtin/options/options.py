"""
Individual Options
"""

from mathics.core.builtin import Predefined


class Automatic(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Automatic.html</url>

    <dl>
      <dt>'Automatic'
      <dd>is used to specify an automatically computed option value.
    </dl>

    'Automatic' is the default for 'PlotRange', 'ImageSize', and other
    graphical options:

    >> Cases[Options[Plot], HoldPattern[_ -> Automatic]]
     = {AxesOrigin ⇾ Automatic, Background ⇾ Automatic, BaselinePosition ⇾ Automatic, ContentSelectable ⇾ Automatic, CoordinatesToolOptions ⇾ Automatic, Exclusions ⇾ Automatic, FrameTicks ⇾ Automatic, ImageSize ⇾ Automatic, Method ⇾ Automatic, PlotRange ⇾ Automatic, PlotRangePadding ⇾ Automatic, PlotRegion ⇾ Automatic, PreserveImageOptions ⇾ Automatic, Ticks ⇾ Automatic}
    """

    summary_text = "option value to choose parameters automatically"
