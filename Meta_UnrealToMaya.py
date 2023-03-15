r"""

      ___           ___           ___           ___     
     /\__\         /\  \         /\  \         /\  \    
    /::|  |       /::\  \        \:\  \       /::\  \   
   /:|:|  |      /:/\:\  \        \:\  \     /:/\:\  \  
  /:/|:|__|__   /::\~\:\  \       /::\  \   /::\~\:\  \ 
 /:/ |::::\__\ /:/\:\ \:\__\     /:/\:\__\ /:/\:\ \:\__\
 \/__/~~/:/  / \:\~\:\ \/__/    /:/  \/__/ \/__\:\/:/  /
       /:/  /   \:\ \:\__\     /:/  /           \::/  / 
      /:/  /     \:\ \/__/     \/__/            /:/  /  
     /:/  /       \:\__\                       /:/  /   
     \/__/         \/__/                       \/__/    

Author: Bryan Godoy, Senior Technical Animator

Script: Meta Unreal To Maya

Description: Exports Unreal MetaHuman Facial Animation as JSON via Facial Control Rig Controls

Instructions: 
    
    1.) Create Level Sequence in Unreal
    2.) Add Desired MetaHuman To Sequence (must be associated to a Facial Control Rig)
    3.) Bake Animation onto MetaHuman Facial Control Board
    4.) Execute Script (Level Sequence must be open)

Versions:

v.[1.0.0]
===> Initial Release

v.[1.0.1]
===> Added functionality to acquire anim data for 'xformCTRLS' and 'vec2dCTRLS'

"""

import unreal as ue
import json

class Meta:

    def __init__(self):

        self.script = "Meta Unreal To Maya [1.0.1]"
        self.targetTrack = "Face"
        self.controlType = [
            "vec2dCTRL",
            "xformCTRL",
            "animParameter"
        ] #vec2dCTRL' == 2 outputs, 'xformCTRL' == 6 outputs (translation, rotation), 'animParameter' == 1 output
        self.metadata = {
            "Level Sequence": None,
            "Control Rig": None,
            "Frame Range": None,
            "Track Name": None,
            "Subtrack Name": None,
            "Animation Data": []
        }
        
        self.xformCTRLS = [
            "CTRL_C_eyesAim",
            "CTRL_L_eyeAim",
            "CTRL_R_eyeAim"
        ]

        self.vec2dCTRLS = [
            "CTRL_C_jaw",
            "CTRL_C_tongue_roll",
            "CTRL_C_tongue_tip",
            "CTRL_C_tongue",
            "CTRL_C_mouth",
            "CTRL_R_nose",
            "CTRL_L_nose",
            "CTRL_L_eye",
            "CTRL_R_eye",
            "CTRL_C_eye",
            "CTRL_C_teethD",
            "CTRL_C_teethU",
            "CTRL_L_mouth_corner",
            "CTRL_R_mouth_corner"
        ]
        
        self.outputPath = r"C:\Users\BGodoy\Documents\maya\2022\scripts\Sumo_SemT"
        
        if(self.outputPath.count(r"\\") > 0):
            
            self.outputPath.replace(r"\\", "\\")

        self.fileName = "MetaHuman_Control_Board"

    def SaveDataLevelSequence(self):
    
        # get data from level sequences
        actorObj = ue.EditorActorSubsystem()
        allActors = ue.EditorActorSubsystem.get_all_level_actors(actorObj)

        for actor in allActors:
            
            if(type(actor) == ue.LevelSequenceActor):

                seq = actor.get_sequence()
                self.metadata["Level Sequence"] = str(seq.get_name())
                tracks = seq.get_bindings()
                
                # fetch control rig for 'self.targetTrack'
                for controlRig in ue.ControlRigSequencerLibrary.get_control_rigs(seq):

                    if(str(controlRig.get_editor_property("control_rig").get_name()).find(self.targetTrack) >= 0):

                        targetCR = controlRig.get_editor_property("control_rig")
                        self.metadata["Control Rig"] = str(targetCR.get_name()) # DATA: CONTROL RIG
                            
                # gather array of 'FrameNumbers'
                frameRange = []

                for frame in range(int(seq.get_playback_start()), int(seq.get_playback_end())):

                    frameRange.append(ue.FrameNumber(frame))

                self.metadata["Frame Range"] = (frameRange[0].value, frameRange[-1].value) # DATA: FRAMERANGE

                # obtain vect2dCTRLS
                getCTRLS = targetCR.get_hierarchy().get_controls()
                
                for ctrl2d in self.vec2dCTRLS:
        
                    for ctrl in getCTRLS:
            
                        if(ctrl2d == ctrl.name):

                            for frame in frameRange:
                                
                                vecX = float(ue.ControlRigSequencerLibrary.get_local_control_rig_vector2d(seq, targetCR, ctrl.name, frame).x)
                                vecY = float(ue.ControlRigSequencerLibrary.get_local_control_rig_vector2d(seq, targetCR, ctrl.name, frame).y)

                                self.metadata["Animation Data"].append([
                                	self.controlType[0],
                                    str(ctrl.name),
                                    frame.value,
                                    [vecX, vecY]
                                    ]) # DATA: CONTROL NAME (Anim Params), FRAME, LOCAL CONTROL RIG VECTOR 2D

                for track in tracks:

                    if(str(track).find(seq.get_name()) >= 0):

                        if(track.get_display_name() == self.targetTrack):

                            self.metadata["Track Name"] = str(track.get_display_name()) # DATA: TRACK NAME
                            subtracks = track.get_tracks()
                            
                            for data in subtracks:
                                
                                if(type(data) == ue.MovieSceneControlRigParameterTrack):

                                    self.metadata["Subtrack Name"] = str(data.get_display_name()) # DATA: SUBTRACK NAME
                                    
                                    for section in data.get_sections():
                                        
                                        animParams = section.get_parameter_names() #ue.MovieSceneControlRigParameterTrack

                                    if(len(animParams) > 0):
                                    
                                        for param in animParams:

                                            for frame in frameRange:
                                                
                                                if(str(param) in self.xformCTRLS):
                                                    
                                                    location = ue.ControlRigSequencerLibrary.get_local_control_rig_transform(seq, targetCR, param, frame).transform_location(ue.Vector())
                                                    rotation = ue.ControlRigSequencerLibrary.get_local_control_rig_transform(seq, targetCR, param, frame).transform_rotation(ue.Rotator())
                                                
                                                    self.metadata["Animation Data"].append([
                                                        self.controlType[1],
                                                        str(param),
                                                        frame.value,
                                                        [location.to_tuple(), rotation.to_tuple()]
                                                    ]) # DATA: CONTROL NAME (Anim Params), FRAME, LOCAL CONTROL RIG TRANSFORM

                                                elif(str(param) not in self.xformCTRLS):

                                                    if(str(param) not in self.vec2dCTRLS):
                                                        
                                                        self.metadata["Animation Data"].append([
                                                            self.controlType[2],
                                                            str(param),
                                                            frame.value,
                                                            ue.ControlRigSequencerLibrary.get_local_control_rig_float(seq, targetCR, param, frame)
                                                        ]) # DATA: CONTROL NAME (Anim Params), FRAME, LOCAL CONTROL RIG FLOAT

                                    else:
                                        
                                        print(f"{self.script}: No animation parameters found in subtrack, {data.get_display_name()}")         
        
        self.OutputJSON()

    def OutputJSON(self):
        
        with open(f"{self.outputPath}\\{self.fileName}.json", "w") as outfile:

            json.dump(self.metadata, outfile, sort_keys = False, indent = 4)
        
        if(outfile):
            
            # print results via Output Log
            for dt in range(len(self.metadata) - 1): # do not print 'Animation Data' to increase performance
                
                print(f"{self.script}: {list(self.metadata.keys())[dt]} ==> {list(self.metadata.values())[dt]}")
            
            print(f"{self.script}: '{self.outputPath}\\{self.fileName}.json' saved successfully!")

        else:

            raise IOError(f"{self.script}: '{self.outputPath}\\{self.fileName}.json' was not saved successfully. Please ensure Level Sequence is open and contains Facial Animation and try again.")
        
if __name__ == '__main__':
    
    Meta().SaveDataLevelSequence()