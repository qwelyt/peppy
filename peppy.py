import cadquery as cq
def U(amount):
    return 19 * amount

# https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf
choc_skirtXY = (15+2.5,15+2)
choc_bottomXY = (13.6, 13.6)
choc_bottom_hooks = (choc_bottomXY[0],14.5+1)
choc_skirt_to_hooks = 0.8+0.1
moduleZ = 3
next_col = choc_skirtXY[0]+0.5


def col(thing):
    y = 17.3
    z = 4.64
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

def choc_holder():
    switch = choc()
    top = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1])
    bottom = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1]+1.55)
    return (cq.Workplane()
            .placeSketch(bottom, top.moved(cq.Location(cq.Vector(0,0,moduleZ))))
            .loft()
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
            )#+switch

def bridge(left,right):
    a = left.faces(">X").val().outerWire()
    b = right.faces("<X").val().outerWire()
    return cq.Solid.makeLoft([a,b])

def fingers():
    _col = col(choc_holder())

    solid_col = (_col[0]+_col[1]+_col[2])

    index = (solid_col.translate((next_col*0,0,0)))
    middle = (solid_col.translate((next_col*1,U(0.25),0)))
    r = tuple(map(lambda w: w.rotate((0,0,0),(0,0,1),-3).translate((next_col*2.05,0,0)), _col))
    p = tuple(map(lambda w: w.rotate((0,0,0),(0,0,1),-10).translate((next_col*3.2,-U(0.5),0)), _col))

    ring = r[0]+r[1]+r[2]
    pinky = p[0]+p[1]+p[2]

    b0 = bridge(r[0],p[0])
    b1 = bridge(r[1],p[1])
    b2 = bridge(r[2],p[2])
    rp = cq.Workplane()+b0+b1+b2

    im = bridge(index, middle)
    mr = bridge(middle, ring)
    #rp = bridge(ring,pinky)

    return (index + middle + ring + pinky
            + im + mr + rp
            )


#c = col(choc_holder())
#show_object(c[0]+c[1]+c[2])
show_object(fingers())
#ch = choc_holder().rotate((0,0,0),(1,0,0),-40)
#chrot = ch.rotate((0,0,0),(0,0,1),-10).translate((next_col*1.6,-10,0))
#b = bridge(ch,chrot)
#show_object(ch)
#show_object(chrot)
#debug(b)
