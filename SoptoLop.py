import hou
from PySide2 import QtWidgets, QtCore

class ImportSoptoLopGUI(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Karma Scene Setup Manager")
        self.setMinimumWidth(850)
        self.setMinimumHeight(150)

        self.Vlayout = QtWidgets.QVBoxLayout()
        
        self.Hlayout_scene_graph_path = QtWidgets.QHBoxLayout()
        
        self.scene_graph_path_label = QtWidgets.QLabel("Scene Graph Path:")
        self.Hlayout_scene_graph_path.addWidget(self.scene_graph_path_label)
        
        self.scene_graph_path_input = QtWidgets.QLineEdit()
        self.Hlayout_scene_graph_path.addWidget(self.scene_graph_path_input)
        
        self.Vlayout.addLayout(self.Hlayout_scene_graph_path)
        
        self.Hlayout_import_type = QtWidgets.QHBoxLayout()
        
        self.import_type_label = QtWidgets.QLabel("Scene Import Type:")
        self.Hlayout_import_type.addWidget(self.import_type_label)
        
        self.import_type_dropdown = QtWidgets.QComboBox()
        self.import_type_dropdown.addItem("Scene Import All Together")
        self.import_type_dropdown.addItem("Scene Import Each Category Separately")
        self.import_type_dropdown.addItem("Scene Import Each Node Separately")
        self.import_type_dropdown.addItem("Scene Import by Prefix")
        self.Hlayout_import_type.addWidget(self.import_type_dropdown)
        
        self.Vlayout.addLayout(self.Hlayout_import_type)
        
        self.add_button = QtWidgets.QPushButton("Create Karma Setup")
        self.Vlayout.addWidget(self.add_button)
        
        self.status_label = QtWidgets.QLabel("")
        self.Vlayout.addWidget(self.status_label)
        
        self.add_button.clicked.connect(self.karmaSetup)

        self.setLayout(self.Vlayout)

        
    def karmaSetup(self):
    
        scene_graph_path = self.scene_graph_path_input.text()
        
        if not scene_graph_path.strip():
            self.status_label.setText("Please enter Scene Graph Path!")
            return   
        
        if " " in scene_graph_path:
            self.status_label.setText("Scene Graph Path should not contain spaces. Consider replacing space with '/'.")
            return
            
        for char in scene_graph_path:
            if not char.isalnum() and char != "/":
                self.status_label.setText("Shot directory should not contain symbols other than '/'.")
                return 

        selected_nodes = hou.selectedNodes()
  
        if self.import_type_dropdown.currentText() == "Scene Import Each Node Separately" or self.import_type_dropdown.currentText() == "Scene Import by Prefix":
            if not selected_nodes:
                hou.ui.displayMessage("No Nodes Selected", title="Warning")
                return

 
        exists = self.checkSceneGraphPathExists(scene_graph_path)
        if exists == True:
            self.status_label.setText("The path already exists in the scene graph.")
            return
        else:
            self.status_label.setText("")  
            
        lop_network = hou.node("/stage")           
        shot = "/"+scene_graph_path
        
        if self.import_type_dropdown.currentText() == "Scene Import All Together":
             sceneimportnode = self.createSceneImportNode(lop_network,"sceneimportAll","*","!!OBJ!!",shot)
             merge_node = lop_network.createNode("merge", "merge")
             merge_node.setInput(0, sceneimportnode)  
           
             merge_node.setDisplayFlag(True)
            
             lop_network.layoutChildren()

        if self.import_type_dropdown.currentText() == "Scene Import Each Category Separately":
        
            geo = self.createSceneImportNode(lop_network,"sceneimportGeos","*","!!OBJ/GEOMETRY!!",shot+"/geometry")
            light = self.createSceneImportNode(lop_network,"sceneimportLights","*","!!OBJ/LIGHT!!",shot+"/lights")
            cam = self.createSceneImportNode(lop_network,"sceneimportCameras","*","!!OBJ/CAMERA!!",shot+"/cameras")
            
            merge_node = lop_network.createNode("merge", "merge")
            merge_node.setInput(0, geo)  
            merge_node.setInput(1, light)
            merge_node.setInput(2, cam)
            
            merge_node.setDisplayFlag(True)
            
            lop_network.layoutChildren()

        if self.import_type_dropdown.currentText() == "Scene Import Each Node Separately" or self.import_type_dropdown.currentText() == "Scene Import by Prefix":
           
            node_groups = {}
            
            for node in selected_nodes:
            
                node_path = node.path()
                node_type = node.type().name()
                node_name = node.name()
                
                if "_" in node_name and self.import_type_dropdown.currentText() == "Scene Import by Prefix":
                    prefix = node_name.split("_")[0] 
                    key = prefix 
                else:
                    if "light" in node_type :
                        key = "lights"
                    else:
                        key = node_type
                        
                if key not in node_groups:
                    node_groups[key] = []
                    
                node_groups[key].append(node)
                
            merge_nodes = []
            for key, nodes in node_groups.items():
                mergename = "merge"+key
                dest_path = "/"+key
                scene_import_nodes = []
                for node in nodes:
                    node_name = "sceneimport"+node.name()
                    scene_import_node = self.createSceneImportNode(lop_network,node_name,node.path(),"!!OBJ!!",shot+dest_path)
                    scene_import_nodes.append(scene_import_node)
                mergenode = self.createMergeNode(lop_network, scene_import_nodes,mergename)
                merge_nodes.append(mergenode)
                
            if merge_nodes:
                combine_merge_node = self.createMergeNode(lop_network, merge_nodes, "mergecombined")
                combine_merge_node.setDisplayFlag(True)
                
            lop_network.layoutChildren()
        self.accept()          
                
    def createSceneImportNode(self,lop_network,name,objects,filter,destpath):
        scene_import_node = lop_network.createNode("sceneimport", name)
        scene_import_node.parm("objects").set(objects)
        scene_import_node.parm("filter").set(filter)
        scene_import_node.parm("objdestpath").set(destpath)
        return scene_import_node
 
    def createMergeNode(self,lop_network,nodeslist, mergename):
        i = 0
        merge_node = lop_network.createNode("merge", mergename)
        for node in nodeslist:
            merge_node.setInput(i,node) 
            i +=1
        return merge_node

    def checkSceneGraphPathExists(self,scene_graph_path):
    
        exists = False
        lop_network = hou.node("/stage")
        correct_scene_graph_path = "/"+scene_graph_path

        for node in lop_network.children():
            if "sceneimport" in node.name():
                if node.parm("objdestpath").eval() == correct_scene_graph_path:
                    exists = True
                    return exists
        return exists   
        
window =  ImportSoptoLopGUI()
window.show()