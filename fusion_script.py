import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # Load parameters
        import json
        with open('params.json', 'r') as f:
            params = json.load(f)

        # Example: use params
        width = 30
        height = 30
        depth = 30

        # Your Fusion modeling code here
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        rootComp = design.rootComponent

        # Create a new sketch on the xy plane
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        sketchCircles = sketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        sketchCircles.addByCenterRadius(centerPoint, 5.0)

        # Get the profile defined by the circle
        profiles = sketch.profiles
        profile = profiles.item(0)

        # Create an extrusion input to be able to define the input needed for the extrusion
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define the distance of the extrusion
        distance = adsk.core.ValueInput.createByReal(height)

        # Define that the extent is a distance extent of 10 mm
        extInput.setDistanceExtent(True, distance)

        # Create the extrusion
        extrude = extrudes.add(extInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
