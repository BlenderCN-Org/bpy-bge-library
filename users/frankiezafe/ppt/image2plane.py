import bpy
import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       )

from bpy_extras.image_utils import load_image

# copy/paste and dirty hack of blender-2.70-linux-glibc211-x86_64/2.70/scripts/addons/io_import_images_as_planes.py 

def set_texture_options( context, texture ):
    #texture.image.use_alpha = BoolProperty(name="Use Alpha", default=False, description="Use alphachannel for transparency")
    texture.image.use_alpha = False
    #texture.image_user.use_auto_refresh = bpy.types.ImageUser.bl_rna.properties["use_auto_refresh"]
    texture.image_user.use_auto_refresh = True
    ctx = context.copy()
    ctx["edit_image"] = texture.image
    ctx["edit_image_user"] = texture.image_user
    bpy.ops.image.match_movie_length(ctx)

def set_material_options( material, slot):
    material.alpha = 1.0
    material.specular_alpha = 1.0
    slot.use_map_alpha = False
    #material.use_transparency = BoolProperty(name="Use Alpha", default=False, description="Use alphachannel for transparency")
    material.use_transparency = False
    #t = bpy.types.Material.bl_rna.properties["transparency_method"]
    #items = tuple((it.identifier, it.name, it.description) for it in t.enum_items)
    #material.transparency_method = EnumProperty(name="Transp. Method", description=t.description, items=items)
    #t = bpy.types.Material.bl_rna.properties["use_shadeless"]
    #material.use_shadeless = BoolProperty(name=t.name, default=False, description=t.description)
    #t = bpy.types.Material.bl_rna.properties["use_transparent_shadows"]
    #material.use_transparent_shadows = BoolProperty(name=t.name, default=False, description=t.description)

def create_image_textures( context, image):
    fn_full = os.path.normpath(bpy.path.abspath(image.filepath))
    # look for texture with importsettings
    for texture in bpy.data.textures:
        if texture.type == 'IMAGE':
            tex_img = texture.image
            if (tex_img is not None) and (tex_img.library is None):
                fn_tex_full = os.path.normpath(bpy.path.abspath(tex_img.filepath))
                if fn_full == fn_tex_full:
                    set_texture_options(context, texture)
                    return texture

    # if no texture is found: create one
    name_compat = bpy.path.display_name_from_filepath(image.filepath)
    texture = bpy.data.textures.new(name=name_compat, type='IMAGE')
    texture.image = image
    set_texture_options(context, texture)
    return texture

def create_material_for_texture( texture):
    # look for material with the needed texture
    for material in bpy.data.materials:
        slot = material.texture_slots[0]
        if slot and slot.texture == texture:
            set_material_options(material, slot)
            return material

    # if no material found: create one
    name_compat = bpy.path.display_name_from_filepath(texture.image.filepath)
    material = bpy.data.materials.new(name=name_compat)
    slot = material.texture_slots.add()
    slot.texture = texture
    slot.texture_coords = 'UV'
    set_material_options(material, slot)
    return material

def img2plane( folder, filename ):
    
    f = load_image( bpy.path.abspath( folder + filename ) )
    
    for i in bpy.data.images:
        print( i )
    for i in bpy.data.movieclips:
        print( i )
    
    img = bpy.data.images[ filename ]
    print( img, img.generated_width, img.generated_height, img.size )
    
    ratio = img.size[ 0 ] / img.size[ 1 ]
    print( ratio )
    
    scalew = 1
    scaleh = 1
    if ratio > 1:
        scaleh = 1 / ratio
    else:
        scalew = 1 / ratio
    
    texture = create_image_textures( bpy.context, img )
    material = create_material_for_texture( texture )
    
    bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
    plane = bpy.context.scene.objects.active
    if plane.mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    plane.dimensions = scalew, scaleh, 0.0
    plane.name = material.name
    bpy.ops.object.transform_apply(scale=True)
    plane.data.uv_textures.new()
    plane.data.materials.append(material)
    plane.data.uv_textures[0].data[0].image = img
    
    material.game_settings.use_backface_culling = False
    material.game_settings.alpha_blend = 'ALPHA'
    
    return plane

img2plane( "//", "surf_wide.jpg" )