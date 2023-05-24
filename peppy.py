import build123d as b3d
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


def col(thing, rotate=True):
    y = 16.8
    if rotate:
        y = 16.8
        z = 4.5
        angle = 30
        return (thing
           , thing.rotate((0,0,0),(1,0,0),angle).translate((0,y,z))
           , thing.rotate((0,0,0),(1,0,0),-angle).translate((0,-y,z))
          )
    return (thing
            , thing.translate((0,y,0))
            , thing.translate((0,-y,0))
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

def block(w=U(1),l=U(1),h=moduleZ):
    return (cq.Workplane()
            .sketch()
            .rect(l,w)
            .finalize()
            .extrude(h)
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

def col_placements():
    def index(c):
        return c.translate((next_col*0,0,0))
    def middle(c):
        return c.translate((next_col*1,U(0.25),0))
    def ring(c):
        return c.rotate((0,0,0),(0,0,1),-3).translate((next_col*2.05,0,0))
    def pinky(c):
        return c.rotate((0,0,0),(0,0,1),-10).translate((next_col*3.2,-U(0.5),0))
    return (index, middle, ring, pinky)

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


    m = col_placements()
    index = m[0](solid_col)#(solid_col.translate((next_col*0,0,0))) 
    middle = m[1](solid_col)#(solid_col.translate((next_col*1,U(0.25),0)))
    r = tuple(map(lambda w: m[2](w), c))
    p = tuple(map(lambda w: m[3](w), c))

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
    b = block(U(1)+10, U(1)+10)
    _col = col(b, False)
    cp = col_placements()
    solid = reduce(lambda a,b: a+b, _col)
    sbb = solid.findSolid().BoundingBox()
    base = cq.Workplane()
    for m in cp:
        base = base + m(solid)
    w = (cq.Workplane()
         .sketch()
         .rect(5, sbb.ylen)
         .finalize()
         .extrude(35)
         )
    w2 = (cq.Workplane()
         .sketch()
         .rect(5, sbb.ylen)
         .finalize()
         .extrude(23)
         )
    wbb = w.findSolid().BoundingBox()
    w2 = cp[3](w2.translate((sbb.xlen/2-wbb.xlen/2.5,0,0)))
    w = w.translate((-sbb.xlen/2+wbb.xlen/2.5,0,0))
    return (base+w+w2).fillet(1)

    
f = (fingers(choc_holder()))
#fbb = f.findSolid().BoundingBox()
#f = f.translate((-fbb.xmax/3-5,5/2,20))
#show_object(f)
fm = (f.translate((-4,0,20)).rotate((0,0,0),(0,1,0),10))
fb = (finger_body())
fb = fb - fm - fm.translate((-0.2,0,-1))- fm.translate((0,0,0.5))
show_object(fm)
show_object(fb)

#show_object(reduce(lambda a,b: a+b, col(choc_holder(False), False)))
