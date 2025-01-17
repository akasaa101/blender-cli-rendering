# blender --background --python 04_principled_bsdf.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils


def set_principled_node_as_rough_blue(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(0.1, 0.2, 0.6, 1.0),
        metallic=0.5,
        specular=0.5,
        roughness=0.9,
    )


def set_principled_node_as_ceramic(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(0.8, 0.8, 0.8, 1.0),
        subsurface=0.1,
        subsurface_color=(0.9, 0.9, 0.9, 1.0),
        subsurface_radius=(1.0, 1.0, 1.0),
        metallic=0.2,
        specular=0.5,
        roughness=0.0,
    )


def set_principled_node_as_gold(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(1.00, 0.71, 0.22, 1.0),
        metallic=1.0,
        specular=0.5,
        roughness=0.1,
    )


def set_principled_node_as_glass(principled_node):
    utils.set_principled_node(principled_node=principled_node,
                              base_color=(0.95, 0.95, 0.95, 1.0),
                              metallic=0.0,
                              specular=0.5,
                              roughness=0.0,
                              clearcoat=0.5,
                              clearcoat_roughness=0.030,
                              ior=1.45,
                              transmission=0.98)


def set_scene_objects():
    left_object, center_object, right_object = utils.create_three_smooth_monkeys()

    mat = bpy.data.materials.new("Material_Left")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_glass(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    left_object.data.materials.append(mat)

    mat = bpy.data.materials.new("Material_Center")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_gold(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    center_object.data.materials.append(mat)

    mat = bpy.data.materials.new("Material_Right")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_rough_blue(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    right_object.data.materials.append(mat)

    current_object = utils.create_plane(size=20.0, name="Floor")
    mat = bpy.data.materials.new("Material_Plane")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_ceramic(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    current_object.data.materials.append(mat)

    bpy.ops.object.empty_add(location=(0.0, -0.75, 1.0))
    focus_target = bpy.context.object
    return focus_target


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(location=(0.0, -16.0, 2.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, focus_target)
utils.set_camera_params(camera_object.data, focus_target, lens=85, fstop=0.5)

## Lights
utils.build_environment_texture_background(world, hdri_path)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera_object,
                          num_samples,
                          use_denoising=True)

# Rendering
bpy.ops.render.render(animation=False, write_still=True)
