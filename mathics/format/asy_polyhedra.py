"""
Functions to draw regular polyhdra in Asymptote vector graphics
"""

from typing import Callable, Dict


def dodecahedron(center: tuple, length: float, color_str: str) -> str:
    """
    Return an asymptote program string to draw a dodecahedron at `center`
    with length `length`.
    """
    return f"""
    real phi=(sqrt(5)+1)/2;
    real g=(phi-1)/2;
    real s=1/2;
    real a=sqrt(1-phi*phi/4-g*g)+phi/2;

    triple center={center};
    real length={length};
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
    "dodecahedron": dodecahedron,
    "tetrahedron": tetrahedron,
}
