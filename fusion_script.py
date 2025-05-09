import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        
        # Parameters from params.json
        cone_height = 50
        cone_base_diameter = 25
        torus_inner_diameter = 15
        torus_thickness = 5
        
        # Create cone
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circle = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            cone_base_diameter/2
        )
        lines = sketch.sketchCurves.sketchLines
        line = lines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(0, 0, cone_height)
        )
        revolveAxis = sketch.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(0, 0, cone_height)
        )
        prof = sketch.profiles.item(1) # The profile around the revolve axis
        revolves = rootComp.features.revolveFeatures
        revInput = revolves.createInput(
            prof,
            revolveAxis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        angle = adsk.core.ValueInput.createByReal(2*3.14159)
        revInput.setAngleExtent(False, angle)
        cone = revolves.add(revInput)
        
        # Create torus
        torus_major_radius = torus_inner_diameter/2 + torus_thickness/2
        torus_minor_radius = torus_thickness/2
        torus_center_z = cone_height/2
        
        torusSketch = sketches.add(rootComp.xZConstructionPlane)
        torusSketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(torus_major_radius, 0, torus_center_z),
            torus_minor_radius
        )
        torusProf = torusSketch.profiles.item(0)
        torusRevolveAxis = torusSketch.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, torus_center_z),
            adsk.core.Point3D.create(0, 10, torus_center_z)
        )
        torusRevInput = revolves.createInput(
            torusProf,
            torusRevolveAxis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        torusRevInput.setAngleExtent(False, angle)
        torus = revolves.add(torusRevInput)
        
    except:
        if app:
            app.userInterface.messageBox(
                'Failed:\n{}'.format(traceback.format_exc())
            )