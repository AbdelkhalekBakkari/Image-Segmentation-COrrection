from __main__ import vtk, qt, ctk, slicer
import vtkSegmentationCorePython as vtkSegmentationCore
import os
#
# CSISegCor
# Cubic Spline Image Segmentation Correction
class CSISegCor:

    def __init__(self, parent):

        parent.title = "Cubic Spline Image Segmentation Correction"
        parent.categories = ["Exemple"]
        parent.dependencies = []
        parent.contributors = [" Abdelkhalek Bakkari ", "Dhifli Mohamed "]

class CSISegCorWidget:

    def __init__(self, parent=None):

        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()


    def setup(self):

        self.__clippingModelNode = None
        self.__clippingMarkupNode = None
        self.__clippingMarkupNodeObserver = None

        self.toFids = slicer.vtkMRMLMarkupsFiducialNode()
        self.fromFids = slicer.vtkMRMLMarkupsFiducialNode()
        self.toFids.SetName('toFids')
        self.fromFids.SetName('fromFids')
        slicer.mrmlScene.AddNode(self.toFids)
        slicer.mrmlScene.AddNode(self.fromFids)
        self.__markupList = []
        # create a callapsible button
        collapsibleButton = ctk.ctkCollapsibleButton()
        collapsibleButton.text = "Cubic Spline Image Segmentation Correction"

        # bind collapsibleButton to root Layout
        self.layout.addWidget(collapsibleButton)

        # new layout for collapsible button
        self.formLayout = qt.QFormLayout(collapsibleButton)

        # volume selector
        self.formFrame = qt.QFrame(collapsibleButton)
        self.formFrame1 = qt.QFrame(collapsibleButton)
        self.formFrame4 = qt.QFrame(collapsibleButton)
        self.formFrame2 = qt.QFrame(collapsibleButton)
        self.formFrame5 = qt.QFrame(collapsibleButton)
        self.formFrame3 = qt.QFrame(collapsibleButton)

        # set a layout to horizontal
        self.formFrame.setLayout(qt.QHBoxLayout())
        self.formFrame1.setLayout(qt.QHBoxLayout())
        self.formFrame4.setLayout(qt.QHBoxLayout())
        self.formFrame2.setLayout(qt.QHBoxLayout())
        self.formFrame5.setLayout(qt.QHBoxLayout())
        self.formFrame3.setLayout(qt.QHBoxLayout())

        # bind a new frame to existing layout in collapsible menu
        self.formLayout.addWidget(self.formFrame)
        self.formLayout.addWidget(self.formFrame1)
        self.formLayout.addWidget(self.formFrame4)
        self.formLayout.addWidget(self.formFrame2)
        self.formLayout.addWidget(self.formFrame5)
        self.formLayout.addWidget(self.formFrame3)

        # creating new volume selector
        self.inputSelector = qt.QLabel("Input Volume: ", self.formFrame)
        self.formFrame.layout().addWidget(self.inputSelector)
        self.inputSelector = slicer.qMRMLNodeComboBox(self.formFrame)
        self.inputSelector.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False

        self.inputSelector1 = qt.QLabel("Input segmentation: ", self.formFrame1)
        self.formFrame1.layout().addWidget(self.inputSelector1)
        self.inputSelector1 = slicer.qMRMLNodeComboBox(self.formFrame1)
        self.inputSelector1.nodeTypes = (("vtkMRMLSegmentationNode"), "")
        self.inputSelector1.addEnabled = False
        self.inputSelector1.removeEnabled = False

        self.inputSelector4 = qt.QLabel("Input transformation: ", self.formFrame4)
        self.formFrame4.layout().addWidget(self.inputSelector4)
        self.inputSelector4 = slicer.qMRMLNodeComboBox(self.formFrame4)
        self.inputSelector4.nodeTypes = (("vtkMRMLTransformNode"), "")
        self.inputSelector4.addEnabled = False
        self.inputSelector4.removeEnabled = False

        self.inputSelector2 = qt.QLabel("Set default Segmentation display : ", self.formFrame2)
        self.formFrame2.layout().addWidget(self.inputSelector2)

        self.inputSelector5 = qt.QLabel("Add markups : ", self.formFrame3)
        self.formFrame5.layout().addWidget(self.inputSelector5)

        self.inputSelector3 = qt.QLabel("Segmentation Correction: ", self.formFrame3)
        self.formFrame3.layout().addWidget(self.inputSelector3)

        # bind the current volume selector to the current scene of slicer
        self.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.inputSelector1.setMRMLScene(slicer.mrmlScene)
        self.inputSelector4.setMRMLScene(slicer.mrmlScene)

        # bind the input selector to the frame
        self.formFrame.layout().addWidget(self.inputSelector)
        self.formFrame1.layout().addWidget(self.inputSelector1)
        self.formFrame4.layout().addWidget(self.inputSelector4)

        # testing
        button = qt.QPushButton("Load Volume")
        self.formFrame.layout().addWidget(button)
        button.connect("clicked()", slicer.util.openAddVolumeDialog)
        button.show()

        # button for importing mesh files
        button1 = qt.QPushButton("Load Segemntation")
        self.formFrame1.layout().addWidget(button1)
        button1.connect("clicked()", slicer.util.openAddSegmentationDialog)
        button1.show()

        # button for importing mesh files
        button4 = qt.QPushButton("Load Transform")
        self.formFrame4.layout().addWidget(button4)
        button4.connect("clicked()", slicer.util.openAddTransformDialog)
        button4.show()

        # button for setting default segmentation display
        button2 = qt.QPushButton("Set default")
        self.formFrame2.layout().addWidget(button2)
        button2.connect("clicked(bool)", self.SetDefaultValuesClicked)
        button2.show()

        # button for Final work
        self.button5 = qt.QToolButton()
        self.button5.icon = qt.QIcon(os.path.join(os.path.dirname(__file__), 'MarkupsMouseModePlace.png'))
        self.button5.setCheckable(1)
        self.formFrame5.layout().addWidget(self.button5)
        self.button5.connect("clicked(bool)", self.enableaddmarkuponclick)
        self.button5.show()

        # button for Final work
        button3 = qt.QPushButton("Do corrections")
        self.formFrame3.layout().addWidget(button3)
        button3.connect("clicked(bool)", self.do_correctionsClicked)
        button3.show()

    def enableaddmarkuponclick(self):
        applicationLogic = slicer.app.applicationLogic()
        selectionNode = applicationLogic.GetSelectionNode()

        selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        interactionNode = applicationLogic.GetInteractionNode()

        if self.button5.checked:
            interactionNode.SwitchToPersistentPlaceMode()
        else:
            interactionNode.SwitchToViewTransformMode()

        #self.onClippingMarkupSelect(self.toFids)

    def onClippingMarkupSelect(self, node):

        if node != None and node != '':
            if node.GetID() not in self.__markupList:
                new_clippingModelNode = slicer.vtkMRMLModelNode()
                new_clippingModelNode.SetScene(slicer.mrmlScene)
                slicer.mrmlScene.AddNode(new_clippingModelNode)
                self.toFids.append(node.GetID())

            self.toFids = node
            self.setAndObserveClippingMarkupNode(node)


    def setAndObserveClippingMarkupNode(self, clippingMarkupNode):

        # Remove observer to old parameter node
        if self.__clippingMarkupNode and self.__clippingMarkupNodeObserver:
            self.__clippingMarkupNode.RemoveObserver(self.__clippingMarkupNodeObserver)
            self.__clippingMarkupNodeObserver = None

        # Set and observe new parameter node
        self.__clippingMarkupNode = clippingMarkupNode
        if self.__clippingMarkupNode:
            self.__clippingMarkupNodeObserver = self.__clippingMarkupNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onClippingMarkupNodeModified)

        applicationLogic = slicer.app.applicationLogic()
        selectionNode = applicationLogic.GetSelectionNode()

        # Update GUI
        self.updateModelFromClippingMarkupNode()

    def updateModelFromClippingMarkupNode(self):

        self.updateModelFromMarkup(self.__clippingMarkupNode, self.__clippingModelNode)

    def SetDefaultValuesClicked(self):
        if(not self.toFids):
            self.toFids = slicer.vtkMRMLMarkupsFiducialNode()
            self.toFids.SetName('toFids')
        if(not self.fromFids):
            self.fromFids = slicer.vtkMRMLMarkupsFiducialNode()
            self.fromFids.SetName('fromFids')
        if self.inputSelector1.currentNode():
            segmentationNode = self.inputSelector1.currentNode()
            TransformNode = self.inputSelector4.currentNode()
            segmentation = segmentationNode.GetSegmentation()
            segment = segmentation.GetSegment(segmentation.GetNthSegmentID(0))
            segment.SetColor(0, 0, 1)
            segmentationNode.GetDisplayNode().Visibility2DFillOff()

            if TransformNode:
                segmentationNode.SetAndObserveTransformNodeID(TransformNode.GetID())
                print ("transform successful")
            print ("color change successful")
        else:
            slicer.util.errorDisplay("No Segementation selected !")

    def do_correctionsClicked(self):
        # Copy and paste into Slicer Python interactor
        # Drag visible fiducials to deform transform

        # Scale defines how large cube will be created
        # numPerEdge defines how many fiducials to put on each edge of the cube
        size=0
        scalex = 10.0
        scaley = 10.0
        scalez = 10.0
        numPerEdge = size/10

        # Create the FROM fiducial list, and hide it so it doesn't change with mouse interactions

        slicer.mrmlScene.AddNode(self.toFids)
        self.toFids.Copy(self.fromFids)
        self.toFids.SetName('toFids')
        self.toFids.GetDisplayNode().SetVisibility(True)

        # Create the transform node to hold the deformable transformation later
        try:
            slicer.mrmlScene.RemoveNode(slicer.util.getNode("TpsTransform"))
            tNode = slicer.vtkMRMLTransformNode()
            tNode.SetName('TpsTransform')
            slicer.mrmlScene.AddNode(tNode)
        except:
            print("creating new TpsTransform")

        tNode = slicer.vtkMRMLTransformNode()
        tNode.SetName('TpsTransform')
        slicer.mrmlScene.AddNode(tNode)

        # Function that will be called whenever a TO fiducial moves and the transform needs an update

        def updateTpsTransform(caller, eventid):
            numPerEdge = self.fromFids.GetNumberOfFiducials()
            if numPerEdge != self.toFids.GetNumberOfFiducials():
                print
                'Error: Fiducial numbers are not equal!'
                return

            fp = vtk.vtkPoints()
            tp = vtk.vtkPoints()
            f = [0, 0, 0]
            t = [0, 0, 0]

            for i in range(numPerEdge):
                self.fromFids.GetNthFiducialPosition(i, f)
                self.toFids.GetNthFiducialPosition(i, t)
                fp.InsertNextPoint(f)
                tp.InsertNextPoint(t)

            tps = vtk.vtkThinPlateSplineTransform()
            tps.SetSourceLandmarks(fp)
            tps.SetTargetLandmarks(tp)
            tps.SetBasisToR()
            tNode.SetAndObserveTransformToParent(tps)

        self.toFids.AddObserver(vtk.vtkCommand.ModifiedEvent, updateTpsTransform)

        # A ROI annotation defines the region where the transform will be visualized

        roi = self.inputSelector1.currentNode()
        slicer.mrmlScene.AddNode(roi)
        roi.SetDisplayVisibility(True)
        # Set up transform visualization as gridlines

        tNode.CreateDefaultDisplayNodes()
        d = tNode.GetDisplayNode()
        d.SetAndObserveRegionNode(roi)
        d.SetVisualizationMode(slicer.vtkMRMLTransformDisplayNode.VIS_MODE_GRID)
        d.SetVisibility(False)
        roi.SetAndObserveTransformNodeID(tNode.GetID())
        TransformNode = self.inputSelector4.currentNode()
        tNode.SetAndObserveTransformNodeID(TransformNode.GetID())

    def updateModelFromMarkup(self, inputMarkup, outputModel):
        """
        Update model to enclose all points in the input markup list
        """

        # Delaunay triangulation is robust and creates nice smooth surfaces from a small number of points,
        # however it can only generate convex surfaces robustly.
        useDelaunay = True

        # Create polydata point set from markup points

        points = vtk.vtkPoints()
        cellArray = vtk.vtkCellArray()

        numberOfPoints = inputMarkup.GetNumberOfFiducials()

        # Surface generation algorithms behave unpredictably when there are not enough points
        # return if there are very few points
        if useDelaunay:
            if numberOfPoints < 3:
                return
        else:
            if numberOfPoints < 10:
                return

        points.SetNumberOfPoints(numberOfPoints)
        new_coord = [0.0, 0.0, 0.0]

        """for i in range(numberOfPoints):
            inputMarkup.GetNthFiducialPosition(i, new_coord)
            points.SetPoint(i, new_coord)"""

        cellArray.InsertNextCell(numberOfPoints)
        for i in range(numberOfPoints):
            cellArray.InsertCellPoint(i)

        pointPolyData = vtk.vtkPolyData()
        pointPolyData.SetLines(cellArray)
        pointPolyData.SetPoints(points)

        # Create surface from point set

        if useDelaunay:

            delaunay = vtk.vtkDelaunay3D()
            delaunay.SetInputData(pointPolyData)

            surfaceFilter = vtk.vtkDataSetSurfaceFilter()
            surfaceFilter.SetInputConnection(delaunay.GetOutputPort())

            smoother = vtk.vtkButterflySubdivisionFilter()
            smoother.SetInputConnection(surfaceFilter.GetOutputPort())
            smoother.SetNumberOfSubdivisions(3)
            smoother.Update()

            outputModel.SetPolyDataConnection(smoother.GetOutputPort())

        else:

            surf = vtk.vtkSurfaceReconstructionFilter()
            surf.SetInputData(pointPolyData)
            surf.SetNeighborhoodSize(20)
            surf.SetSampleSpacing(
                80)  # lower value follows the small details more closely but more dense pointset is needed as input

            cf = vtk.vtkContourFilter()
            cf.SetInputConnection(surf.GetOutputPort())
            cf.SetValue(0, 0.0)

            # Sometimes the contouring algorithm can create a volume whose gradient
            # vector and ordering of polygon (using the right hand rule) are
            # inconsistent. vtkReverseSense cures this problem.
            reverse = vtk.vtkReverseSense()
            reverse.SetInputConnection(cf.GetOutputPort())
            reverse.ReverseCellsOff()
            reverse.ReverseNormalsOff()

            outputModel.SetPolyDataConnection(reverse.GetOutputPort())

        # Create default model display node if does not exist yet
        if not outputModel.GetDisplayNode():
            modelDisplayNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelDisplayNode")
            modelDisplayNode.SetColor(0, 0, 1)  # Blue
            modelDisplayNode.BackfaceCullingOff()
            modelDisplayNode.SliceIntersectionVisibilityOn()
            modelDisplayNode.SetOpacity(0.3)  # Between 0-1, 1 being opaque
            slicer.mrmlScene.AddNode(modelDisplayNode)
            outputModel.SetAndObserveDisplayNodeID(modelDisplayNode.GetID())

        outputModel.GetDisplayNode().SliceIntersectionVisibilityOn()

        outputModel.Modified()


    def onClippingMarkupNodeModified(self, observer, eventid):

        self.updateModelFromClippingMarkupNode()

    def updateModelFromClippingMarkupNode(self):

        self.updateModelFromMarkup(self.__clippingMarkupNode, self.__clippingModelNode)

