from mathics.builtin.box.graphics3d import Coords3D

from mathics.builtin.base import BoxConstructError

from mathics.builtin.colors.color_directives import _ColorObject, Opacity
from mathics.builtin.drawing.graphics_internals import GLOBALS3D, _GraphicsElementBox

import numbers
from mathics.core.symbols import Symbol


class UniformPolyhedron3DBox(_GraphicsElementBox):
    # Let's overwrite the default summary_text here,
    # to recover the spaces.
    summary_text = "box representation of a 3d uniform polyhedron"

    def init(self, graphics, style, item):
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )

        if len(item.elements) != 3:
            raise BoxConstructError

        points = item.elements[1].to_python()
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxConstructError

        self.points = tuple(Coords3D(pos=point) for point in points)
        self.edge_length = item.elements[2].to_python()
        self.sub_type = item.elements[0].to_python(string_quotes=False)

    def extent(self):
        result = []

        # TODO: correct extent calculation, the current one is approximated
        result.extend(
            [
                coords.add(self.edge_length, self.edge_length, self.edge_length).pos()[
                    0
                ]
                for coords in self.points
            ]
        )
        result.extend(
            [
                coords.add(
                    -self.edge_length, -self.edge_length, -self.edge_length
                ).pos()[0]
                for coords in self.points
            ]
        )
        return result

    def _apply_boxscaling(self, boxscale):
        # No box scaling for now
        return


# FIXME: GLOBALS3D is a horrible name.
GLOBALS3D.update(
    {
        Symbol("System`UniformPolyhedron3DBox"): UniformPolyhedron3DBox,
    }
)
