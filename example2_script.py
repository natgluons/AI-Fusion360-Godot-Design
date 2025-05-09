import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        
        # Parameters from params.json
        cylinder_diameter = 30
        cylinder_height = 50
        sphere_diameter = 20
        
        # Create cylinder
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        circles = sketch.sketchCurves.sketchCircles
        circle = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),
            cylinder_diameter/2
        )
        prof = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(cylinder_height)
        extInput.setDistanceExtent(False, distance)
        cylinder = extrudes.add(extInput)
        
        # Create sphere on top
        sphere_radius = sphere_diameter/2
        sphere_center = adsk.core.Point3D.create(
            0, 0, cylinder_height + sphere_radius
        )
        spheres = rootComp.features.sphereFeatures
        sphereInput = spheres.createInput(
            adsk.core.ValueInput.createByReal(sphere_radius),
            sphere_center
        )
        spheres.add(sphereInput)
        
    except:
        if app:
            app.userInterface.messageBox(
                'Failed:\n{}'.format(traceback.format_exc())
            )
