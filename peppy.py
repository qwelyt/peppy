import cadquery as cq
from functools import reduce
from copy import copy, deepcopy
def U(amount):
    return 19 * amount

# https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf
choc_skirtXY = (15+2.5,15+1.5)
choc_bottomXY = (13.6, 13.6)
choc_bottom_hooks = (choc_bottomXY[0],14.5+1)
choc_skirt_to_hooks = 0.8+0.1
moduleZ = 3
next_col = choc_skirtXY[0]+0.5


def col(thing):
    y = 16.8
    z = 4.5
    angle = 30
    return (thing
       , thing.rotate((0,0,0),(1,0,0),angle).translate((0,y,z))
       , thing.rotate((0,0,0),(1,0,0),-angle).translate((0,-y,z))
      )
def choc():
    return (cq.importers.importStep('choc.step')
              .rotate((0,0,0),(0,0,1),90)
              .translate((0,0,3.1))
            )

def choc_holder(cut=True, switch=None):
    top = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1])
    bottom = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1]+1.55)
    ret = cq.Workplane()
    if switch is not None:
        ret.add(switch)

    base = (cq.Workplane()
            .placeSketch(bottom, top.moved(cq.Location(cq.Vector(0,0,moduleZ))))
            .loft()
            )
    if not cut:
        return ret.add(base)

    return ret.add(base
            .sketch()
            .rect(choc_bottomXY[0], choc_bottomXY[1])
            .finalize()
            .cutThruAll()
            .faces("<Z")
            .workplane()
            .sketch()
            .rect(choc_bottom_hooks[0], choc_bottom_hooks[1])
            .finalize()
            .extrude(-(moduleZ-choc_skirt_to_hooks), "cut")
            )

def block(w):
    top = cq.Sketch().rect(w, choc_skirtXY[1])
    bottom = cq.Sketch().rect(w, choc_skirtXY[1]+1.55)
    return (cq.Workplane()
            .placeSketch(bottom, top.moved(cq.Location(cq.Vector(0,0,moduleZ))))
            .loft()
            )

def _bridge(left,right):
    a = cq.Workplane().add(left).faces(">X").val().outerWire()
    b = cq.Workplane().add(right).faces("<X").val().outerWire()
    return cq.Workplane().add(cq.Solid.makeLoft([a,b]))

def bridge(left,right):
    if (isinstance(left, tuple) or isinstance(left, list)) and (isinstance(right, tuple) or isinstance(right, list)):
        if len(left) != len(right):
            raise Exception("The things you want to join must be of the same length")
        r = cq.Workplane()
        for i in range(len(left)):
            a = left[i]#.faces(">X").val().outerWire()
            b = right[i]#.faces("<X").val().outerWire()
            r.add(_bridge(a,b))

        return r

    return _bridge(left,right)

def fingers(part):
    _col = col(part)
    front=(lambda t: t.faces(">Y")
          .workplane(centerOption="CenterOfMass")
          .transformed(rotate=cq.Vector(45,0,0))
          .rect(choc_skirtXY[0],moduleZ-0.8)
      )
    back=(lambda t: t.faces("<Y")
          .workplane(centerOption="CenterOfMass")
          .transformed(rotate=cq.Vector(45,0,0))
          .rect(choc_skirtXY[0],moduleZ-0.8)
      )
    c1 = (front(_col[1]).extrude(-1.1)
          + front(_col[1]).extrude(5)
          )
    c2 = (back(_col[2]).extrude(-1.1)
          + back(_col[2]).extrude(5)
          )

    solid_col = (_col[0]+_col[1]+_col[2]+c1+c2)
    c = (_col[0],_col[1],_col[2],c1,c2)

    index = (solid_col.translate((next_col*0,0,0)))
    middle = (solid_col.translate((next_col*1,U(0.25),0)))
    r = tuple(map(lambda w: w.rotate((0,0,0),(0,0,1),-3).translate((next_col*2.05,0,0)), c))
    p = tuple(map(lambda w: w.rotate((0,0,0),(0,0,1),-10).translate((next_col*3.2,-U(0.5),0)), c))

    ring = reduce(lambda a,b: a+b, r)
    pinky = reduce(lambda a,b: a+b, p)

    im = bridge(index, middle)
    mr = bridge(middle, ring)
    rp = bridge(r,p)

    left = (index.faces("<X").val().thicken(5))
    right = (pinky.faces("<<X[1]").val().thicken(5))

    return (index + middle + ring + pinky
            + im + mr + rp
            + left + right
            ).clean()

def finger_body():
    _fingers = fingers()
    show_object(_fingers)
    b = block(1)
    #c = col(block(1))
    fbb = _fingers.findSolid().BoundingBox()
    debug(_fingers.faces("<Y or <<X[1]"))
    #r = _fingers.faces("<X").val().thicken(5)
    #l = _fingers.faces("<<X[1]").val().thicken(5)
    #b = _fingers.faces("<Y").val().thicken(5)
    #show_object(r)
    #show_object(l)
    #show_object(b)

#c = col(choc_holder(False))
#cc = reduce(lambda a,b: a+b, c)
#p=(lambda t: t.faces(">Y")
#      .workplane(centerOption="CenterOfMass")
#      .transformed(rotate=cq.Vector(45,0,0))
#      .rect(choc_skirtXY[0],moduleZ-0.8)
#  )
#debug(p(cc).extrude(-1.1))
#debug(p(cc).extrude(5))
#show_object(cc)
f = (fingers(choc_holder()))
show_object(f)
#debug(f.wires().toPending().extrude(2))
#finger_body()
#ch = choc_holder().rotate((0,0,0),(1,0,0),-40)
#chrot = ch.rotate((0,0,0),(0,0,1),-10).translate((next_col*1.6,-10,0))
#b = bridge(ch,chrot)
#show_object(ch)
#show_object(chrot)
#debug(b)
