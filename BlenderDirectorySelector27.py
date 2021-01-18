# https://blender.stackexchange.com/questions/14738/use-filemanager-to-select-directory-instead-of-file/14778

import bpy


class SelectDirExample(bpy.types.Operator):

    """Create render for all chracters"""
    bl_idname = "example.select_dir"
    bl_label = "Dir Selection Example Operator"
    bl_options = {'REGISTER'}

    # Define this to tell 'fileselect_add' that we want a directoy
    directory = bpy.props.StringProperty(
        name="Outdir Path",
        description="Where I will save my stuff"
        # subtype='DIR_PATH' is not needed to specify the selection mode.
        # But this will be anyway a directory path.
        )

    def execute(self, context):

        print("Selected dir: '" + self.directory + "'")

        return {'FINISHED'}

    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected
        # file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        # Tells Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(SelectDirExample)


def unregister():
    bpy.utils.unregister_class(SelectDirExample)


#
# Invoke register if started from editor
if __name__ == "__main__":
    register()