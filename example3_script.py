import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent
        
        # Parameters from params.json
        width = 60
        depth = 40
        height = 20
        holes = [
            {"diameter": 10, "x": -15, "y": 0},
            {"diameter": 10, "x": 15, "y": 0}
        ]
        
        # Create base block
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        rect = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-width/2, -depth/2, 0),
            adsk.core.Point3D.create(width/2, depth/2, 0)
        )
        prof = sketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(height)
        extInput.setDistanceExtent(False, distance)
        block = extrudes.add(extInput)
        
        # Create holes
        topFace = block.endFaces[0]
        holeSketch = sketches.add(topFace)
        for hole in holes:
            holeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(hole["x"], hole["y"], 0),
                hole["diameter"]/2
            )
        
        for i in range(len(holes)):
            prof = holeSketch.profiles.item(i)
            holeInput = extrudes.createInput(
                prof,
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            holeInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
            extrudes.add(holeInput)
            
    except:
        if app:
            app.userInterface.messageBox(
                'Failed:\n{}'.format(traceback.format_exc())
            )
