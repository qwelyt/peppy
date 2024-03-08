# %%
from ocp_vscode import (
    show,
    show_object,
    reset_show,
    set_port,
    set_defaults,
    get_defaults,
    Camera,
)

set_port(3939)
set_defaults(reset_camera=Camera.KEEP)

import build123d as bd
import math

choc = bd.import_step("choc.step").rotate(bd.Axis.Z, 90)


# %%
def U(amount):
    return 19 * amount


def switch_holder(with_switch=False):
    thickness = 2
    with bd.BuildPart() as prt:
        with bd.BuildSketch():
            bd.Rectangle(U(1), U(1))
            bd.Rectangle(14, 14, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=thickness)
        with bd.BuildSketch():
            bd.Rectangle(15, 15)
        bd.extrude(amount=thickness - 1, mode=bd.Mode.SUBTRACT)
        edge0 = (
            prt.edges()
            .filter_by(bd.Axis.X)
            .group_by(bd.Axis.Z)[0]
            .sort_by(bd.Axis.Y)[0]
        )
        edge1 = (
            prt.edges()
            .filter_by(bd.Axis.X)
            .group_by(bd.Axis.Z)[0]
            .sort_by(bd.Axis.Y)[-1]
        )
        edge2 = (
            prt.edges()
            .filter_by(bd.Axis.Z)
            .group_by(bd.Axis.X)[-1]
            .sort_by(bd.Axis.Y)[-1]
        )
        vertex0 = prt.vertices().group_by(bd.Axis.Z)[0].sort_by(bd.Axis.Y)[0]
        vertex1 = prt.vertices().group_by(bd.Axis.Z)[0].sort_by(bd.Axis.Y)[-1]

        if with_switch:
            bd.add(choc.moved(bd.Location((0, 0, thickness))))
    return prt.part


def col(angle=30, switch=False):
    holder = switch_holder(with_switch=switch)
    back = holder.rotate(bd.Axis.X, -angle)
    front = holder.rotate(bd.Axis.X, angle)

    back_edge = back.edges().sort_by(bd.Axis.Z)[0]
    front_edge = front.edges().sort_by(bd.Axis.Z)[0]
    mid_back_edge = holder.edges().group_by(bd.Axis.Z)[0].sort_by(bd.Axis.Y)[0]
    mid_front_edge = holder.edges().group_by(bd.Axis.Z)[0].sort_by(bd.Axis.Y)[-1]

    bd.RigidJoint("back", back, bd.Location(back_edge.center()))
    bd.RigidJoint("front", front, bd.Location(front_edge.center()))

    bd.RigidJoint("back", holder, bd.Location(mid_back_edge.center()))
    bd.RigidJoint("front", holder, bd.Location(mid_front_edge.center()))

    holder.joints["back"].connect_to(back.joints["back"])
    holder.joints["front"].connect_to(front.joints["front"])

    return (
        back,
        holder,
        front,
    )


_col = col(switch=False)
c0 = _col[0].edges().sort_by(bd.Axis.Z)[0]
c2 = _col[2].edges().sort_by(bd.Axis.Z)[0]
c1 = _col[1].edges().group_by(bd.Axis.Z)[0].sort_by(bd.Axis.Y)[0]
show(_col[0], _col[1], _col[2], c0, c2, c1, render_joints=True)
# %%


def bridge(left, right):
    bridges = []
    for i in range(len(left)):
        bridges.append(
            bd.loft(
                [
                    left[i].faces().sort_by(bd.Axis.X)[-1],
                    right[i].faces().sort_by(bd.Axis.X)[0],
                ]
            )
        )
    return bridges


def fingers():
    _col = col()
    size = _col[1].bounding_box().size
    index = _col
    middle = tuple(
        map(lambda s: s.moved(bd.Location((size.X * 1.05, U(0.25), 0))), _col)
    )
    ring = tuple(
        map(
            lambda s: s.rotate(bd.Axis.Z, -5).moved(
                bd.Location((size.X * 2.2, U(-0.25), 2.5))
            ),
            _col,
        )
    )
    pinky = tuple(
        map(
            lambda s: s.rotate(bd.Axis.Z, -10).moved(
                bd.Location((size.X * 3.3, U(-1.25), 5))
            ),
            _col,
        )
    )

    return (index, middle, ring, pinky)


def finger_section():
    _fingers = fingers()
    (index, middle, ring, pinky) = _fingers
    bridges = [bridge(_fingers[i], _fingers[i + 1]) for i in range(len(_fingers) - 1)]
    with bd.BuildPart() as prt:
        bd.add(index)
        bd.add(middle)
        bd.add(ring)
        bd.add(pinky)
        for b in bridges:
            bd.add(b)

    return prt.part


def peppy():
    angle = 35
    with bd.BuildPart() as thumb:
        for c in col():
            bd.add(c)
    with bd.BuildPart() as prt:
        bd.add(finger_section())
        bd.add(
            thumb.part.rotate(bd.Axis.Z, 115)
            .rotate(bd.Axis.Y, -angle)
            .moved(bd.Location((-U(1.5), -U(1.5), -U(1))))
        )
    return prt.part.rotate(bd.Axis.Y, angle / 2)


part = peppy()
# %%

fcs = part.faces()

show(
    # part,
    finger_section(),
    # part.faces().sort_by(bd.Axis.X)[10],
    # col(),
    # render_joints=True
)

finger_section().export_stl(__file__.replace(".py", "fingers.stl"))
