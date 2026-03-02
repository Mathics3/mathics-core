"""
Mathics3 Graphics box rendering to Asymptote Vector graphics strings using
numpy arrays.
"""

from mathics.builtin.box.graphics3d import Polygon3DBox
from mathics.format.render.asy_fns import asy_create_pens


def polygon_3d_box_numpy(box: Polygon3DBox, **options) -> str:

    # FIXME: this is the old code.
    stroke_width = box.style.get_line_width(face_element=True)
    if box.vertex_colors is None:
        face_color = box.face_color
        face_opacity_value = box.face_opacity.opacity if box.face_opacity else None
    else:
        face_color = None
        face_opacity_value = None

    edge_opacity_value = box.edge_opacity.opacity if box.edge_opacity else None
    pen = asy_create_pens(
        edge_color=box.edge_color,
        face_color=face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=stroke_width,
        is_face_element=True,
    )

    asy = "// Polygon3DBox\n"
    for line in box.lines:
        asy += (
            "path3 g="
            + "--".join(["(%.5g,%.5g,%.5g)" % coords.pos()[0] for coords in line])
            + "--cycle;"
        )
        asy += "draw(surface(g), %s);" % (pen)

    # print(asy)
    return asy

    return
