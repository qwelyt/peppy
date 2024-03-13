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
    thickness = 3
    with bd.BuildPart() as prt:
        with bd.BuildSketch():
            bd.Rectangle(U(1), U(0.9))
            bd.Rectangle(14, 14, mode=bd.Mode.SUBTRACT)
        bd.extrude(amount=thickness)
        with bd.BuildSketch():
            bd.Rectangle(15, 15)
        bd.extrude(amount=thickness - 1, mode=bd.Mode.SUBTRACT)

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
        map(lambda s: s.moved(bd.Location((size.X * 1 + 0.2, U(0.25), 0))), _col)
    )
    ring = tuple(
        map(
            lambda s: s.rotate(bd.Axis.Z, -5).moved(
                bd.Location((size.X * 2.12, U(-0.2), 2.5))
            ),
            _col,
        )
    )
    pinky = tuple(
        map(
            lambda s: s.rotate(bd.Axis.Z, -10).moved(
                bd.Location((size.X * 3.15, U(-1.1), 5))
            ),
            _col,
        )
    )

    return (index, middle, ring, pinky)


def finger_section(bridges=True):
    _fingers = fingers()
    (index, middle, ring, pinky) = _fingers
    _bridges = (
        [bridge(_fingers[i], _fingers[i + 1]) for i in range(len(_fingers) - 1)]
        if bridges
        else []
    )
    with bd.BuildPart() as prt:
        bd.add(index)
        bd.add(middle)
        bd.add(ring)
        bd.add(pinky)
        for b in _bridges:
            bd.add(b)

    return (
        prt.part,
        index,
        middle,
        ring,
        pinky,
    )


fs = finger_section(True)
print("valid: ", fs[0].is_valid())
show(fs, fs[1][0].faces().sort_by(bd.Axis.X)[0])
# %%


def case(fingers, thumb):
    bridges = [
        bd.loft(
            [
                thumb[0].faces().sort_by(bd.Axis.Z)[-1],
                fingers[1][0].faces().sort_by(bd.Axis.Y)[0],
            ]
        ),
        bd.loft(
            [
                thumb[0].faces().sort_by(bd.Axis.Y)[-1],
                fingers[1][0].faces().sort_by(bd.Axis.X)[0],
            ]
        ),
    ]
    with bd.BuildPart() as prt:
        for f in fingers:
            bd.add(f)
        bd.add(thumb)

    return prt.part


def peppy():
    angle = 30
    thumb = tuple(
        map(
            lambda s: s.rotate(bd.Axis.Z, 115)
            .rotate(bd.Axis.Y, -angle * 2)
            .moved(bd.Location((-U(0.75), -U(2.3), -U(0.65)))),
            _col,
        )
    )
    _finger_section = finger_section()

    def fix(thing):
        if isinstance(thing, tuple) or isinstance(thing, list):
            # print(thing)
            return tuple(map(lambda p: fix(p), thing))
        else:
            # print("lol", thing)
            return thing.rotate(bd.Axis.Y, angle).rotate(bd.Axis.X, 15)

    return tuple(
        map(
            lambda p: fix(p),
            (
                case(_finger_section, thumb),
                _finger_section,
                thumb,
            ),
        )
    )


# %%

part = peppy()
# %%
pbb = part[0].bounding_box()
x = pbb.min.X + pbb.max.X
y = pbb.min.Y + pbb.max.Y
z = pbb.min.Z + pbb.max.Z
loc = bd.Location((-x / 2, -y / 2, -z * 3))
bbbb = bd.loft(
    [
        part[2][0].faces().group_by(bd.Axis.X)[-3].sort_by(bd.Axis.Y)[0],
        part[1][4][0].faces().sort_by(bd.Axis.Y)[0],
    ]
)
b1 = bd.loft(
    [
        part[2][0].faces().sort_by(bd.Axis.Z)[-1],
        part[1][4][0].faces().sort_by(bd.Axis.X)[0],
    ]
)


ee = []
for p in part[2]:
    ee.append(bd.extrude(p.faces().sort_by(bd.Axis.Y)[0], 2))
    ee.append(bd.extrude(p.faces().sort_by(bd.Axis.Y)[-1], 2))
for p in part[1][0]:
    ee.append(bd.extrude(p.faces().sort_by(bd.Axis.X)[0], 2))
for p in part[1][-1]:
    ee.append(bd.extrude(p.faces().sort_by(bd.Axis.X)[-1], 2))

p1 = part[1][-1][0] + ee[7]

ll = [
    bd.loft(
        [
            p1.faces().sort_by(bd.Axis.Y)[0],
            ee[0].faces().sort_by(bd.Axis.X)[4],
        ]
    ),
    bd.loft(
        [
            p1.faces().sort_by(bd.Axis.Y)[0],
            ee[2].faces().sort_by(bd.Axis.X)[4],
        ]
    ),
    bd.loft(
        [
            p1.faces().sort_by(bd.Axis.Y)[0],
            ee[4].faces().sort_by(bd.Axis.X)[4],
        ]
    ),
]


show(
    part[0],
    bd.Rectangle(pbb.size.X, pbb.size.Y)
    .moved(bd.Location(pbb.center()))
    .moved(bd.Location((0, 0, -(10 + pbb.size.Z / 2)))),
    # part[0].project_to_viewport((0,0,50)),
    # ll,
    # ee,
    # render_joints=True
)

# part[0].export_stl(__file__.replace(".py", "wThumb.stl"))
# finger_section()[0].export_stl(__file__.replace(".py", "fingers.stl"))

# %%
