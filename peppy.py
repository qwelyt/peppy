import cadquery as cq
#from cq_server.ui import ui, show_object, debug

#module chocCut(){
#  union(){
#    cube([14,14,moduleZ*2],center=true);
#    translate([0,14/4,-1])cube([15,4,moduleZ],center=true);
#    translate([0,-14/4,-1])cube([15,4,moduleZ],center=true);
#  }
#}

def row(thing):
    return (thing
       + thing.rotate((0,0,0),(1,0,0),40).translate((0,16,5.85))
       + thing.rotate((0,0,0),(1,0,0),-40).translate((0,-16,5.85))
      )

s = 18.2
c = s-2
wp = (cq.Workplane('XY')
        .sketch()
        .rect(c,s)
        .rect(13.9,13.9, mode='s')
        .finalize()
        .extrude(3)
        .faces("<Z")
        .workplane()
        .sketch()
        .push([(0, -14/2),(0,14/2)])
        .rect(13.5,2)
        .finalize()
        .extrude(-1.7, "cut")
        )
choc = (cq.importers.importStep('choc.step')
              .rotate((0,0,0),(1,0,0),90)
              .translate((0,0,3.5))
        )

bit = wp +choc

#show_object(wp)
#show_object(choc)#, options="{'color':(100,100,100)}")
r = row(wp)
index = r.translate((-s,-s/4,0))
long = r
ring = r.translate((s,-s/2,0))
pinky = r.translate((s*2,-s,0))
thumb = (r.rotate((0,0,0),(1,0,0),80)
        .rotate((0,0,0),(0,0,1),-70)
        .translate((-s*2,-s*1.2,-s))
        )

il = cq.Solid.makeLoft([
    index.faces(">X").val().outerWire(),
    long.faces("<X").val().outerWire(),
    ])

lr = cq.Solid.makeLoft([
    long.faces(">X").val().outerWire(),
    ring.faces("<X").val().outerWire(),
    ])
rp = cq.Solid.makeLoft([
    ring.faces(">X").val().outerWire(),
    pinky.faces("<X").val().outerWire(),
    ])


#show_object(index.faces(">YZ"), options={"color":(0,1,0)})#, name="itz")
#show_object(cq.Workplane().add(il).faces(">YZ"), options={"color":(0,1,0)})

mm = cq.Solid.makeLoft([
    index.faces(">YZ").val().outerWire(),
    cq.Workplane().add(il).faces(">YZ").val().outerWire(),
    ])
#show_object(mm)



module = ( index
        + long
        + ring
        + pinky
#        + thumb
        +cq.Workplane().add(il).add(lr).add(rp)
        ).add(mm)
show_object(module)
#show_object(cq.Workplane().add(il).add(lr).add(rp))#, options={"color":(1,1,0)})
#show_object(index)
#show_object(thumb)
#show_object(index.faces("<X"), options={"color":(0,1,0)})
#show_object(thumb.faces("<<Z[5]"), options={"color":(0,1,0)})
#a = r.translate((s,0,0))
#b = r.rotate((0,0,0),(0,0,1),6).translate((-s,-s,0))
#tb = (a.faces("<X").val().outerWire())
#tc = (b.faces(">X").val().outerWire())
#td = [tb, tc]
#show_object(a+b)
#show_object(cq.Solid.makeLoft(td), options={"color":(0,0,1)})
#b1 = cq.Workplane().copyWorkplane(tb).box(s,1.5,10).translate((0,0,s/2))
#show_object(b)

#show_object(bit.rotate((0,0,0),(1,0,0),40).translate((0,16,5.85)))
#show_object(bit.rotate((0,0,0),(1,0,0),-40).translate((0,-16,5.85)))
