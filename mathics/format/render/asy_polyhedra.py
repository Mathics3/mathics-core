"""
Functions to draw regular polyhedra in Asymptote vector graphics
"""

# FIXME: All of these regular polyhedra routine could be table driven
# by putting edge points, and paths into a table.
# The same is also true on the in the mathics-threejs-backend code.

from typing import Callable, Dict


def cube(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a cube at `center`
    with length `length`.
    """
    return f"""
    real length={length};

    triple center={center};
    real unit_corner = sqrt(3) / 4;
    triple[] d;
    d[0]=center + length*(unit_corner,unit_corner,unit_corner);
    d[1]=center + length*(unit_corner,-unit_corner,unit_corner);
    d[2]=center + length*(-unit_corner,-unit_corner,unit_corner);
    d[3]=center + length*(-unit_corner,unit_corner,unit_corner);
    d[4]=center + length*(-unit_corner,unit_corner,-unit_corner);
    d[5]=center + length*(-unit_corner,-unit_corner,-unit_corner);
    d[6]=center + length*(unit_corner,-unit_corner,-unit_corner);
    d[7]=center + length*(unit_corner,unit_corner,-unit_corner);

    path3[] p;
    p[0]=d[0]--d[1]--d[2]--d[3]--cycle;
    p[1]=d[0]--d[3]--d[4]--d[7]--cycle;
    p[2]=d[0]--d[1]--d[6]--d[7]--cycle;
    p[3]=d[3]--d[4]--d[5]--d[2]--cycle;
    p[4]=d[7]--d[6]--d[5]--d[4]--cycle;
    p[5]=d[1]--d[2]--d[5]--d[6]--cycle;

    pen sides={color_str};

    draw(surface(p[0]),sides);
    draw(surface(p[1]),sides);
    draw(surface(p[2]),sides);
    draw(surface(p[3]),sides);
    draw(surface(p[4]),sides);
    draw(surface(p[5]),sides);
    """


def dodecahedron(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a dodecahedron at `center`
    with edge length `length`.
    """
    return f"""
    real phi=(sqrt(5)+1)/2;
    real g=(phi-1)/2;
    real s=1/2;
    real a=sqrt(1-phi*phi/4-g*g)+phi/2;

    triple center={center};
    real length={length} / 2;
    triple[] d;
    d[0]=center + length*(phi/2,phi/2,phi/2);
    d[1]=center + length*(-phi/2,phi/2,phi/2);
    d[2]=center + length*(phi/2,-phi/2,phi/2);
    d[3]=center + length*(phi/2,phi/2,-phi/2);
    d[4]=center + length*(-phi/2,-phi/2,phi/2);
    d[5]=center + length*(phi/2,-phi/2,-phi/2);
    d[6]=center + length*(-phi/2,phi/2,-phi/2);
    d[7]=center + length*(-phi/2,-phi/2,-phi/2);

    triple[] n;
    n[0]=center + length*(0,s,a);
    n[1]=center + length*(0,-s,a);
    n[2]=center + length*(0,s,-a);
    n[3]=center + length*(0,-s,-a);
    n[4]=center + length*(s,a,0);
    n[5]=center + length*(-s,a,0);
    n[6]=center + length*(s,-a,0);
    n[7]=center + length*(-s,-a,0);
    n[8]=center + length*(a,0,s);
    n[9]=center + length*(a,0,-s);
    n[10]=center + length*(-a,0,s);
    n[11]=center + length*(-a,0,-s);

    path3[] p;
    p[0]=d[0]--n[0]--d[1]--n[5]--n[4]--cycle;
    p[1]=n[0]--n[1]--d[2]--n[8]--d[0]--cycle;
    p[2]=n[0]--n[1]--d[4]--n[10]--d[1]--cycle;
    p[3]=d[0]--n[4]--d[3]--n[9]--n[8]--cycle;
    p[4]=d[3]--n[4]--n[5]--d[6]--n[2]--cycle;
    p[5]=d[6]--n[5]--d[1]--n[10]--n[11]--cycle;
    p[6]=n[8]--n[9]--d[5]--n[6]--d[2]--cycle;
    p[7]=n[10]--n[11]--d[7]--n[7]--d[4]--cycle;
    p[8]=d[7]--n[11]--d[6]--n[2]--n[3]--cycle;
    p[9]=n[3]--n[2]--d[3]--n[9]--d[5]--cycle;
    p[10]=d[7]--n[7]--n[6]--d[5]--n[3]--cycle;
    p[11]=n[6]--d[2]--n[1]--d[4]--n[7]--cycle;

    pen sides={color_str};

    draw(surface(p[0]),sides);
    draw(surface(p[1]),sides);
    draw(surface(p[2]),sides);
    draw(surface(p[3]),sides);
    draw(surface(p[4]),sides);
    draw(surface(p[5]),sides);
    draw(surface(p[6]),sides);
    draw(surface(p[7]),sides);
    draw(surface(p[8]),sides);
    draw(surface(p[9]),sides);
    draw(surface(p[10]),sides);
    draw(surface(p[11]),sides);
    """


# Loosely based on mathics-threejs-backend/src/primitives/uniformPolyhedron.js
def icosahedron(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a icosahedron at `center`
    with edge length `length`.
    """
    return f"""
    real v0 = 0.5576 * {length};
    real v1 = 0.9022 * {length};

    triple center={center};
    triple[] d;
    d[0]=center + (v0, v1, 0);
    d[1]=center + (0, v0, v1);
    d[2]=center + (-v0, v1, 0);
    d[3]=center + (-v1, 0, -v0);
    d[4]=center + (-v1, 0, v0);
    d[5]=center + (0, v0, -v1);
    d[6]=center + (0, -v0, -v1);
    d[7]=center + (-v0, -v1, 0);
    d[8]=center + (v0, -v1, 0);
    d[9]=center + (0, -v0, v1);
    d[10]=center + (v1, 0, v0);
    d[11]=center + (v1, 0, -v0);

    path3[] p;
    p[0]=d[0]--d[1]--d[2]--cycle;
    p[1]=d[2]--d[1]--d[4]--cycle;
    p[2]=d[2]--d[4]--d[3]--cycle;
    p[3]=d[0]--d[2]--d[5]--cycle;
    p[4]=d[2]--d[5]--d[3]--cycle;
    p[5]=d[3]--d[5]--d[6]--cycle;
    p[6]=d[3]--d[6]--d[7]--cycle;
    p[7]=d[3]--d[4]--d[7]--cycle;
    p[8]=d[1]--d[4]--d[9]--cycle;
    p[9]=d[4]--d[7]--d[9]--cycle;
    p[10]=d[0]--d[1]--d[10]--cycle;
    p[11]=d[1]--d[9]--d[10]--cycle;
    p[12]=d[7]--d[8]--d[9]--cycle;
    p[13]=d[8]--d[9]--d[10]--cycle;
    p[14]=d[6]--d[7]--d[8]--cycle;
    p[15]=d[0]--d[5]--d[11]--cycle;
    p[16]=d[0]--d[10]--d[11]--cycle;
    p[17]=d[8]--d[10]--d[11]--cycle;
    p[18]=d[5]--d[6]--d[11]--cycle;
    p[19]=d[6]--d[8]--d[11]--cycle;

    pen sides={color_str};

    // dot(d[0]); label("0", d[0]);
    // dot(d[1]); label("1", d[1]);
    // dot(d[2]); label("2", d[2]);
    // dot(d[3]); label("3", d[3]);
    // dot(d[4]); label("4", d[4]);
    // dot(d[5]); label("5", d[5]);
    // dot(d[6]); label("6", d[6]);
    // dot(d[7]); label("7", d[7]);
    // dot(d[8]); label("8", d[8]);
    // dot(d[9]); label("9", d[9]);
    // dot(d[10]); label("10", d[10]);
    // dot(d[11]); label("11", d[11]);

    draw(surface(p[0]),sides);
    draw(surface(p[1]),sides);
    draw(surface(p[2]),sides);
    draw(surface(p[3]),sides);
    draw(surface(p[4]),sides);
    draw(surface(p[5]),sides);
    draw(surface(p[6]),sides);
    draw(surface(p[7]),sides);
    draw(surface(p[8]),sides);
    draw(surface(p[9]),sides);
    draw(surface(p[10]),sides);
    draw(surface(p[11]),sides);
    draw(surface(p[12]),sides);
    draw(surface(p[13]),sides);
    draw(surface(p[14]),sides);
    draw(surface(p[15]),sides);
    draw(surface(p[16]),sides);
    draw(surface(p[17]),sides);
    draw(surface(p[18]),sides);
    draw(surface(p[19]),sides);
    """


def octahedron(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a tetrahedron at `center`
    with edge length `length`.
    """
    return f"""
    triple center={center};
    real vertex_position = 0.30615 * {length};

    triple[] d;
    path3[] p;

    d[0]=center + (0, vertex_position, 0);
    d[1]=center + (0, 0, vertex_position);
    d[2]=center + (-vertex_position, 0, 0);
    d[3]=center + (0, 0, -vertex_position);
    d[4]=center + (vertex_position, 0, 0);
    d[5]=center + (0, -vertex_position, 0);

    p[0]=d[0]--d[1]--d[2]--cycle;
    p[1]=d[0]--d[2]--d[3]--cycle;
    p[2]=d[0]--d[3]--d[4]--cycle;
    p[3]=d[0]--d[4]--d[1]--cycle;

    p[4]=d[5]--d[1]--d[2]--cycle;
    p[5]=d[5]--d[2]--d[3]--cycle;
    p[6]=d[5]--d[3]--d[4]--cycle;
    p[7]=d[5]--d[4]--d[1]--cycle;

    pen sides={color_str};

    draw(surface(p[0]),sides);
    draw(surface(p[1]),sides);
    draw(surface(p[2]),sides);
    draw(surface(p[3]),sides);
    draw(surface(p[4]),sides);
    draw(surface(p[5]),sides);
    draw(surface(p[6]),sides);
    draw(surface(p[7]),sides);
    """


def tetrahedron(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a tetrahedron at `center`
    with length `length`.
    """
    return f"""
    triple center={center};
    real vertex_position = 0.30615 * {length};

    triple[] d;
    path3[] p;

    d[0]=center + (vertex_position, vertex_position, vertex_position);
    d[1]=center + (vertex_position, -vertex_position, -vertex_position);
    d[2]=center + (-vertex_position, vertex_position, -vertex_position);
    d[3]=center + (-vertex_position, -vertex_position, vertex_position);
    p[0]=d[0]--d[1]--d[2]--cycle;
    p[1]=d[0]--d[2]--d[3]--cycle;
    p[2]=d[0]--d[1]--d[3]--cycle;
    p[3]=d[1]--d[2]--d[3]--cycle;

    pen sides={color_str};

    draw(surface(p[0]),sides);
    draw(surface(p[1]),sides);
    draw(surface(p[2]),sides);
    draw(surface(p[3]),sides);
    """


def unimplimented_polygon(center: tuple, length: float, color_str: str) -> str:
    return f"draw(surface(sphere({center}, {length})), {color_str});"


HEDRON_NAME_MAP: Dict[str, Callable] = {
    "cube": cube,
    "dodecahedron": dodecahedron,
    "icosahedron": icosahedron,
    "octahedron": octahedron,
    "tetrahedron": tetrahedron,
}
