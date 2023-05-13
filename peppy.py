import cadquery as cq

# https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf
choc_skirtXY = (15+2,15+2)
choc_bottomXY = (13.8, 13.8)
choc_bottom_hooks = (14.5+1,14.5+1)
choc_skirt_to_hooks = 0.8+0.1
moduleZ = 3

def col(thing):
    y = 16.09
    z = 5.85
    return (thing
       + thing.rotate((0,0,0),(1,0,0),40).translate((0,y,z))
       + thing.rotate((0,0,0),(1,0,0),-40).translate((0,-y,z))
      )

def wp():
    top = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1])
    bottom = cq.Sketch().rect(choc_skirtXY[0], choc_skirtXY[1]+1.22)
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
            )

   #   .faces("<Z")
   #   .workplane()
   #   .sketch()
   #   .rect(choc_bottom_hooks[0],choc_bottom_hooks[1])
   #   .finalize()
   #   .extrude(-(moduleZ-choc_skirt_to_hooks), "cut")
   #   )

#show_object(wp())
show_object(col(wp()))

s = 24
def poly():
    return (cq.Workplane()
            .polygon(6,s)
            .extrude(19)
            .faces(">Z")
            .polygon(6,s-3)
            .cutThruAll()
            .faces(">Y")
            .workplane()
            .rect(100,100)
            .extrude(-s/2.31, "cut")
            )

#show_object(poly())
