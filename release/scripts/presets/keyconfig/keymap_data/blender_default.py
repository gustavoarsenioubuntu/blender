# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# ------------------------------------------------------------------------------
# Configurable Parameters

from collections import namedtuple

# TODO: remove when we drop Python 3.6
import sys
if sys.version_info >= (3, 7):
    KeymapParams = namedtuple(
        "KeymapParams",
        ("apple", "legacy", "select_mouse", "action_mouse"),
        defaults=(
            sys.platform == "darwin",
            False,
            'SELECTMOUSE',
            'ACTIONMOUSE',
        ),
    )
else:
    KeymapParams = namedtuple(
        "KeymapParams",
        ("apple", "legacy", "select_mouse", "action_mouse"),
    )
    KeymapParams.__new__.__defaults__ = (
        sys.platform == "darwin",
        False,
        'SELECTMOUSE',
        'ACTIONMOUSE',
    )
del namedtuple, sys


# ------------------------------------------------------------------------------
# Constants

# Physical layout.
NUMBERS_1 = ('ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'ZERO')
# Numeric order.
NUMBERS_0 = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE')


# ------------------------------------------------------------------------------
# Keymap Item Wrappers

def op_menu(menu, kmi_args):
    return ("wm.call_menu", kmi_args, {"properties": [("name", menu)]})


def op_menu_pie(menu, kmi_args):
    return ("wm.call_menu_pie", kmi_args, {"properties": [("name", menu)]})


def op_panel(menu, kmi_args, kmi_data=()):
    return ("wm.call_panel", kmi_args, {"properties": [("name", menu), *kmi_data]})


# ------------------------------------------------------------------------------
# Keymap Templates

def _template_items_select_actions(operator):
    return [
        (operator, {"type": 'A', "value": 'PRESS'}, {"properties": [("action", 'SELECT')]}),
        (operator, {"type": 'A', "value": 'PRESS', "alt": True}, {"properties": [("action", 'DESELECT')]}),
        (operator, {"type": 'I', "value": 'PRESS', "ctrl": True}, {"properties": [("action", 'INVERT')]}),
        (operator, {"type": 'A', "value": 'DOUBLE_CLICK'}, {"properties": [("action", 'DESELECT')]}),
    ]


def _template_items_object_subdivision_set():
    return [
        ("object.subdivision_set",
         {"type": NUMBERS_0[i], "value": 'PRESS', "ctrl": True},
         {"properties": [("level", i)]})
        for i in range(6)
    ]


def _template_items_gizmo_tweak_value():
    return [
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ]


def _template_items_gizmo_tweak_modal():
    return [
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("PRECISION_ON", {"type": 'RIGHT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("PRECISION_OFF", {"type": 'RIGHT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("PRECISION_ON", {"type": 'LEFT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("PRECISION_OFF", {"type": 'LEFT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("SNAP_ON", {"type": 'RIGHT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_OFF", {"type": 'RIGHT_CTRL', "value": 'RELEASE', "any": True}, None),
        ("SNAP_ON", {"type": 'LEFT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_OFF", {"type": 'LEFT_CTRL', "value": 'RELEASE', "any": True}, None),
    ]


def _template_items_editmode_mesh_select_mode():
    return [
        (
            "mesh.select_mode",
            {"type": k, "value": 'PRESS', **key_expand, **key_extend},
            {"properties": [*prop_extend, *prop_expand, ("type", e)]}
        )
        for key_expand, prop_expand in (({}, ()), ({"ctrl": True}, (("use_expand", True),)))
        for key_extend, prop_extend in (({}, ()), ({"shift": True}, (("use_extend", True),)))
        for k, e in (('ONE', 'VERT'), ('TWO', 'EDGE'), ('THREE', 'FACE'))
    ]


def _template_items_proportional_editing(*, connected=False):
    return [
        op_menu_pie("VIEW3D_MT_proportional_editing_falloff_pie", {"type": 'O', "value": 'PRESS', "shift": True}),
        ("wm.context_toggle_enum", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.proportional_edit'), ("value_1", 'DISABLED'), ("value_2", 'ENABLED')]}),
        *(() if not connected else (
            ("wm.context_toggle_enum", {"type": 'O', "value": 'PRESS', "alt": True},
             {"properties": [("data_path", 'tool_settings.proportional_edit'), ("value_1", 'DISABLED'), ("value_2", 'CONNECTED')]}),
        ))
    ]


# ------------------------------------------------------------------------------
# Window, Screen, Areas, Regions

def km_window(params):
    items = []
    keymap = (
        "Window",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    if params.apple:
        # Apple standard shortcuts. Cmd+F for search since F-keys are not easy to use.
        items.extend([
            ("wm.read_homefile", {"type": 'N', "value": 'PRESS', "oskey": True}, None),
            op_menu("TOPBAR_MT_file_open_recent", {"type": 'O', "value": 'PRESS', "shift": True, "oskey": True}),
            ("wm.open_mainfile", {"type": 'O', "value": 'PRESS', "oskey": True}, None),
            ("wm.save_mainfile", {"type": 'S', "value": 'PRESS', "oskey": True}, None),
            ("wm.save_as_mainfile", {"type": 'S', "value": 'PRESS', "shift": True, "oskey": True}, None),
            ("wm.quit_blender", {"type": 'Q', "value": 'PRESS', "oskey": True}, None),
            ("wm.search_menu", {"type": 'F', "value": 'PRESS', "oskey": True}, None),
        ])

    items.extend([
        # File operations
        ("wm.read_homefile", {"type": 'N', "value": 'PRESS', "ctrl": True}, None),
        op_menu("TOPBAR_MT_file_open_recent", {"type": 'O', "value": 'PRESS', "shift": True, "ctrl": True}),
        ("wm.open_mainfile", {"type": 'O', "value": 'PRESS', "ctrl": True}, None),
        ("wm.save_mainfile", {"type": 'S', "value": 'PRESS', "ctrl": True}, None),
        ("wm.save_as_mainfile", {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("wm.quit_blender", {"type": 'Q', "value": 'PRESS', "ctrl": True}, None),

        # Quick menu and toolbar
        op_menu("SCREEN_MT_user_menu", {"type": 'Q', "value": 'PRESS'}),
        ("wm.toolbar", {"type": 'SPACE', "value": 'PRESS'}, None),

        # Fast editor switching
        *(
            ("wm.context_set_enum",
             {"type": k, "value": 'PRESS', "shift": True},
             {"properties": [("data_path", 'area.type'), ("value", t)]})
            for k, t in (
                ('F4', 'CONSOLE'),
                ('F5', 'VIEW_3D'),
                ('F6', 'GRAPH_EDITOR'),
                ('F7', 'PROPERTIES'),
                ('F8', 'SEQUENCE_EDITOR'),
                ('F9', 'OUTLINER'),
                ('F10', 'IMAGE_EDITOR'),
                ('F11', 'TEXT_EDITOR'),
                ('F12', 'DOPESHEET_EDITOR'),
            )
        ),

        # NDOF settings
        op_menu("USERPREF_MT_ndof_settings", {"type": 'NDOF_BUTTON_MENU', "value": 'PRESS'}),
        ("wm.context_scale_float", {"type": 'NDOF_BUTTON_PLUS', "value": 'PRESS'},
         {"properties": [("data_path", 'user_preferences.inputs.ndof_sensitivity'), ("value", 1.1)]}),
        ("wm.context_scale_float", {"type": 'NDOF_BUTTON_MINUS', "value": 'PRESS'},
         {"properties": [("data_path", 'user_preferences.inputs.ndof_sensitivity'), ("value", 1.0 / 1.1)]}),
        ("wm.context_scale_float", {"type": 'NDOF_BUTTON_PLUS', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'user_preferences.inputs.ndof_sensitivity'), ("value", 1.5)]}),
        ("wm.context_scale_float", {"type": 'NDOF_BUTTON_MINUS', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'user_preferences.inputs.ndof_sensitivity'), ("value", 2.0 / 3.0)]}),
        ("info.reports_display_update", {"type": 'TIMER_REPORT', "value": 'ANY', "any": True}, None),
    ])

    if not params.legacy:
        # New shortcuts
        items.extend([
            ("wm.doc_view_manual_ui_context", {"type": 'F1', "value": 'PRESS'}, None),
            op_menu("TOPBAR_MT_file_specials", {"type": 'F2', "value": 'PRESS'}),
            ("wm.search_menu", {"type": 'F3', "value": 'PRESS'}, None),
            op_menu("TOPBAR_MT_window_specials", {"type": 'F4', "value": 'PRESS'}),
        ])
    else:
        # Old shorctus
        items.extend([
            ("wm.window_new", {"type": 'W', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("wm.save_homefile", {"type": 'U', "value": 'PRESS', "ctrl": True}, None),
            ("wm.open_mainfile", {"type": 'F1', "value": 'PRESS'}, None),
            ("wm.link", {"type": 'O', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("wm.append", {"type": 'F1', "value": 'PRESS', "shift": True}, None),
            ("wm.save_mainfile", {"type": 'W', "value": 'PRESS', "ctrl": True}, None),
            ("wm.save_as_mainfile", {"type": 'F2', "value": 'PRESS'}, None),
            ("wm.save_as_mainfile", {"type": 'S', "value": 'PRESS', "ctrl": True, "alt": True},
             {"properties": [("copy", True)]}),
            ("wm.window_fullscreen_toggle", {"type": 'F11', "value": 'PRESS', "alt": True}, None),
            ("wm.doc_view_manual_ui_context", {"type": 'F1', "value": 'PRESS', "alt": True}, None),
            ("wm.redraw_timer", {"type": 'T', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("wm.debug_menu", {"type": 'D', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ])

    return keymap


def km_screen(params):
    items = []
    keymap = (
        "Screen",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Animation
        ("screen.animation_step", {"type": 'TIMER0', "value": 'ANY', "any": True}, None),
        ("screen.region_blend", {"type": 'TIMERREGION', "value": 'ANY', "any": True}, None),
        # Full screen and cycling
        ("screen.screen_full_area", {"type": 'SPACE', "value": 'PRESS', "ctrl": True}, None),
        ("screen.screen_full_area", {"type": 'SPACE', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("use_hide_panels", True)]}),
        ("screen.space_context_cycle", {"type": 'TAB', "value": 'PRESS', "ctrl": True},
         {"properties": [("direction", 'NEXT')]}),
        ("screen.space_context_cycle", {"type": 'TAB', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'PREV')]}),
        ("screen.workspace_cycle", {"type": 'PAGE_DOWN', "value": 'PRESS', "ctrl": True},
         {"properties": [("direction", 'NEXT')]}),
        ("screen.workspace_cycle", {"type": 'PAGE_UP', "value": 'PRESS', "ctrl": True},
         {"properties": [("direction", 'PREV')]}),
        # Quad view
        ("screen.region_quadview", {"type": 'Q', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        # Repeat last
        ("screen.repeat_last", {"type": 'R', "value": 'PRESS', "shift": True}, None),
        # Files
        ("file.execute", {"type": 'RET', "value": 'PRESS'}, None),
        ("file.execute", {"type": 'NUMPAD_ENTER', "value": 'PRESS'}, None),
        ("file.cancel", {"type": 'ESC', "value": 'PRESS'}, None),
        # Undo
        ("ed.undo", {"type": 'Z', "value": 'PRESS', "ctrl": True}, None),
        ("ed.redo", {"type": 'Z', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        # Render
        ("render.render", {"type": 'F12', "value": 'PRESS'},
         {"properties": [("use_viewport", True)]}),
        ("render.render", {"type": 'F12', "value": 'PRESS', "ctrl": True},
         {"properties": [("animation", True), ("use_viewport", True)]}),
        ("render.view_cancel", {"type": 'ESC', "value": 'PRESS'}, None),
        ("render.view_show", {"type": 'F11', "value": 'PRESS'}, None),
        ("render.play_rendered_anim", {"type": 'F11', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.legacy:
        # Old keymap
        items.extend([
            ("ed.undo_history", {"type": 'Z', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("screen.screen_set", {"type": 'RIGHT_ARROW', "value": 'PRESS', "ctrl": True},
             {"properties": [("delta", 1)]}),
            ("screen.screen_set", {"type": 'LEFT_ARROW', "value": 'PRESS', "ctrl": True},
             {"properties": [("delta", -1)]}),
            ("screen.screenshot", {"type": 'F3', "value": 'PRESS', "ctrl": True}, None),
            ("screen.repeat_history", {"type": 'R', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("screen.region_flip", {"type": 'F5', "value": 'PRESS'}, None),
            ("screen.redo_last", {"type": 'F6', "value": 'PRESS'}, None),
            ("script.reload", {"type": 'F8', "value": 'PRESS'}, None),
            ("screen.userpref_show", {"type": 'U', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ])

    if params.apple:
        # Apple undo and user prefs
        items.extend([
            ("ed.undo", {"type": 'Z', "value": 'PRESS', "oskey": True}, None),
            ("ed.redo", {"type": 'Z', "value": 'PRESS', "shift": True, "oskey": True}, None),
            ("ed.undo_history", {"type": 'Z', "value": 'PRESS', "alt": True, "oskey": True}, None),
            ("screen.userpref_show", {"type": 'COMMA', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_screen_editing(params):
    items = []
    keymap = ("Screen Editing",
              {"space_type": 'EMPTY', "region_type": 'WINDOW'},
              {"items": items})

    items.extend([
        # Action zones
        ("screen.actionzone", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("modifier", 0)]}),
        ("screen.actionzone", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("modifier", 1)]}),
        ("screen.actionzone", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("modifier", 2)]}),
        # Screen tools
        ("screen.area_split", {"type": 'ACTIONZONE_AREA', "value": 'ANY'}, None),
        ("screen.area_join", {"type": 'ACTIONZONE_AREA', "value": 'ANY'}, None),
        ("screen.area_dupli", {"type": 'ACTIONZONE_AREA', "value": 'ANY', "shift": True}, None),
        ("screen.area_swap", {"type": 'ACTIONZONE_AREA', "value": 'ANY', "ctrl": True}, None),
        ("screen.region_scale", {"type": 'ACTIONZONE_REGION', "value": 'ANY'}, None),
        ("screen.screen_full_area", {"type": 'ACTIONZONE_FULLSCREEN', "value": 'ANY'},
         {"properties": [("use_hide_panels", True)]}),
        # Area move after action zones
        ("screen.area_move", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("screen.area_options", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
    ])

    if params.legacy:
        items.extend([
            ("screen.header", {"type": 'F9', "value": 'PRESS', "alt": True}, None),
        ])

    return keymap


def km_header(_params):
    items = []
    keymap = (
        "Header",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("screen.header_context_menu", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
    ])

    return keymap


def km_view2d(_params):
    items = []
    keymap = (
        "View2D",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Scrollbars
        ("view2d.scroller_activate", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroller_activate", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        # Pan/scroll
        ("view2d.pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("view2d.pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
        ("view2d.pan", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("view2d.scroll_right", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("view2d.scroll_left", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("view2d.scroll_down", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True}, None),
        ("view2d.scroll_up", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True}, None),
        ("view2d.ndof", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
        # Zoom with single step
        ("view2d.zoom_out", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'}, None),
        ("view2d.zoom_in", {"type": 'WHEELINMOUSE', "value": 'PRESS'}, None),
        ("view2d.zoom_out", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("view2d.zoom_in", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("view2d.zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
        ("view2d.smoothview", {"type": 'TIMER1', "value": 'ANY', "any": True}, None),
        # Scroll up/down, only when zoom is not available.
        ("view2d.scroll_down", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroll_up", {"type": 'WHEELUPMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroll_right", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroll_left", {"type": 'WHEELUPMOUSE', "value": 'PRESS'}, None),
        # Zoom with drag and border
        ("view2d.zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("view2d.zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
        ("view2d.zoom_border", {"type": 'B', "value": 'PRESS', "shift": True}, None),
    ])

    return keymap


def km_view2d_buttons_list(_params):
    items = []
    keymap = (
        "View2D Buttons List",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Scrollbars
        ("view2d.scroller_activate", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroller_activate", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        # Pan scroll
        ("view2d.pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("view2d.pan", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("view2d.scroll_down", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroll_up", {"type": 'WHEELUPMOUSE', "value": 'PRESS'}, None),
        ("view2d.scroll_down", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("page", True)]}),
        ("view2d.scroll_up", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("page", True)]}),
        # Zoom
        ("view2d.zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("view2d.zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
        ("view2d.zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
        ("view2d.zoom_out", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("view2d.zoom_in", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("view2d.reset", {"type": 'HOME', "value": 'PRESS'}, None),
    ])

    return keymap


def km_user_interface(_params):
    items = []
    keymap = (
        "User Interface",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Eyedroppers all have the same event, and pass it through until
        # a suitable eyedropper handles it.
        ("ui.eyedropper_color", {"type": 'E', "value": 'PRESS'}, None),
        ("ui.eyedropper_colorband", {"type": 'E', "value": 'PRESS'}, None),
        ("ui.eyedropper_colorband_point", {"type": 'E', "value": 'PRESS', "alt": True}, None),
        ("ui.eyedropper_id", {"type": 'E', "value": 'PRESS'}, None),
        ("ui.eyedropper_depth", {"type": 'E', "value": 'PRESS'}, None),
        # Copy data path
        ("ui.copy_data_path_button", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("ui.copy_data_path_button", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("full_path", True)]}),
        # Keyframes and drivers
        ("anim.keyframe_insert_button", {"type": 'I', "value": 'PRESS'}, None),
        ("anim.keyframe_delete_button", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("anim.keyframe_clear_button", {"type": 'I', "value": 'PRESS', "shift": True, "alt": True}, None),
        ("anim.driver_button_add", {"type": 'D', "value": 'PRESS', "ctrl": True}, None),
        ("anim.driver_button_remove", {"type": 'D', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("anim.keyingset_button_add", {"type": 'K', "value": 'PRESS'}, None),
        ("anim.keyingset_button_remove", {"type": 'K', "value": 'PRESS', "alt": True}, None),
    ])

    return keymap


# ------------------------------------------------------------------------------
# Editors


def km_property_editor(_params):
    items = []
    keymap = (
        "Property Editor",
        {"space_type": 'PROPERTIES', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("buttons.context_menu", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
        ("screen.space_context_cycle", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("direction", 'PREV'), ], },),
        ("screen.space_context_cycle", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("direction", 'NEXT'), ], },),
    ])

    return keymap


def km_outliner(_params):
    items = []
    keymap = (
        "Outliner",
        {"space_type": 'OUTLINER', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("outliner.highlight_update", {"type": 'MOUSEMOVE', "value": 'ANY', "any": True}, None),
        ("outliner.item_rename", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
        ("outliner.item_activate", {"type": 'LEFTMOUSE', "value": 'CLICK'},
         {"properties": [("extend", False), ("recursive", False)]}),
        ("outliner.item_activate", {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
         {"properties": [("extend", True), ("recursive", False)]}),
        ("outliner.item_activate", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True},
         {"properties": [("extend", False), ("recursive", True)]}),
        ("outliner.item_activate", {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
         {"properties": [("extend", True), ("recursive", True)]}),
        ("outliner.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("outliner.item_openclose", {"type": 'RET', "value": 'PRESS'},
         {"properties": [("all", False)]}),
        ("outliner.item_openclose", {"type": 'RET', "value": 'PRESS', "shift": True},
         {"properties": [("all", True)]}),
        ("outliner.item_rename", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("outliner.operation", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
        ("outliner.item_drag_drop", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, None),
        ("outliner.item_drag_drop", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, None),
        ("outliner.show_hierarchy", {"type": 'HOME', "value": 'PRESS'}, None),
        ("outliner.show_active", {"type": 'PERIOD', "value": 'PRESS'}, None),
        ("outliner.show_active", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("outliner.scroll_page", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("up", False)]}),
        ("outliner.scroll_page", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("up", True)]}),
        ("outliner.show_one_level", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("outliner.show_one_level", {"type": 'NUMPAD_MINUS', "value": 'PRESS'},
         {"properties": [("open", False)]}),
        *_template_items_select_actions("outliner.select_all"),
        ("outliner.expanded_toggle", {"type": 'A', "value": 'PRESS', "shift": True}, None),
        ("outliner.keyingset_add_selected", {"type": 'K', "value": 'PRESS'}, None),
        ("outliner.keyingset_remove_selected", {"type": 'K', "value": 'PRESS', "alt": True}, None),
        ("anim.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
        ("anim.keyframe_delete", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("outliner.drivers_add_selected", {"type": 'D', "value": 'PRESS', "ctrl": True}, None),
        ("outliner.drivers_delete_selected", {"type": 'D', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("outliner.collection_new", {"type": 'C', "value": 'PRESS'}, None),
        ("outliner.collection_delete", {"type": 'X', "value": 'PRESS'}, None),
        ("outliner.collection_delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("object.move_to_collection", {"type": 'M', "value": 'PRESS'}, None),
        ("object.link_to_collection", {"type": 'M', "value": 'PRESS', "shift": True}, None),
        ("outliner.collection_exclude_set", {"type": 'E', "value": 'PRESS'}, None),
        ("outliner.collection_exclude_clear", {"type": 'E', "value": 'PRESS', "alt": True}, None),
        ("object.hide_view_clear", {"type": 'H', "value": 'PRESS', "alt": True},
         {"properties": [("select", False)]}),
        ("object.hide_view_set", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("object.hide_view_set", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
    ])

    return keymap


def km_uv_editor(params):
    items = []
    keymap = (
        "UV Editor",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Selection modes.
        *_template_items_editmode_mesh_select_mode(),
        ("mesh.select_mode", {"type": 'FOUR', "value": 'PRESS'}, None),
        ("wm.context_set_enum", {"type": 'ONE', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.uv_select_mode'), ("value", 'VERTEX')]}),
        ("wm.context_set_enum", {"type": 'TWO', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.uv_select_mode'), ("value", 'EDGE')]}),
        ("wm.context_set_enum", {"type": 'THREE', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.uv_select_mode'), ("value", 'FACE')]}),
        ("wm.context_set_enum", {"type": 'FOUR', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.uv_select_mode'), ("value", 'ISLAND')]}),
        ("uv.mark_seam", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
        ("uv.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("uv.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("uv.select_loop", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False)]}),
        ("uv.select_loop", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True)]}),
        ("uv.select_split", {"type": 'Y', "value": 'PRESS'}, None),
        ("uv.select_box", {"type": 'B', "value": 'PRESS'},
         {"properties": [("pinned", False)]}),
        ("uv.select_box", {"type": 'B', "value": 'PRESS', "ctrl": True},
         {"properties": [("pinned", True)]}),
        ("uv.circle_select", {"type": 'C', "value": 'PRESS'}, None),
        ("uv.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("deselect", False)]}),
        ("uv.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("deselect", True)]}),
        ("uv.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", True), ("deselect", False)]}),
        ("uv.select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("extend", True), ("deselect", False)]}),
        ("uv.select_linked", {"type": 'L', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", False), ("deselect", True)]}),
        ("uv.select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("extend", False), ("deselect", True)]}),
        ("uv.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("uv.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        *_template_items_select_actions("uv.select_all"),
        ("uv.select_pinned", {"type": 'P', "value": 'PRESS', "shift": True}, None),
        op_menu("IMAGE_MT_uvs_weldalign", {"type": 'W', "value": 'PRESS', "shift": True}),
        ("uv.stitch", {"type": 'V', "value": 'PRESS'}, None),
        ("uv.pin", {"type": 'P', "value": 'PRESS'},
         {"properties": [("clear", False)]}),
        ("uv.pin", {"type": 'P', "value": 'PRESS', "alt": True},
         {"properties": [("clear", True)]}),
        ("uv.unwrap", {"type": 'U', "value": 'PRESS'}, None),
        ("uv.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("uv.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("uv.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("uv.cursor_set", {"type": params.action_mouse, "value": 'PRESS'}, None),
        op_menu_pie("IMAGE_MT_uvs_snap_pie", {"type": 'S', "value": 'PRESS', "shift": True}),
        op_menu("IMAGE_MT_uvs_select_mode", {"type": 'TAB', "value": 'PRESS', "ctrl": True}),
        *_template_items_proportional_editing(connected=False),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.shear", {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("transform.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("wm.context_toggle", {"type": 'TAB', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.use_snap')]}),
        ("wm.context_menu_enum", {"type": 'TAB', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("data_path", 'tool_settings.snap_uv_element')]}),
    ])

    if params.legacy:
        items.extend([
            ("uv.minimize_stretch", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
            ("uv.pack_islands", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
            ("uv.average_islands_scale", {"type": 'A', "value": 'PRESS', "ctrl": True}, None),
            ("wm.context_toggle", {"type": 'Q', "value": 'PRESS'},
             {"properties": [("data_path", 'tool_settings.use_uv_sculpt')]}),
        ])

    return keymap


def km_uv_sculpt(_params):
    items = []
    keymap = (
        "UV Sculpt",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("wm.context_toggle", {"type": 'Q', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.use_uv_sculpt')]}),
        ("sculpt.uv_sculpt_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'NORMAL')]}),
        ("sculpt.uv_sculpt_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'INVERT')]}),
        ("sculpt.uv_sculpt_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'RELAX')]}),
        ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 0.9)]}),
        ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 1.0 / 0.9)]}),
        *_template_paint_radial_control("uv_sculpt"),
        ("brush.uv_sculpt_tool_set", {"type": 'S', "value": 'PRESS'},
         {"properties": [("tool", 'RELAX')]}),
        ("brush.uv_sculpt_tool_set", {"type": 'P', "value": 'PRESS'},
         {"properties": [("tool", 'PINCH')]}),
        ("brush.uv_sculpt_tool_set", {"type": 'G', "value": 'PRESS'},
         {"properties": [("tool", 'GRAB')]}),
    ])

    return keymap


# 3D View: all regions.
def km_view3d_generic(_params):
    items = []
    keymap = (
        "3D View Generic",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("view3d.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("view3d.toolshelf", {"type": 'T', "value": 'PRESS'}, None),
    ])

    return keymap


# 3D View: main region.
def km_view3d(params):
    items = []
    keymap = (
        "3D View",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Cursor.
        ("view3d.cursor3d", {"type": params.action_mouse, "value": 'CLICK'}, None),
        # Navigation.
        ("view3d.rotate", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("view3d.move", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
        ("view3d.zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("view3d.dolly", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("view3d.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS', "ctrl": True},
         {"properties": [("use_all_regions", True)]}),
        ("view3d.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'},
         {"properties": [("use_all_regions", False)]}),
        ("view3d.smoothview", {"type": 'TIMER1', "value": 'ANY', "any": True}, None),
        ("view3d.rotate", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("view3d.rotate", {"type": 'MOUSEROTATE', "value": 'ANY'}, None),
        ("view3d.move", {"type": 'TRACKPADPAN', "value": 'ANY', "shift": True}, None),
        ("view3d.zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
        ("view3d.zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
        ("view3d.zoom", {"type": 'NUMPAD_PLUS', "value": 'PRESS'},
         {"properties": [("delta", 1)]}),
        ("view3d.zoom", {"type": 'NUMPAD_MINUS', "value": 'PRESS'},
         {"properties": [("delta", -1)]}),
        ("view3d.zoom", {"type": 'EQUAL', "value": 'PRESS', "ctrl": True},
         {"properties": [("delta", 1)]}),
        ("view3d.zoom", {"type": 'MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("delta", -1)]}),
        ("view3d.zoom", {"type": 'WHEELINMOUSE', "value": 'PRESS'},
         {"properties": [("delta", 1)]}),
        ("view3d.zoom", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'},
         {"properties": [("delta", -1)]}),
        ("view3d.dolly", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True},
         {"properties": [("delta", 1)]}),
        ("view3d.dolly", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True},
         {"properties": [("delta", -1)]}),
        ("view3d.dolly", {"type": 'EQUAL', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("delta", 1)]}),
        ("view3d.dolly", {"type": 'MINUS', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("delta", -1)]}),
        ("view3d.view_center_camera", {"type": 'HOME', "value": 'PRESS'}, None),
        ("view3d.view_center_lock", {"type": 'HOME', "value": 'PRESS'}, None),
        ("view3d.view_all", {"type": 'HOME', "value": 'PRESS'},
         {"properties": [("center", False)]}),
        ("view3d.view_all", {"type": 'HOME', "value": 'PRESS', "ctrl": True},
         {"properties": [("use_all_regions", True), ("center", False)]}),
        op_menu_pie("VIEW3D_MT_view_pie", {"type": 'ACCENT_GRAVE', "value": 'PRESS'}),
        ("view3d.navigate", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "shift": True}, None),
        # Numpad views.
        ("view3d.view_camera", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("view3d.view_axis", {"type": 'NUMPAD_1', "value": 'PRESS'},
         {"properties": [("type", 'FRONT')]}),
        ("view3d.view_orbit", {"type": 'NUMPAD_2', "value": 'PRESS'},
         {"properties": [("type", 'ORBITDOWN')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_3', "value": 'PRESS'},
         {"properties": [("type", 'RIGHT')]}),
        ("view3d.view_orbit", {"type": 'NUMPAD_4', "value": 'PRESS'},
         {"properties": [("type", 'ORBITLEFT')]}),
        ("view3d.view_persportho", {"type": 'NUMPAD_5', "value": 'PRESS'}, None),
        ("view3d.view_orbit", {"type": 'NUMPAD_6', "value": 'PRESS'},
         {"properties": [("type", 'ORBITRIGHT')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_7', "value": 'PRESS'},
         {"properties": [("type", 'TOP')]}),
        ("view3d.view_orbit", {"type": 'NUMPAD_8', "value": 'PRESS'},
         {"properties": [("type", 'ORBITUP')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_1', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'BACK')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_3', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'LEFT')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_7', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'BOTTOM')]}),
        ("view3d.view_pan", {"type": 'NUMPAD_2', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PANDOWN')]}),
        ("view3d.view_pan", {"type": 'NUMPAD_4', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PANLEFT')]}),
        ("view3d.view_pan", {"type": 'NUMPAD_6', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PANRIGHT')]}),
        ("view3d.view_pan", {"type": 'NUMPAD_8', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PANUP')]}),
        ("view3d.view_roll", {"type": 'NUMPAD_4', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'LEFT')]}),
        ("view3d.view_roll", {"type": 'NUMPAD_6', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'RIGHT')]}),
        ("view3d.view_orbit", {"type": 'NUMPAD_9', "value": 'PRESS'},
         {"properties": [("angle", 3.1415927), ("type", 'ORBITRIGHT')]}),
        ("view3d.view_axis", {"type": 'NUMPAD_1', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'FRONT'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NUMPAD_3', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'RIGHT'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NUMPAD_7', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'TOP'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NUMPAD_1', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'BACK'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NUMPAD_3', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'LEFT'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NUMPAD_7', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'BOTTOM'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'EVT_TWEAK_M', "value": 'NORTH', "alt": True},
         {"properties": [("type", 'TOP'), ("relative", True)]}),
        ("view3d.view_axis", {"type": 'EVT_TWEAK_M', "value": 'SOUTH', "alt": True},
         {"properties": [("type", 'BOTTOM'), ("relative", True)]}),
        ("view3d.view_axis", {"type": 'EVT_TWEAK_M', "value": 'EAST', "alt": True},
         {"properties": [("type", 'RIGHT'), ("relative", True)]}),
        ("view3d.view_axis", {"type": 'EVT_TWEAK_M', "value": 'WEST', "alt": True},
         {"properties": [("type", 'LEFT'), ("relative", True)]}),
        ("view3d.ndof_orbit_zoom", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
        ("view3d.ndof_orbit", {"type": 'NDOF_MOTION', "value": 'ANY', "ctrl": True}, None),
        ("view3d.ndof_pan", {"type": 'NDOF_MOTION', "value": 'ANY', "shift": True}, None),
        ("view3d.ndof_all", {"type": 'NDOF_MOTION', "value": 'ANY', "shift": True, "ctrl": True}, None),
        ("view3d.view_selected", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'},
         {"properties": [("use_all_regions", False)]}),
        ("view3d.view_roll", {"type": 'NDOF_BUTTON_ROLL_CCW', "value": 'PRESS'},
         {"properties": [("type", 'LEFT')]}),
        ("view3d.view_roll", {"type": 'NDOF_BUTTON_ROLL_CCW', "value": 'PRESS'},
         {"properties": [("type", 'RIGHT')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_FRONT', "value": 'PRESS'},
         {"properties": [("type", 'FRONT')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_BACK', "value": 'PRESS'},
         {"properties": [("type", 'BACK')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_LEFT', "value": 'PRESS'},
         {"properties": [("type", 'LEFT')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_RIGHT', "value": 'PRESS'},
         {"properties": [("type", 'RIGHT')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_TOP', "value": 'PRESS'},
         {"properties": [("type", 'TOP')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_BOTTOM', "value": 'PRESS'},
         {"properties": [("type", 'BOTTOM')]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_FRONT', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'FRONT'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_RIGHT', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'RIGHT'), ("align_active", True)]}),
        ("view3d.view_axis", {"type": 'NDOF_BUTTON_TOP', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'TOP'), ("align_active", True)]}),
        # Selection.
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", False),
             ("center", False),
             ("enumerate", False),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", True),
             ("center", False),
             ("enumerate", False),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", False),
             ("center", True),
             ("enumerate", False),
             ("object", True),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", False),
             ("center", False),
             ("enumerate", True),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [
             ("extend", True),
             ("deselect", False),
             ("toggle", True),
             ("center", True),
             ("enumerate", False),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", False),
             ("center", True),
             ("enumerate", True),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", True),
             ("center", False),
             ("enumerate", True),
             ("object", False),
         ], },),
        ("view3d.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [
             ("extend", False),
             ("deselect", False),
             ("toggle", True),
             ("center", True),
             ("enumerate", True),
             ("object", False),
         ], },),
        ("view3d.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        # Borders.
        ("view3d.clip_border", {"type": 'B', "value": 'PRESS', "alt": True}, None),
        ("view3d.zoom_border", {"type": 'B', "value": 'PRESS', "shift": True}, None),
        ("view3d.render_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
        ("view3d.clear_render_border", {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        # Cameras.
        ("view3d.camera_to_view", {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("view3d.object_as_camera", {"type": 'NUMPAD_0', "value": 'PRESS', "ctrl": True}, None),
        # Copy/paste.
        ("view3d.copybuffer", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("view3d.pastebuffer", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        # Menus.
        op_menu_pie("VIEW3D_MT_snap_pie", {"type": 'S', "value": 'PRESS', "shift": True}),
        op_menu_pie("VIEW3D_MT_pivot_pie", {"type": 'PERIOD', "value": 'PRESS'}),
        op_menu_pie("VIEW3D_MT_orientations_pie", {"type": 'COMMA', "value": 'PRESS'}),
        # Transform.
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.bend", {"type": 'W', "value": 'PRESS', "shift": True}, None),
        ("transform.tosphere", {"type": 'S', "value": 'PRESS', "shift": True, "alt": True}, None),
        ("transform.shear", {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("transform.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("wm.context_toggle", {"type": 'TAB', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.use_snap')]}),
        op_panel("VIEW3D_PT_snapping", {"type": 'TAB', "value": 'PRESS', "shift": True, "ctrl": True}, [("keep_open", False)]),
        ("object.transform_axis_target", {"type": 'T', "value": 'PRESS', "shift": True}, None),
        ("transform.skin_resize", {"type": 'A', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("view3d.copybuffer", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("view3d.pastebuffer", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    if not params.legacy:
        # New pie menus.
        items.extend([
            ("wm.context_toggle", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True},
             {"properties": [("data_path", 'space_data.show_gizmo_tool')]}),
            op_menu_pie("VIEW3D_MT_pivot_pie", {"type": 'PERIOD', "value": 'PRESS'}),
            op_menu_pie("VIEW3D_MT_orientations_pie", {"type": 'COMMA', "value": 'PRESS'}),
            op_menu_pie("VIEW3D_MT_shading_pie", {"type": 'Z', "value": 'PRESS'}),
            ("view3d.toggle_shading", {"type": 'Z', "value": 'PRESS', "alt": True},
             {"properties": [("type", 'MATERIAL')]}),
            ("view3d.toggle_shading", {"type": 'Z', "value": 'PRESS', "shift": True},
             {"properties": [("type", 'RENDERED')]}),
        ])
    else:
        items.extend([
            # Old navigation.
            ("view3d.view_lock_to_active", {"type": 'NUMPAD_PERIOD', "value": 'PRESS', "shift": True}, None),
            ("view3d.view_lock_clear", {"type": 'NUMPAD_PERIOD', "value": 'PRESS', "alt": True}, None),
            ("view3d.navigate", {"type": 'F', "value": 'PRESS', "shift": True}, None),
            ("view3d.zoom_camera_1_to_1", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "shift": True}, None),
            ("view3d.view_center_cursor", {"type": 'HOME', "value": 'PRESS', "alt": True}, None),
            ("view3d.view_center_pick", {"type": 'F', "value": 'PRESS', "alt": True}, None),
            ("view3d.view_all", {"type": 'C', "value": 'PRESS', "shift": True},
             {"properties": [("center", True)]}),
            ("view3d.view_pan", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True},
             {"properties": [("type", 'PANRIGHT')]}),
            ("view3d.view_pan", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True},
             {"properties": [("type", 'PANLEFT')]}),
            ("view3d.view_pan", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True},
             {"properties": [("type", 'PANUP')]}),
            ("view3d.view_pan", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True},
             {"properties": [("type", 'PANDOWN')]}),
            ("view3d.view_orbit", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
             {"properties": [("type", 'ORBITLEFT')]}),
            ("view3d.view_orbit", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
             {"properties": [("type", 'ORBITRIGHT')]}),
            ("view3d.view_orbit", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("type", 'ORBITUP')]}),
            ("view3d.view_orbit", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("type", 'ORBITDOWN')]}),
            ("view3d.view_roll", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
             {"properties": [("type", 'LEFT')]}),
            ("view3d.view_roll", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
             {"properties": [("type", 'RIGHT')]}),
            ("transform.create_orientation", {"type": 'SPACE', "value": 'PRESS', "ctrl": True, "alt": True},
             {"properties": [("use", True)]}),
            ("transform.translate", {"type": 'T', "value": 'PRESS', "shift": True},
             {"properties": [("texture_space", True)]}),
            ("transform.resize", {"type": 'T', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("texture_space", True)]}),
            # Old pivot.
            ("wm.context_set_enum", {"type": 'COMMA', "value": 'PRESS'},
             {"properties": [("data_path", 'space_data.pivot_point'), ("value", 'BOUNDING_BOX_CENTER')]}),
            ("wm.context_set_enum", {"type": 'COMMA', "value": 'PRESS', "ctrl": True},
             {"properties": [("data_path", 'space_data.pivot_point'), ("value", 'MEDIAN_POINT')]}),
            ("wm.context_toggle", {"type": 'COMMA', "value": 'PRESS', "alt": True},
             {"properties": [("data_path", 'tool_settings.use_transform_pivot_point_align')]}),
            ("wm.context_toggle", {"type": 'SPACE', "value": 'PRESS', "ctrl": True},
             {"properties": [("data_path", 'space_data.show_gizmo_tool')]}),
            ("wm.context_set_enum", {"type": 'PERIOD', "value": 'PRESS'},
             {"properties": [("data_path", 'space_data.pivot_point'), ("value", 'CURSOR')]}),
            ("wm.context_set_enum", {"type": 'PERIOD', "value": 'PRESS', "ctrl": True},
             {"properties": [("data_path", 'space_data.pivot_point'), ("value", 'INDIVIDUAL_ORIGINS')]}),
            ("wm.context_set_enum", {"type": 'PERIOD', "value": 'PRESS', "alt": True},
             {"properties": [("data_path", 'space_data.pivot_point'), ("value", 'ACTIVE_ELEMENT')]}),
            # Old shading.
            ("wm.context_toggle_enum", {"type": 'Z', "value": 'PRESS'},
             {"properties": [("data_path", 'space_data.shading.type'), ("value_1", 'WIREFRAME'), ("value_2", 'SOLID')]}),
            ("wm.context_toggle_enum", {"type": 'Z', "value": 'PRESS', "shift": True},
             {"properties": [("data_path", 'space_data.shading.type'), ("value_1", 'RENDERED'), ("value_2", 'SOLID')]}),
            ("wm.context_toggle_enum", {"type": 'Z', "value": 'PRESS', "alt": True},
             {"properties": [("data_path", 'space_data.shading.type'), ("value_1", 'MATERIAL'), ("value_2", 'SOLID')]}),
        ])

    return keymap


def km_mask_editing(params):
    items = []
    keymap = (
        "Mask Editing",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("mask.new", {"type": 'N', "value": 'PRESS', "alt": True}, None),
        op_menu("MASK_MT_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        op_menu_pie("VIEW3D_MT_proportional_editing_falloff_pie", {"type": 'O', "value": 'PRESS', "shift": True}),
        ("wm.context_toggle", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.use_proportional_edit_mask')]}),
        ("mask.add_vertex_slide", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True}, None),
        ("mask.add_feather_vertex_slide", {"type": params.action_mouse, "value": 'PRESS', "shift": True}, None),
        ("mask.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("mask.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("mask.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False), ("deselect", False), ("toggle", False)]}),
        ("mask.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", False), ("deselect", False), ("toggle", True)]}),
        *_template_items_select_actions("mask.select_all"),
        ("mask.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("mask.select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("deselect", False)]}),
        ("mask.select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("deselect", True)]}),
        ("mask.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("mask.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        ("mask.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True},
         {"properties": [("deselect", False)]}),
        ("mask.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("deselect", True)]}),
        ("mask.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("mask.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("mask.hide_view_clear", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("mask.hide_view_set", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("mask.hide_view_set", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("clip.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", False)]}),
        ("mask.cyclic_toggle", {"type": 'C', "value": 'PRESS', "alt": True}, None),
        ("mask.slide_point", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("mask.slide_spline_curvature", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("mask.handle_type_set", {"type": 'V', "value": 'PRESS'}, None),
        ("mask.normals_make_consistent", {"type": 'N', "value": 'PRESS', "ctrl" if params.legacy else "shift": True}, None),
        ("mask.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        ("mask.parent_clear", {"type": 'P', "value": 'PRESS', "alt": True}, None),
        ("mask.shape_key_insert", {"type": 'I', "value": 'PRESS'}, None),
        ("mask.shape_key_clear", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("mask.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("mask.copy_splines", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("mask.paste_splines", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("uv.cursor_set", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.transform", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'MASK_SHRINKFATTEN')]}),
    ])

    return keymap


def km_markers(params):
    items = []
    keymap = (
        "Markers",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
        ("marker.move", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("marker.duplicate", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("marker.select", {"type": params.select_mouse, "value": 'PRESS'}, None),
        ("marker.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("marker.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", False), ("camera", True)]}),
        ("marker.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", True), ("camera", True)]}),
        ("marker.select_box", {"type": 'B', "value": 'PRESS'}, None),
        *_template_items_select_actions("marker.select_all"),
        ("marker.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("marker.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("marker.rename", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("marker.move", {"type": 'G', "value": 'PRESS'}, None),
        ("marker.camera_bind", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_graph_editor_generic(_params):
    items = []
    keymap = (
        "Graph Editor Generic",
        {"space_type": 'GRAPH_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("graph.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("graph.extrapolation_type", {"type": 'E', "value": 'PRESS', "shift": True}, None),
        ("anim.channels_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
        ("graph.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("graph.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("graph.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
    ])

    return keymap


def km_graph_editor(params):
    items = []
    keymap = (
        "Graph Editor",
        {"space_type": 'GRAPH_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("wm.context_toggle", {"type": 'H', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.show_handles')]}),
        ("graph.cursor_set", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False), ("column", False), ("curves", False)]}),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False), ("column", True), ("curves", False)]}),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True), ("column", False), ("curves", False)]}),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True), ("column", True), ("curves", False)]}),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("extend", False), ("column", False), ("curves", True)]}),
        ("graph.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("extend", True), ("column", False), ("curves", True)]}),
        ("graph.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", False)]}),
        ("graph.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", True)]}),
        ("graph.select_leftright", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'LEFT'), ("extend", False)]}),
        ("graph.select_leftright", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'RIGHT'), ("extend", False)]}),
        *_template_items_select_actions("graph.select_all"),
        ("graph.select_box", {"type": 'B', "value": 'PRESS'},
         {"properties": [("axis_range", False), ("include_handles", False)]}),
        ("graph.select_box", {"type": 'B', "value": 'PRESS', "alt": True},
         {"properties": [("axis_range", True), ("include_handles", False)]}),
        ("graph.select_box", {"type": 'B', "value": 'PRESS', "ctrl": True},
         {"properties": [("axis_range", False), ("include_handles", True)]}),
        ("graph.select_box", {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("axis_range", True), ("include_handles", True)]}),
        ("graph.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("deselect", False)]}),
        ("graph.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("deselect", True)]}),
        ("graph.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        ("graph.select_column", {"type": 'K', "value": 'PRESS'},
         {"properties": [("mode", 'KEYS')]}),
        ("graph.select_column", {"type": 'K', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'CFRA')]}),
        ("graph.select_column", {"type": 'K', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'MARKERS_COLUMN')]}),
        ("graph.select_column", {"type": 'K', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'MARKERS_BETWEEN')]}),
        ("graph.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("graph.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("graph.select_linked", {"type": 'L', "value": 'PRESS'}, None),
        ("graph.frame_jump", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        op_menu_pie("GRAPH_MT_snap_pie", {"type": 'S', "value": 'PRESS', "shift": True}),
        ("graph.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("graph.handle_type", {"type": 'V', "value": 'PRESS'}, None),
        ("graph.interpolation_type", {"type": 'T', "value": 'PRESS'}, None),
        ("graph.easing_type", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
        ("graph.smooth", {"type": 'O', "value": 'PRESS', "alt": True}, None),
        ("graph.sample", {"type": 'O', "value": 'PRESS', "shift": True, "alt": True}, None),
        ("graph.bake", {"type": 'C', "value": 'PRESS', "alt": True}, None),
        op_menu("GRAPH_MT_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("GRAPH_MT_delete", {"type": 'DEL', "value": 'PRESS'}),
        op_menu("GRAPH_MT_specials", {"type": 'W', "value": 'PRESS'}),
        ("graph.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("graph.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
        ("graph.click_insert", {"type": params.action_mouse, "value": 'CLICK', "ctrl": True},
         {"properties": [("extend", False)]}),
        ("graph.click_insert", {"type": params.action_mouse, "value": 'CLICK', "shift": True, "ctrl": True},
         {"properties": [("extend", True)]}),
        ("graph.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("graph.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("graph.paste", {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("flipped", True)]}),
        ("graph.previewrange_set", {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("graph.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("graph.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("graph.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("graph.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("graph.fmodifier_add", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("only_active", False)]}),
        ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.transform", {"type": 'E', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_EXTEND')]}),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("wm.context_toggle", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.use_proportional_fcurve')]}),
        op_menu_pie("VIEW3D_MT_proportional_editing_falloff_pie", {"type": 'O', "value": 'PRESS', "shift": True}),
        op_menu_pie("GRAPH_MT_pivot_pie", {"type": 'PERIOD', "value": 'PRESS'}),
        ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
        ("marker.rename", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("graph.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("graph.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
            ("graph.paste", {"type": 'V', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("flipped", True)]}),
        ])

    return keymap


def km_image_generic(_params):
    items = []
    keymap = (
        "Image Generic",
        {"space_type": 'IMAGE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("image.new", {"type": 'N', "value": 'PRESS', "alt": True}, None),
        ("image.open", {"type": 'O', "value": 'PRESS', "alt": True}, None),
        ("image.reload", {"type": 'R', "value": 'PRESS', "alt": True}, None),
        ("image.read_viewlayers", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
        ("image.save", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        ("image.save_as", {"type": 'S', "value": 'PRESS', "shift": True}, None),
        ("image.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("image.toolshelf", {"type": 'T', "value": 'PRESS'}, None),
        op_menu("IMAGE_MT_specials", {"type": 'W', "value": 'PRESS'}),
        ("image.cycle_render_slot", {"type": 'J', "value": 'PRESS'}, None),
        ("image.cycle_render_slot", {"type": 'J', "value": 'PRESS', "alt": True},
         {"properties": [("reverse", True)]}),
    ])

    return keymap


def km_image(params):
    items = []
    keymap = (
        "Image",
        {"space_type": 'IMAGE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("image.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("image.view_all", {"type": 'HOME', "value": 'PRESS', "shift": True},
         {"properties": [("fit_view", True)]}),
        ("image.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("image.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("image.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
        ("image.view_pan", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("image.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("image.view_ndof", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
        ("image.view_zoom_in", {"type": 'WHEELINMOUSE', "value": 'PRESS'}, None),
        ("image.view_zoom_out", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'}, None),
        ("image.view_zoom_in", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("image.view_zoom_out", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("image.view_zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("image.view_zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
        ("image.view_zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
        ("image.view_zoom_border", {"type": 'B', "value": 'PRESS', "shift": True}, None),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 8.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 4.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 2.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 8.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 4.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 2.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_1', "value": 'PRESS'},
         {"properties": [("ratio", 1.0)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS'},
         {"properties": [("ratio", 0.5)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS'},
         {"properties": [("ratio", 0.25)]}),
        ("image.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS'},
         {"properties": [("ratio", 0.125)]}),
        ("image.change_frame", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("image.sample", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("image.curves_point_set", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("point", 'BLACK_POINT')]}),
        ("image.curves_point_set", {"type": params.action_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("point", 'WHITE_POINT')]}),
        ("object.mode_set", {"type": 'TAB', "value": 'PRESS'},
         {"properties": [("mode", 'EDIT'), ("toggle", True)]}),
        *(
            (("wm.context_set_int",
              {"type": NUMBERS_1[i], "value": 'PRESS'},
              {"properties": [("data_path", 'space_data.image.render_slots.active_index'), ("value", i)]})
             for i in range(9)
             )
        ),
        op_menu_pie("IMAGE_MT_pivot_pie", {"type": 'PERIOD', "value": 'PRESS'}),
        ("image.render_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
        ("image.clear_render_border", {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True}, None),
    ])

    return keymap


def km_node_generic(_params):
    items = []
    keymap = (
        "Node Generic",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("node.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("node.toolbar", {"type": 'T', "value": 'PRESS'}, None),
    ])

    return keymap


def km_node_editor(params):
    items = []
    keymap = (
        "Node Editor",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("node.select", {"type": params.action_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("extend", False)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.action_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("extend", True)]}),
        ("node.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("extend", True)]}),
        ("node.select_box", {"type": 'EVT_TWEAK_S', "value": 'ANY'},
         {"properties": [("tweak", True)]}),
        ("node.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True},
         {"properties": [("deselect", False)]}),
        ("node.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("deselect", True)]}),
        ("node.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        ("node.link", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("detach", False)]}),
        ("node.link", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("detach", True)]}),
        ("node.resize", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("node.add_reroute", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, None),
        ("node.links_cut", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("node.select_link_viewer", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("node.backimage_move", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "alt": True}, None),
        ("node.backimage_zoom", {"type": 'V', "value": 'PRESS'},
         {"properties": [("factor", 1.0 / 1.2)]}),
        ("node.backimage_zoom", {"type": 'V', "value": 'PRESS', "alt": True},
         {"properties": [("factor", 1.2)]}),
        ("node.backimage_fit", {"type": 'HOME', "value": 'PRESS', "alt": True}, None),
        ("node.backimage_sample", {"type": params.action_mouse, "value": 'PRESS', "alt": True}, None),
        op_menu("NODE_MT_specials", {"type": 'W', "value": 'PRESS'}),
        ("node.link_make", {"type": 'F', "value": 'PRESS'},
         {"properties": [("replace", False)]}),
        ("node.link_make", {"type": 'F', "value": 'PRESS', "shift": True},
         {"properties": [("replace", True)]}),
        op_menu("NODE_MT_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        ("node.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("node.duplicate_move_keep_inputs", {"type": 'D', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("node.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        ("node.detach", {"type": 'P', "value": 'PRESS', "alt": True}, None),
        ("node.join", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
        ("node.hide_toggle", {"type": 'H', "value": 'PRESS'}, None),
        ("node.mute_toggle", {"type": 'M', "value": 'PRESS'}, None),
        ("node.preview_toggle", {"type": 'H', "value": 'PRESS', "shift": True}, None),
        ("node.hide_socket_toggle", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
        ("node.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("node.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("node.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("node.select_box", {"type": 'B', "value": 'PRESS'},
         {"properties": [("tweak", False)]}),
        ("node.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("node.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("node.delete_reconnect", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("node.delete_reconnect", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
        *_template_items_select_actions("node.select_all"),
        ("node.select_linked_to", {"type": 'L', "value": 'PRESS', "shift": True}, None),
        ("node.select_linked_from", {"type": 'L', "value": 'PRESS'}, None),
        ("node.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True},
         {"properties": [("extend", False)]}),
        ("node.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", True)]}),
        ("node.select_same_type_step", {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("prev", False)]}),
        ("node.select_same_type_step", {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("prev", True)]}),
        ("node.find_node", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
        ("node.group_make", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("node.group_ungroup", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("node.group_separate", {"type": 'P', "value": 'PRESS'}, None),
        ("node.group_edit", {"type": 'TAB', "value": 'PRESS'},
         {"properties": [("exit", False)]}),
        ("node.group_edit", {"type": 'TAB', "value": 'PRESS', "ctrl": True},
         {"properties": [("exit", True)]}),
        ("node.read_viewlayers", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
        ("node.render_changed", {"type": 'Z', "value": 'PRESS'}, None),
        ("node.clipboard_copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("node.clipboard_paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("node.viewer_border", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
        ("node.clear_viewer_border", {"type": 'B', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("node.translate_attach", {"type": 'G', "value": 'PRESS'}, None),
        ("node.translate_attach", {"type": 'EVT_TWEAK_A', "value": 'ANY'}, None),
        ("node.translate_attach", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.translate", {"type": 'G', "value": 'PRESS'},
         {"properties": [("release_confirm", True)]}),
        ("transform.translate", {"type": 'EVT_TWEAK_A', "value": 'ANY'},
         {"properties": [("release_confirm", True)]}),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'},
         {"properties": [("release_confirm", True)]}),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("node.move_detach_links", {"type": 'D', "value": 'PRESS', "alt": True}, None),
        ("node.move_detach_links_release", {"type": 'EVT_TWEAK_A', "value": 'ANY', "alt": True}, None),
        ("node.move_detach_links", {"type": 'EVT_TWEAK_S', "value": 'ANY', "alt": True}, None),
        ("wm.context_toggle", {"type": 'TAB', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.use_snap')]}),
        ("wm.context_menu_enum", {"type": 'TAB', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("data_path", 'tool_settings.snap_node_element')]}),
    ])

    if params.apple:
        items.extend([
            ("node.clipboard_copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("node.clipboard_paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_info(params):
    items = []
    keymap = (
        "Info",
        {"space_type": 'INFO', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("info.select_pick", {"type": params.select_mouse, "value": 'PRESS'}, None),
        ("info.select_all_toggle", {"type": 'A', "value": 'PRESS'}, None),
        ("info.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("info.report_replay", {"type": 'R', "value": 'PRESS'}, None),
        ("info.report_delete", {"type": 'X', "value": 'PRESS'}, None),
        ("info.report_delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("info.report_copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("info.report_copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_file_browser(_params):
    items = []
    keymap = (
        "File Browser",
        {"space_type": 'FILE_BROWSER', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("file.parent", {"type": 'UP_ARROW', "value": 'PRESS', "alt": True}, None),
        ("file.previous", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True}, None),
        ("file.next", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True}, None),
        ("file.refresh", {"type": 'R', "value": 'PRESS'}, None),
        ("file.parent", {"type": 'P', "value": 'PRESS'}, None),
        ("file.previous", {"type": 'BACK_SPACE', "value": 'PRESS'}, None),
        ("file.next", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True}, None),
        ("wm.context_toggle", {"type": 'H', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.params.show_hidden')]}),
        ("file.directory_new", {"type": 'I', "value": 'PRESS'}, None),
        ("file.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("file.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("file.smoothscroll", {"type": 'TIMER1', "value": 'ANY', "any": True}, None),
        ("file.bookmark_toggle", {"type": 'T', "value": 'PRESS'}, None),
        ("file.bookmark_add", {"type": 'B', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_file_browser_main(_params):
    items = []
    keymap = (
        "File Browser Main",
        {"space_type": 'FILE_BROWSER', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("file.execute", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'},
         {"properties": [("need_active", True)]}),
        ("file.refresh", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("file.select", {"type": 'LEFTMOUSE', "value": 'CLICK'}, None),
        ("file.select", {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True},
         {"properties": [("extend", True)]}),
        ("file.select", {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True, "ctrl": True},
         {"properties": [("extend", True), ("fill", True)]}),
        ("file.select", {"type": 'RIGHTMOUSE', "value": 'CLICK'},
         {"properties": [("open", False)]}),
        ("file.select", {"type": 'RIGHTMOUSE', "value": 'CLICK', "shift": True},
         {"properties": [("extend", True), ("open", False)]}),
        ("file.select", {"type": 'RIGHTMOUSE', "value": 'CLICK', "alt": True},
         {"properties": [("extend", True), ("fill", True), ("open", False)]}),
        ("file.select_walk", {"type": 'UP_ARROW', "value": 'PRESS'},
         {"properties": [("direction", 'UP')]}),
        ("file.select_walk", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'UP'), ("extend", True)]}),
        ("file.select_walk", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'UP'), ("extend", True), ("fill", True)]}),
        ("file.select_walk", {"type": 'DOWN_ARROW', "value": 'PRESS'},
         {"properties": [("direction", 'DOWN')]}),
        ("file.select_walk", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'DOWN'), ("extend", True)]}),
        ("file.select_walk", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'DOWN'), ("extend", True), ("fill", True)]}),
        ("file.select_walk", {"type": 'LEFT_ARROW', "value": 'PRESS'},
         {"properties": [("direction", 'LEFT')]}),
        ("file.select_walk", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'LEFT'), ("extend", True)]}),
        ("file.select_walk", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'LEFT'), ("extend", True), ("fill", True)]}),
        ("file.select_walk", {"type": 'RIGHT_ARROW', "value": 'PRESS'},
         {"properties": [("direction", 'RIGHT')]}),
        ("file.select_walk", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'RIGHT'), ("extend", True)]}),
        ("file.select_walk", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'RIGHT'), ("extend", True), ("fill", True)]}),
        ("file.previous", {"type": 'BUTTON4MOUSE', "value": 'CLICK'}, None),
        ("file.next", {"type": 'BUTTON5MOUSE', "value": 'CLICK'}, None),
        ("file.select_all", {"type": 'A', "value": 'PRESS'}, None),
        ("file.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("file.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, None),
        ("file.rename", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("file.highlight", {"type": 'MOUSEMOVE', "value": 'ANY', "any": True}, None),
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS'},
         {"properties": [("increment", 1)]}),
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True},
         {"properties": [("increment", 10)]}),
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("increment", 100)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS'},
         {"properties": [("increment", -1)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True},
         {"properties": [("increment", -10)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("increment", -100)]}),
    ])

    return keymap


def km_file_browser_buttons(_params):
    items = []
    keymap = (
        "File Browser Buttons",
        {"space_type": 'FILE_BROWSER', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS'},
         {"properties": [("increment", 1)]}),
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True},
         {"properties": [("increment", 10)]}),
        ("file.filenum", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("increment", 100)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS'},
         {"properties": [("increment", -1)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True},
         {"properties": [("increment", -10)]}),
        ("file.filenum", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("increment", -100)]}),
    ])

    return keymap


def km_dopesheet_generic(_params):
    items = []
    keymap = (
        "Dopesheet Generic",
        {"space_type": 'DOPESHEET_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("action.properties", {"type": 'N', "value": 'PRESS'}, None),
    ])

    return keymap


def km_dopesheet(params):
    items = []
    keymap = (
        "Dopesheet",
        {"space_type": 'DOPESHEET_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False), ("column", False), ("channel", False)]}),
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False), ("column", True), ("channel", False)]}),
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True), ("column", False), ("channel", False)]}),
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True), ("column", True), ("channel", False)]}),
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("extend", False), ("column", False), ("channel", True)]}),
        ("action.clickselect", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("extend", True), ("column", False), ("channel", True)]}),
        ("action.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", False)]}),
        ("action.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", True)]}),
        ("action.select_leftright", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'LEFT'), ("extend", False)]}),
        ("action.select_leftright", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'RIGHT'), ("extend", False)]}),
        *_template_items_select_actions("action.select_all"),
        ("action.select_box", {"type": 'B', "value": 'PRESS'},
         {"properties": [("axis_range", False)]}),
        ("action.select_box", {"type": 'B', "value": 'PRESS', "alt": True},
         {"properties": [("axis_range", True)]}),
        ("action.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("deselect", False)]}),
        ("action.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("deselect", True)]}),
        ("action.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        ("action.select_column", {"type": 'K', "value": 'PRESS'},
         {"properties": [("mode", 'KEYS')]}),
        ("action.select_column", {"type": 'K', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'CFRA')]}),
        ("action.select_column", {"type": 'K', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'MARKERS_COLUMN')]}),
        ("action.select_column", {"type": 'K', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'MARKERS_BETWEEN')]}),
        ("action.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("action.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("action.select_linked", {"type": 'L', "value": 'PRESS'}, None),
        ("action.frame_jump", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        op_menu_pie("DOPESHEET_MT_snap_pie", {"type": 'S', "value": 'PRESS', "shift": True}),
        ("action.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("action.handle_type", {"type": 'V', "value": 'PRESS'}, None),
        ("action.interpolation_type", {"type": 'T', "value": 'PRESS'}, None),
        ("action.extrapolation_type", {"type": 'E', "value": 'PRESS', "shift": True}, None),
        ("action.keyframe_type", {"type": 'R', "value": 'PRESS'}, None),
        op_menu("DOPESHEET_MT_specials", {"type": 'W', "value": 'PRESS'}),
        ("action.sample", {"type": 'O', "value": 'PRESS', "shift": True, "alt": True}, None),
        op_menu("DOPESHEET_MT_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("DOPESHEET_MT_delete", {"type": 'DEL', "value": 'PRESS'}),
        ("action.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("action.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
        ("action.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("action.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("action.paste", {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("flipped", True)]}),
        ("action.previewrange_set", {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("action.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("action.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("action.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("action.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
        ("anim.channels_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
        ("transform.transform", {"type": 'G', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_TRANSLATE')]}),
        ("transform.transform", {"type": 'EVT_TWEAK_S', "value": 'ANY'},
         {"properties": [("mode", 'TIME_TRANSLATE')]}),
        ("transform.transform", {"type": 'E', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_EXTEND')]}),
        ("transform.transform", {"type": 'S', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_SCALE')]}),
        ("transform.transform", {"type": 'T', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'TIME_SLIDE')]}),
        ("wm.context_toggle", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.use_proportional_action')]}),
        op_menu_pie("VIEW3D_MT_proportional_editing_falloff_pie", {"type": 'O', "value": 'PRESS', "shift": True}),
        ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
        ("marker.rename", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("action.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("action.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
            ("action.paste", {"type": 'V', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("flipped", True)]}),
        ])

    return keymap


def km_nla_generic(_params):
    items = []
    keymap = (
        "NLA Generic",
        {"space_type": 'NLA_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("nla.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("nla.tweakmode_enter", {"type": 'TAB', "value": 'PRESS'}, None),
        ("nla.tweakmode_exit", {"type": 'TAB', "value": 'PRESS'}, None),
        ("nla.tweakmode_enter", {"type": 'TAB', "value": 'PRESS', "shift": True},
         {"properties": [("isolate_action", True)]}),
        ("nla.tweakmode_exit", {"type": 'TAB', "value": 'PRESS', "shift": True},
         {"properties": [("isolate_action", True)]}),
        ("anim.channels_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_nla_channels(_params):
    items = []
    keymap = (
        "NLA Channels",
        {"space_type": 'NLA_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("nla.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("nla.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("nla.tracks_add", {"type": 'A', "value": 'PRESS', "shift": True},
         {"properties": [("above_selected", False)]}),
        ("nla.tracks_add", {"type": 'A', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("above_selected", True)]}),
        ("nla.tracks_delete", {"type": 'X', "value": 'PRESS'}, None),
        ("nla.tracks_delete", {"type": 'DEL', "value": 'PRESS'}, None),
    ])

    return keymap


def km_nla_editor(params):
    items = []
    keymap = (
        "NLA Editor",
        {"space_type": 'NLA_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("nla.click_select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("nla.click_select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("nla.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", False)]}),
        ("nla.select_leftright", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("mode", 'CHECK'), ("extend", True)]}),
        ("nla.select_leftright", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'LEFT'), ("extend", False)]}),
        ("nla.select_leftright", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("mode", 'RIGHT'), ("extend", False)]}),
        *_template_items_select_actions("nla.select_all"),
        ("nla.select_box", {"type": 'B', "value": 'PRESS'},
         {"properties": [("axis_range", False)]}),
        ("nla.select_box", {"type": 'B', "value": 'PRESS', "alt": True},
         {"properties": [("axis_range", True)]}),
        ("nla.previewrange_set", {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("nla.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("nla.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("nla.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("nla.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("nla.actionclip_add", {"type": 'A', "value": 'PRESS', "shift": True}, None),
        ("nla.transition_add", {"type": 'T', "value": 'PRESS', "shift": True}, None),
        ("nla.soundclip_add", {"type": 'K', "value": 'PRESS', "shift": True}, None),
        ("nla.meta_add", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("nla.meta_remove", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("nla.duplicate", {"type": 'D', "value": 'PRESS', "shift": True},
         {"properties": [("linked", False)]}),
        ("nla.duplicate", {"type": 'D', "value": 'PRESS', "alt": True},
         {"properties": [("linked", True)]}),
        ("nla.make_single_user", {"type": 'U', "value": 'PRESS'}, None),
        ("nla.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("nla.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("nla.split", {"type": 'Y', "value": 'PRESS'}, None),
        ("nla.mute_toggle", {"type": 'H', "value": 'PRESS'}, None),
        ("nla.swap", {"type": 'F', "value": 'PRESS', "alt": True}, None),
        ("nla.move_up", {"type": 'PAGE_UP', "value": 'PRESS'}, None),
        ("nla.move_down", {"type": 'PAGE_DOWN', "value": 'PRESS'}, None),
        ("nla.apply_scale", {"type": 'A', "value": 'PRESS', "ctrl": True}, None),
        ("nla.clear_scale", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        op_menu_pie("NLA_MT_snap_pie", {"type": 'S', "value": 'PRESS', "shift": True}),
        ("nla.fmodifier_add", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("transform.transform", {"type": 'G', "value": 'PRESS'},
         {"properties": [("mode", 'TRANSLATION')]}),
        ("transform.transform", {"type": 'EVT_TWEAK_S', "value": 'ANY'},
         {"properties": [("mode", 'TRANSLATION')]}),
        ("transform.transform", {"type": 'E', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_EXTEND')]}),
        ("transform.transform", {"type": 'S', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_SCALE')]}),
        ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
        ("marker.rename", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_text_generic(params):
    items = []
    keymap = (
        "Text Generic",
        {"space_type": 'TEXT_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("text.start_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
        ("text.jump", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
        ("text.find", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("text.replace", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
        ("text.properties", {"type": 'T', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("text.start_find", {"type": 'F', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_text(params):
    items = []
    keymap = (
        "Text",
        {"space_type": 'TEXT_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    if params.apple:
        items.extend([
            ("text.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'LINE_BEGIN')]}),
            ("text.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'LINE_END')]}),
            ("text.move", {"type": 'UP_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'FILE_TOP')]}),
            ("text.move", {"type": 'DOWN_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'FILE_BOTTOM')]}),
            ("text.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("type", 'LINE_BEGIN')]}),
            ("text.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("type", 'LINE_END')]}),
            ("text.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("type", 'PREVIOUS_WORD')]}),
            ("text.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("type", 'NEXT_WORD')]}),
            ("text.move_select", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("type", 'FILE_TOP')]}),
            ("text.move_select", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("type", 'FILE_BOTTOM')]}),
            ("text.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "alt": True},
             {"properties": [("type", 'PREVIOUS_WORD')]}),
            ("text.save", {"type": 'S', "value": 'PRESS', "alt": True, "oskey": True}, None),
            ("text.save_as", {"type": 'S', "value": 'PRESS', "shift": True, "alt": True, "oskey": True}, None),
            ("text.cut", {"type": 'X', "value": 'PRESS', "oskey": True}, None),
            ("text.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("text.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
            ("text.find_set_selected", {"type": 'E', "value": 'PRESS', "oskey": True}, None),
            ("text.select_all", {"type": 'A', "value": 'PRESS', "oskey": True}, None),
            ("text.select_line", {"type": 'A', "value": 'PRESS', "shift": True, "oskey": True}, None),
        ])

    items.extend([
        ("text.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("text.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("wm.context_cycle_int", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", False)]}),
        ("wm.context_cycle_int", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", True)]}),
        ("wm.context_cycle_int", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", False)]}),
        ("wm.context_cycle_int", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", True)]}),
    ])

    if not params.legacy:
        items.extend([
            ("text.new", {"type": 'N', "value": 'PRESS', "alt": True}, None),
        ])
    else:
        items.extend([
            ("text.new", {"type": 'N', "value": 'PRESS', "ctrl": True}, None),
        ])

    items.extend([
        ("text.open", {"type": 'O', "value": 'PRESS', "alt": True}, None),
        ("text.reload", {"type": 'R', "value": 'PRESS', "alt": True}, None),
        ("text.save", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        ("text.save_as", {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("text.run_script", {"type": 'P', "value": 'PRESS', "alt": True}, None),
        ("text.cut", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("text.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("text.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("text.cut", {"type": 'DEL', "value": 'PRESS', "shift": True}, None),
        ("text.copy", {"type": 'INSERT', "value": 'PRESS', "ctrl": True}, None),
        ("text.paste", {"type": 'INSERT', "value": 'PRESS', "shift": True}, None),
        ("text.duplicate_line", {"type": 'D', "value": 'PRESS', "ctrl": True}, None),
        ("text.select_all", {"type": 'A', "value": 'PRESS', "ctrl": True}, None),
        ("text.select_line", {"type": 'A', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("text.select_word", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
        ("text.move_lines", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'UP')]}),
        ("text.move_lines", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("direction", 'DOWN')]}),
        ("text.indent", {"type": 'TAB', "value": 'PRESS'}, None),
        ("text.unindent", {"type": 'TAB', "value": 'PRESS', "shift": True}, None),
        ("text.uncomment", {"type": 'D', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("text.move", {"type": 'HOME', "value": 'PRESS'},
         {"properties": [("type", 'LINE_BEGIN')]}),
        ("text.move", {"type": 'END', "value": 'PRESS'},
         {"properties": [("type", 'LINE_END')]}),
        ("text.move", {"type": 'E', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'LINE_END')]}),
        ("text.move", {"type": 'E', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'LINE_END')]}),
        ("text.move", {"type": 'LEFT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("text.move", {"type": 'RIGHT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("text.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("text.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("text.move", {"type": 'UP_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_LINE')]}),
        ("text.move", {"type": 'DOWN_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_LINE')]}),
        ("text.move", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_PAGE')]}),
        ("text.move", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_PAGE')]}),
        ("text.move", {"type": 'HOME', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'FILE_TOP')]}),
        ("text.move", {"type": 'END', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'FILE_BOTTOM')]}),
        ("text.move_select", {"type": 'HOME', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'LINE_BEGIN')]}),
        ("text.move_select", {"type": 'END', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'LINE_END')]}),
        ("text.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("text.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("text.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("text.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("text.move_select", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_LINE')]}),
        ("text.move_select", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_LINE')]}),
        ("text.move_select", {"type": 'PAGE_UP', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_PAGE')]}),
        ("text.move_select", {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_PAGE')]}),
        ("text.move_select", {"type": 'HOME', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'FILE_TOP')]}),
        ("text.move_select", {"type": 'END', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'FILE_BOTTOM')]}),
        ("text.delete", {"type": 'DEL', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("text.delete", {"type": 'BACK_SPACE', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("text.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("text.delete", {"type": 'DEL', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("text.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("text.overwrite_toggle", {"type": 'INSERT', "value": 'PRESS'}, None),
        ("text.scroll_bar", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("text.scroll_bar", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("text.scroll", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("text.scroll", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("text.selection_set", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, None),
        ("text.cursor_set", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("text.selection_set", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("select", True)]}),
        ("text.scroll", {"type": 'WHEELUPMOUSE', "value": 'PRESS'},
         {"properties": [("lines", -1)]}),
        ("text.scroll", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'},
         {"properties": [("lines", 1)]}),
        ("text.line_break", {"type": 'RET', "value": 'PRESS'}, None),
        ("text.line_break", {"type": 'NUMPAD_ENTER', "value": 'PRESS'}, None),
        op_menu("TEXT_MT_toolbox", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}),
        ("text.autocomplete", {"type": 'SPACE', "value": 'PRESS', "ctrl": True}, None),
        ("text.line_number", {"type": 'TEXTINPUT', "value": 'ANY', "any": True}, None),
        ("text.insert", {"type": 'TEXTINPUT', "value": 'ANY', "any": True}, None),
    ])

    return keymap


def km_sequencercommon(_params):
    items = []
    keymap = (
        "SequencerCommon",
        {"space_type": 'SEQUENCE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("sequencer.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("wm.context_toggle", {"type": 'O', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'scene.sequence_editor.show_overlay')]}),
        ("sequencer.view_toggle", {"type": 'TAB', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_sequencer(params):
    items = []
    keymap = (
        "Sequencer",
        {"space_type": 'SEQUENCE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        *_template_items_select_actions("sequencer.select_all"),
        ("sequencer.cut", {"type": 'K', "value": 'PRESS'},
         {"properties": [("type", 'SOFT')]}),
        ("sequencer.cut", {"type": 'K', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'HARD')]}),
        ("sequencer.mute", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("sequencer.mute", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("sequencer.unmute", {"type": 'H', "value": 'PRESS', "alt": True},
         {"properties": [("unselected", False)]}),
        ("sequencer.unmute", {"type": 'H', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("unselected", True)]}),
        ("sequencer.lock", {"type": 'L', "value": 'PRESS', "shift": True}, None),
        ("sequencer.unlock", {"type": 'L', "value": 'PRESS', "shift": True, "alt": True}, None),
        ("sequencer.reassign_inputs", {"type": 'R', "value": 'PRESS'}, None),
        ("sequencer.reload", {"type": 'R', "value": 'PRESS', "alt": True}, None),
        ("sequencer.reload", {"type": 'R', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("adjust_length", True)]}),
        ("sequencer.offset_clear", {"type": 'O', "value": 'PRESS', "alt": True}, None),
        ("sequencer.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("sequencer.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("sequencer.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("sequencer.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.images_separate", {"type": 'Y', "value": 'PRESS'}, None),
        ("sequencer.meta_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
        ("sequencer.meta_make", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.meta_separate", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("sequencer.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("sequencer.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("sequencer.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("sequencer.view_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("sequencer.strip_jump", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("next", True), ("center", False)]}),
        ("sequencer.strip_jump", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("next", False), ("center", False)]}),
        ("sequencer.strip_jump", {"type": 'PAGE_UP', "value": 'PRESS', "alt": True},
         {"properties": [("next", True), ("center", True)]}),
        ("sequencer.strip_jump", {"type": 'PAGE_DOWN', "value": 'PRESS', "alt": True},
         {"properties": [("next", False), ("center", True)]}),
        ("sequencer.swap", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("side", 'LEFT')]}),
        ("sequencer.swap", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("side", 'RIGHT')]}),
        ("sequencer.gap_remove", {"type": 'BACK_SPACE', "value": 'PRESS'},
         {"properties": [("all", False)]}),
        ("sequencer.gap_remove", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True},
         {"properties": [("all", True)]}),
        ("sequencer.gap_insert", {"type": 'EQUAL', "value": 'PRESS', "shift": True}, None),
        ("sequencer.snap", {"type": 'S', "value": 'PRESS', "shift": True}, None),
        ("sequencer.swap_inputs", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        *(
            (("sequencer.cut_multicam",
              {"type": NUMBERS_1[i], "value": 'PRESS'},
              {"properties": [("camera", i + 1)]})
             for i in range(10)
             )
        ),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False), ("linked_handle", False), ("left_right", 'NONE'), ("linked_time", False)]}),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True), ("linked_handle", False), ("left_right", 'NONE'), ("linked_time", False)]}),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False), ("linked_handle", True), ("left_right", 'NONE'), ("linked_time", False)]}),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True), ("linked_handle", True), ("left_right", 'NONE'), ("linked_time", False)]}),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("extend", False), ("linked_handle", False), ("left_right", 'MOUSE'), ("linked_time", True)]}),
        ("sequencer.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", True), ("linked_handle", False), ("left_right", 'NONE'), ("linked_time", True)]}),
        ("sequencer.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("sequencer.select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("sequencer.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("sequencer.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("sequencer.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        op_menu("SEQUENCER_MT_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        op_menu("SEQUENCER_MT_change", {"type": 'C', "value": 'PRESS'}),
        ("sequencer.slip", {"type": 'S', "value": 'PRESS'}, None),
        ("wm.context_set_int", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'scene.sequence_editor.overlay_frame'), ("value", 0)]}),
        ("transform.seq_slide", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.seq_slide", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.transform", {"type": 'E', "value": 'PRESS'},
         {"properties": [("mode", 'TIME_EXTEND')]}),
        ("marker.add", {"type": 'M', "value": 'PRESS'}, None),
        ("marker.rename", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.apple:
        items.extend([
            ("sequencer.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("sequencer.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_sequencerpreview(params):
    items = []
    keymap = (
        "SequencerPreview",
        {"space_type": 'SEQUENCE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("sequencer.view_all_preview", {"type": 'HOME', "value": 'PRESS'}, None),
        ("sequencer.view_all_preview", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("sequencer.view_ghost_border", {"type": 'O', "value": 'PRESS'}, None),
        ("sequencer.view_zoom_ratio", {"type": 'NUMPAD_1', "value": 'PRESS'},
         {"properties": [("ratio", 1.0)]}),
        ("sequencer.sample", {"type": params.action_mouse, "value": 'PRESS'}, None),
    ])

    return keymap


def km_console(params):
    items = []
    keymap = (
        "Console",
        {"space_type": 'CONSOLE', "region_type": 'WINDOW'},
        {"items": items},
    )

    if params.apple:
        items.extend([
            ("console.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'LINE_BEGIN')]}),
            ("console.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "oskey": True},
             {"properties": [("type", 'LINE_END')]}),
            ("console.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("console.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    items.extend([
        ("console.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("console.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("console.move", {"type": 'HOME', "value": 'PRESS'},
         {"properties": [("type", 'LINE_BEGIN')]}),
        ("console.move", {"type": 'END', "value": 'PRESS'},
         {"properties": [("type", 'LINE_END')]}),
        ("wm.context_cycle_int", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", False)]}),
        ("wm.context_cycle_int", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", True)]}),
        ("wm.context_cycle_int", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", False)]}),
        ("wm.context_cycle_int", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.font_size'), ("reverse", True)]}),
        ("console.move", {"type": 'LEFT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("console.move", {"type": 'RIGHT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("console.history_cycle", {"type": 'UP_ARROW', "value": 'PRESS'},
         {"properties": [("reverse", True)]}),
        ("console.history_cycle", {"type": 'DOWN_ARROW', "value": 'PRESS'},
         {"properties": [("reverse", False)]}),
        ("console.delete", {"type": 'DEL', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("console.delete", {"type": 'BACK_SPACE', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("console.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("console.delete", {"type": 'DEL', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("console.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("console.clear_line", {"type": 'RET', "value": 'PRESS', "shift": True}, None),
        ("console.clear_line", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "shift": True}, None),
        ("console.execute", {"type": 'RET', "value": 'PRESS'},
         {"properties": [("interactive", True)]}),
        ("console.execute", {"type": 'NUMPAD_ENTER', "value": 'PRESS'},
         {"properties": [("interactive", True)]}),
        ("console.autocomplete", {"type": 'SPACE', "value": 'PRESS', "ctrl": True}, None),
        ("console.copy_as_script", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("console.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("console.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("console.select_set", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("console.select_word", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
        ("console.insert", {"type": 'TAB', "value": 'PRESS', "ctrl": True},
         {"properties": [("text", '\t')]}),
        ("console.indent", {"type": 'TAB', "value": 'PRESS'}, None),
        ("console.unindent", {"type": 'TAB', "value": 'PRESS', "shift": True}, None),
        ("console.insert", {"type": 'TEXTINPUT', "value": 'ANY', "any": True}, None),
    ])

    return keymap


def km_clip(_params):
    items = []
    keymap = (
        "Clip",
        {"space_type": 'CLIP_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("clip.open", {"type": 'O', "value": 'PRESS', "alt": True}, None),
        ("clip.tools", {"type": 'T', "value": 'PRESS'}, None),
        ("clip.properties", {"type": 'N', "value": 'PRESS'}, None),
        ("clip.track_markers", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("backwards", True), ("sequence", False)]}),
        ("clip.track_markers", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("backwards", False), ("sequence", False)]}),
        ("clip.track_markers", {"type": 'T', "value": 'PRESS', "ctrl": True},
         {"properties": [("backwards", False), ("sequence", True)]}),
        ("clip.track_markers", {"type": 'T', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("backwards", True), ("sequence", True)]}),
        ("wm.context_toggle_enum", {"type": 'TAB', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.mode'), ("value_1", 'TRACKING'), ("value_2", 'MASK')]}),
        ("clip.solve_camera", {"type": 'S', "value": 'PRESS', "shift": True}, None),
        ("clip.set_solver_keyframe", {"type": 'Q', "value": 'PRESS'},
         {"properties": [("keyframe", 'KEYFRAME_A')]}),
        ("clip.set_solver_keyframe", {"type": 'E', "value": 'PRESS'},
         {"properties": [("keyframe", 'KEYFRAME_B')]}),
        ("clip.prefetch", {"type": 'P', "value": 'PRESS'}, None),
    ])

    return keymap


def km_clip_editor(params):
    items = []
    keymap = (
        "Clip Editor",
        {"space_type": 'CLIP_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("clip.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("clip.view_pan", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
        ("clip.view_pan", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("clip.view_zoom", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("clip.view_zoom", {"type": 'TRACKPADZOOM', "value": 'ANY'}, None),
        ("clip.view_zoom", {"type": 'TRACKPADPAN', "value": 'ANY', "ctrl": True}, None),
        ("clip.view_zoom_in", {"type": 'WHEELINMOUSE', "value": 'PRESS'}, None),
        ("clip.view_zoom_out", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'}, None),
        ("clip.view_zoom_in", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("clip.view_zoom_out", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 8.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 4.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS', "ctrl": True},
         {"properties": [("ratio", 2.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 8.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 4.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS', "shift": True},
         {"properties": [("ratio", 2.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_1', "value": 'PRESS'},
         {"properties": [("ratio", 1.0)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_2', "value": 'PRESS'},
         {"properties": [("ratio", 0.5)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_4', "value": 'PRESS'},
         {"properties": [("ratio", 0.25)]}),
        ("clip.view_zoom_ratio", {"type": 'NUMPAD_8', "value": 'PRESS'},
         {"properties": [("ratio", 0.125)]}),
        ("clip.view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("clip.view_all", {"type": 'F', "value": 'PRESS'},
         {"properties": [("fit_view", True)]}),
        ("clip.view_selected", {"type": 'NUMPAD_PERIOD', "value": 'PRESS'}, None),
        ("clip.view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("clip.view_ndof", {"type": 'NDOF_MOTION', "value": 'ANY'}, None),
        ("clip.frame_jump", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("position", 'PATHSTART')]}),
        ("clip.frame_jump", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("position", 'PATHEND')]}),
        ("clip.frame_jump", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("position", 'FAILEDPREV')]}),
        ("clip.frame_jump", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("position", 'PATHSTART')]}),
        ("clip.change_frame", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("clip.select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("clip.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        *_template_items_select_actions("clip.select_all"),
        ("clip.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("clip.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        op_menu("CLIP_MT_select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}),
        ("clip.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True},
         {"properties": [("deselect", False)]}),
        ("clip.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("deselect", True)]}),
        ("clip.add_marker_slide", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("clip.delete_marker", {"type": 'X', "value": 'PRESS', "shift": True}, None),
        ("clip.delete_marker", {"type": 'DEL', "value": 'PRESS', "shift": True}, None),
        ("clip.slide_marker", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("clip.disable_markers", {"type": 'D', "value": 'PRESS', "shift": True},
         {"properties": [("action", 'TOGGLE')]}),
        ("clip.delete_track", {"type": 'X', "value": 'PRESS'}, None),
        ("clip.delete_track", {"type": 'DEL', "value": 'PRESS'}, None),
        ("clip.lock_tracks", {"type": 'L', "value": 'PRESS', "ctrl": True},
         {"properties": [("action", 'LOCK')]}),
        ("clip.lock_tracks", {"type": 'L', "value": 'PRESS', "alt": True},
         {"properties": [("action", 'UNLOCK')]}),
        ("clip.hide_tracks", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("clip.hide_tracks", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("clip.hide_tracks_clear", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("clip.slide_plane_marker", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("clip.keyframe_insert", {"type": 'I', "value": 'PRESS'}, None),
        ("clip.keyframe_delete", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("clip.join_tracks", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
        op_menu("CLIP_MT_tracking_specials", {"type": 'W', "value": 'PRESS'}),
        ("wm.context_toggle", {"type": 'L', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.lock_selection')]}),
        ("wm.context_toggle", {"type": 'D', "value": 'PRESS', "alt": True},
         {"properties": [("data_path", 'space_data.show_disabled')]}),
        ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("data_path", 'space_data.show_marker_search')]}),
        ("wm.context_toggle", {"type": 'M', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.use_mute_footage')]}),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "alt": True},
         {"properties": [("action", 'REMAINED'), ("clear_active", False)]}),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "shift": True},
         {"properties": [("action", 'UPTO'), ("clear_active", False)]}),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("action", 'ALL'), ("clear_active", False)]}),
        ("clip.cursor_set", {"type": params.action_mouse, "value": 'PRESS'}, None),
        op_menu_pie("CLIP_MT_pivot_pie", {"type": 'PERIOD', "value": 'PRESS'}),
        ("clip.copy_tracks", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("clip.paste_tracks", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
    ])

    return keymap


def km_clip_graph_editor(params):
    items = []
    keymap = (
        "Clip Graph Editor",
        {"space_type": 'CLIP_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("clip.change_frame", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("clip.graph_select", {"type": params.select_mouse, "value": 'PRESS'},
         {"properties": [("extend", False)]}),
        ("clip.graph_select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        *_template_items_select_actions("clip.graph_select_all_markers"),
        ("clip.graph_select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("clip.graph_delete_curve", {"type": 'X', "value": 'PRESS'}, None),
        ("clip.graph_delete_curve", {"type": 'DEL', "value": 'PRESS'}, None),
        ("clip.graph_delete_knot", {"type": 'X', "value": 'PRESS', "shift": True}, None),
        ("clip.graph_delete_knot", {"type": 'DEL', "value": 'PRESS', "shift": True}, None),
        ("clip.graph_view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("clip.graph_view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
        ("clip.graph_center_current_frame", {"type": 'NUMPAD_0', "value": 'PRESS'}, None),
        ("wm.context_toggle", {"type": 'L', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.lock_time_cursor')]}),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "alt": True},
         {"properties": [("action", 'REMAINED'), ("clear_active", True)]}),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "shift": True},
         {"properties": [("action", 'UPTO'), ("clear_active", True)]}),
        ("clip.clear_track_path", {"type": 'T', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("action", 'ALL'), ("clear_active", True)]}),
        ("clip.graph_disable_markers", {"type": 'D', "value": 'PRESS', "shift": True},
         {"properties": [("action", 'TOGGLE')]}),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
    ])

    return keymap


def km_clip_dopesheet_editor(_params):
    items = []
    keymap = (
        "Clip Dopesheet Editor",
        {"space_type": 'CLIP_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("clip.dopesheet_select_channel", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("extend", True)]}),
        ("clip.dopesheet_view_all", {"type": 'HOME', "value": 'PRESS'}, None),
        ("clip.dopesheet_view_all", {"type": 'NDOF_BUTTON_FIT', "value": 'PRESS'}, None),
    ])

    return keymap


# ------------------------------------------------------------------------------
# Animation


def km_frames(params):
    items = []
    keymap = (
        "Frames",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Frame offsets
        ("screen.frame_offset", {"type": 'LEFT_ARROW', "value": 'PRESS'},
         {"properties": [("delta", -1)]}),
        ("screen.frame_offset", {"type": 'RIGHT_ARROW', "value": 'PRESS'},
         {"properties": [("delta", 1)]}),
        ("screen.frame_jump", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("end", True)]}),
        ("screen.frame_jump", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("end", False)]}),
        ("screen.keyframe_jump", {"type": 'UP_ARROW', "value": 'PRESS'},
         {"properties": [("next", True)]}),
        ("screen.keyframe_jump", {"type": 'DOWN_ARROW', "value": 'PRESS'},
         {"properties": [("next", False)]}),
        ("screen.keyframe_jump", {"type": 'MEDIA_LAST', "value": 'PRESS'},
         {"properties": [("next", True)]}),
        ("screen.keyframe_jump", {"type": 'MEDIA_FIRST', "value": 'PRESS'},
         {"properties": [("next", False)]}),
    ])

    if not params.legacy:
        # New playback
        items.extend([
            ("screen.animation_play", {"type": 'SPACE', "value": 'PRESS', "shift": True}, None),
            ("screen.animation_play", {"type": 'SPACE', "value": 'PRESS', "shift": True, "ctrl": True},
             {"properties": [("reverse", True)]}),
        ])
    else:
        # Old playback
        items.extend([
            ("screen.frame_offset", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True},
             {"properties": [("delta", 10)]}),
            ("screen.frame_offset", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True},
             {"properties": [("delta", -10)]}),
            ("screen.frame_offset", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "alt": True},
             {"properties": [("delta", 1)]}),
            ("screen.frame_offset", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "alt": True},
             {"properties": [("delta", -1)]}),
            ("screen.frame_jump", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
             {"properties": [("end", True)]}),
            ("screen.frame_jump", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
             {"properties": [("end", False)]}),
            ("screen.animation_play", {"type": 'A', "value": 'PRESS', "alt": True}, None),
            ("screen.animation_play", {"type": 'A', "value": 'PRESS', "shift": True, "alt": True},
             {"properties": [("reverse", True)]}),
        ])

    items.extend([
        ("screen.animation_cancel", {"type": 'ESC', "value": 'PRESS'}, None),
        ("screen.animation_play", {"type": 'MEDIA_PLAY', "value": 'PRESS'}, None),
        ("screen.animation_cancel", {"type": 'MEDIA_STOP', "value": 'PRESS'}, None),
    ])

    return keymap


def km_animation(params):
    items = []
    keymap = (
        "Animation",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Frame management.
        ("anim.change_frame", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("wm.context_toggle", {"type": 'T', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'space_data.show_seconds')]}),
        # Preview range.
        ("anim.previewrange_set", {"type": 'P', "value": 'PRESS'}, None),
        ("anim.previewrange_clear", {"type": 'P', "value": 'PRESS', "alt": True}, None),
    ])

    return keymap


def km_animation_channels(_params):
    items = []
    keymap = (
        "Animation Channels",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Click select.
        ("anim.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("anim.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("anim.channels_click", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("children_only", True)]}),
        # Rename.
        ("anim.channels_rename", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, None),
        ("anim.channels_rename", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
        # Select keys.
        ("anim.channel_select_keys", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK'}, None),
        ("anim.channel_select_keys", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK', "shift": True},
         {"properties": [("extend", True)]}),
        # Find (setting the name filter).
        ("anim.channels_find", {"type": 'F', "value": 'PRESS', "ctrl": True}, None),
        # Selection.
        *_template_items_select_actions("anim.channels_select_all"),
        ("anim.channels_select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("anim.channels_select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, None),
        # Delete.
        ("anim.channels_delete", {"type": 'X', "value": 'PRESS'}, None),
        ("anim.channels_delete", {"type": 'DEL', "value": 'PRESS'}, None),
        # Settings.
        ("anim.channels_setting_toggle", {"type": 'W', "value": 'PRESS', "shift": True}, None),
        ("anim.channels_setting_enable", {"type": 'W', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("anim.channels_setting_disable", {"type": 'W', "value": 'PRESS', "alt": True}, None),
        ("anim.channels_editable_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
        # Expand/collapse.
        ("anim.channels_expand", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("anim.channels_collapse", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("anim.channels_expand", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("all", False)]}),
        ("anim.channels_collapse", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True},
         {"properties": [("all", False)]}),
        # Move.
        ("anim.channels_move", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("direction", 'UP')]}),
        ("anim.channels_move", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("direction", 'DOWN')]}),
        ("anim.channels_move", {"type": 'PAGE_UP', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'TOP')]}),
        ("anim.channels_move", {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'BOTTOM')]}),
        # Group.
        ("anim.channels_group", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("anim.channels_ungroup", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        # Menus.
        op_menu("DOPESHEET_MT_specials_channels", {"type": 'W', "value": 'PRESS'}),
    ])

    return keymap


# ------------------------------------------------------------------------------
# Modes


def km_grease_pencil(_params):
    items = []
    keymap = (
        "Grease Pencil",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Draw
        ("gpencil.annotate", {"type": 'LEFTMOUSE', "value": 'PRESS', "key_modifier": 'D'},
         {"properties": [("mode", 'DRAW'), ("wait_for_input", False)]}),
        # Draw - straight lines
        ("gpencil.annotate", {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True, "key_modifier": 'D'},
         {"properties": [("mode", 'DRAW_STRAIGHT'), ("wait_for_input", False)]}),
        # Draw - poly lines
        ("gpencil.annotate", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "alt": True, "key_modifier": 'D'},
         {"properties": [("mode", 'DRAW_POLY'), ("wait_for_input", False)]}),
        # Erase
        ("gpencil.annotate", {"type": 'RIGHTMOUSE', "value": 'PRESS', "key_modifier": 'D'},
         {"properties": [("mode", 'ERASER'), ("wait_for_input", False)]}),

        # Enter edit mode
        ("gpencil.editmode_toggle", {"type": 'TAB', "value": 'PRESS', "key_modifier": 'D'}, None),
        # Add blank frame (B because it's easy to reach from D).
        ("gpencil.blank_frame_add", {"type": 'B', "value": 'PRESS', "key_modifier": 'D'}, None),
        # Delete active frame - for easier video tutorials/review sessions.
        # This works even when not in edit mode.
        ("gpencil.active_frames_delete_all", {"type": 'X', "value": 'PRESS', "key_modifier": 'D'}, None),
        ("gpencil.active_frames_delete_all", {"type": 'DEL', "value": 'PRESS', "key_modifier": 'D'}, None),
    ])

    return keymap


def _grease_pencil_selection(params):
    return [
        # Select all
        *_template_items_select_actions("gpencil.select_all"),
        # Circle select
        ("gpencil.select_circle", {"type": 'C', "value": 'PRESS'}, None),
        # Box select
        ("gpencil.select_box", {"type": 'B', "value": 'PRESS'}, None),
        # Lasso select
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'ADD')]}),
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        # In the Node Editor, lasso select needs ALT modifier too
        # (as somehow CTRL+LMB drag gets taken for "cut" quite early).
        # There probably isn't too much harm adding this for other editors too
        # as part of standard GP editing keymap. This hotkey combo doesn't seem
        # to see much use under standard scenarios?
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True},
         {"properties": [("mode", 'ADD')]}),
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("mode", 'SUB')]}),
        ("gpencil.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True), ("toggle", True)]}),
        # Whole stroke select
        ("gpencil.select", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("entire_strokes", True)]}),
        ("gpencil.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", True), ("entire_strokes", True)]}),
        # Select linked
        ("gpencil.select_linked", {"type": 'L', "value": 'PRESS'}, None),
        ("gpencil.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        # Select alternate
        ("gpencil.select_alternate", {"type": 'L', "value": 'PRESS', "shift": True}, None),
        # Select grouped
        ("gpencil.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        # Select more/less
        ("gpencil.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("gpencil.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
    ]


def _grease_pencil_display():
    return [
        ("wm.context_toggle", {"type": 'Q', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'space_data.overlay.use_gpencil_edit_lines')]}),
        ("wm.context_toggle", {"type": 'Q', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("data_path", 'space_data.overlay.use_gpencil_multiedit_line_only')]}),
    ]


def km_grease_pencil_stroke_edit_mode(params):
    items = []
    keymap = (
        "Grease Pencil Stroke Edit Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Interpolation
        ("gpencil.interpolate", {"type": 'E', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("gpencil.interpolate_sequence", {"type": 'E', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        # Normal select
        ("gpencil.select", {"type": params.select_mouse, "value": 'PRESS'}, None),
        # Selection
        *_grease_pencil_selection(params),
        # Duplicate and move selected points
        ("gpencil.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        # Delete
        op_menu("VIEW3D_MT_edit_gpencil_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_edit_gpencil_delete", {"type": 'DEL', "value": 'PRESS'}),
        ("gpencil.dissolve", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("gpencil.dissolve", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
        ("gpencil.active_frames_delete_all", {"type": 'X', "value": 'PRESS', "shift": True}, None),
        ("gpencil.active_frames_delete_all", {"type": 'DEL', "value": 'PRESS', "shift": True}, None),
        # Context menu
        op_menu("VIEW3D_MT_gpencil_edit_specials", {"type": 'W', "value": 'PRESS'}),
        # Separate
        op_menu("GPENCIL_MT_separate", {"type": 'P', "value": 'PRESS'}),
        # Split and joint strokes
        ("gpencil.stroke_split", {"type": 'V', "value": 'PRESS'}, None),
        ("gpencil.stroke_join", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
        ("gpencil.stroke_join", {"type": 'J', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'JOINCOPY')]}),
        # Copy + paset
        ("gpencil.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("gpencil.paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        # Snap
        op_menu("GPENCIL_MT_snap", {"type": 'S', "value": 'PRESS', "shift": True}),
        # Convert to geometry
        ("gpencil.convert", {"type": 'C', "value": 'PRESS', "alt": True}, None),
        # Show/hide
        ("gpencil.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("gpencil.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("gpencil.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("gpencil.selection_opacity_toggle", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
        # Display
        *_grease_pencil_display(),
        # Isolate layer
        ("gpencil.layer_isolate", {"type": 'NUMPAD_ASTERIX', "value": 'PRESS'}, None),
        # Move to layer
        ("gpencil.move_to_layer", {"type": 'M', "value": 'PRESS'}, None),
        # Transform tools
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("transform.mirror", {"type": 'M', "value": 'PRESS', "ctrl": True}, None),
        ("transform.bend", {"type": 'W', "value": 'PRESS', "shift": True}, None),
        ("transform.tosphere", {"type": 'S', "value": 'PRESS', "shift": True, "alt": True}, None),
        ("transform.shear", {"type": 'S', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("transform.transform", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'GPENCIL_SHRINKFATTEN')]}),
        # Proportonal editing
        *_template_items_proportional_editing(connected=True),
        # Add menu
        ("object.gpencil_add", {"type": 'A', "value": 'PRESS', "shift": True}, None),
        # Vertex group menu
        op_menu("GPENCIL_MT_gpencil_vertex_group", {"type": 'G', "value": 'PRESS', "ctrl": True}),
        # Toggle edit mode
        ("gpencil.editmode_toggle", {"type": 'TAB', "value": 'PRESS'}, None),
        # Select mode
        ("gpencil.selectmode_toggle", {"type": 'ONE', "value": 'PRESS'},
         {"properties": [("mode", 0)]}),
        ("gpencil.selectmode_toggle", {"type": 'TWO', "value": 'PRESS'},
         {"properties": [("mode", 1)]}),
    ])

    if params.apple:
        # Apple copy + paste
        items.extend([
            ("gpencil.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("gpencil.paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_grease_pencil_stroke_paint_mode(_params):
    items = []
    keymap = (
        "Grease Pencil Stroke Paint Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Brush strength
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "shift": True},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_paint.brush.gpencil_settings.pen_strength')]}),
        # Brush size
        ("wm.radial_control", {"type": 'F', "value": 'PRESS'},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_paint.brush.size')]}),
        # Brush size
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path_primary", 'user_preferences.edit.grease_pencil_eraser_radius')]}),
        # Draw context menu
        op_menu("GPENCIL_MT_gpencil_draw_specials", {"type": 'W', "value": 'PRESS'}),
        # Draw delete menu
        op_menu("GPENCIL_MT_gpencil_draw_delete", {"type": 'X', "value": 'PRESS'}),
    ])

    return keymap


def km_grease_pencil_stroke_paint_draw_brush(_params):
    items = []
    keymap = (
        "Grease Pencil Stroke Paint (Draw brush)",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Draw
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'DRAW'), ("wait_for_input", False)]}),
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'DRAW'), ("wait_for_input", False)]}),
        # Draw - straight lines
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'DRAW_STRAIGHT'), ("wait_for_input", False)]}),
        # Draw - poly lines
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("mode", 'DRAW_POLY'), ("wait_for_input", False)]}),
        # Erase
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'ERASER'), ("wait_for_input", False)]}),

        # Tablet Mappings for Drawing ------------------ */
        # For now, only support direct drawing using the eraser, as most users using a tablet
        # may still want to use that as their primary pointing device!
        ("gpencil.draw", {"type": 'ERASER', "value": 'PRESS'},
         {"properties": [("mode", 'ERASER'), ("wait_for_input", False)]}),
        # Selected (used by eraser)
        # Box select
        ("gpencil.select_box", {"type": 'B', "value": 'PRESS'}, None),
        # Lasso select
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True}, None),
    ])

    return keymap


def km_grease_pencil_stroke_paint_erase(_params):
    items = []
    keymap = (
        "Grease Pencil Stroke Paint (Erase)",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Erase
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'ERASER'), ("wait_for_input", False)]}),
        ("gpencil.draw", {"type": 'ERASER', "value": 'PRESS'},
         {"properties": [("mode", 'ERASER'), ("wait_for_input", False)]}),
        # Box select (used by eraser)
        ("gpencil.select_box", {"type": 'B', "value": 'PRESS'}, None),
        # Lasso select
        ("gpencil.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True, "alt": True}, None),
    ])

    return keymap


def km_grease_pencil_stroke_paint_fill(_params):
    items = []
    keymap = (
        "Grease Pencil Stroke Paint (Fill)",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Fill
        ("gpencil.fill", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("on_back", False)]}),
        ("gpencil.fill", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("on_back", True)]}),
        # If press alternate key, the brush now it's for drawing areas
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'DRAW'), ("wait_for_input", False), ("disable_straight", True)]}),
        # If press alternative key, the brush now it's for drawing lines
        ("gpencil.draw", {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'DRAW'), ("wait_for_input", False), ("disable_straight", True), ("disable_fill", True)]}),
    ])

    return keymap


def km_grease_pencil_stroke_sculpt_mode(params):
    items = []
    keymap = (
        "Grease Pencil Stroke Sculpt Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items}
    )

    items.extend([
        # Selection
        *_grease_pencil_selection(params),
        # Painting
        ("gpencil.brush_paint", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]}),
        ("gpencil.brush_paint", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("wait_for_input", False)]}),
        ("gpencil.brush_paint", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("wait_for_input", False)]}),
        # Brush strength
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "shift": True},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_sculpt.brush.strength')]}),
        # Brush size
        ("wm.radial_control", {"type": 'F', "value": 'PRESS'},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_sculpt.brush.size')]}),
        # Context menu
        op_menu("VIEW3D_MT_gpencil_sculpt_specials", {"type": 'W', "value": 'PRESS'}),
        # Display
        *_grease_pencil_display(),
    ])

    return keymap


def km_grease_pencil_stroke_weight_mode(params):
    items = []
    keymap = (
        "Grease Pencil Stroke Weight Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Selection
        *_grease_pencil_selection(params),
        # Painting
        ("gpencil.brush_paint", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("wait_for_input", False)]}),
        ("gpencil.brush_paint", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("wait_for_input", False)]}),
        # Brush strength
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "shift": True},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_sculpt.weight_brush.strength')]}),
        # Brush sze
        ("wm.radial_control", {"type": 'F', "value": 'PRESS'},
         {"properties": [("data_path_primary", 'tool_settings.gpencil_sculpt.weight_brush.size')]}),
        # Display
        *_grease_pencil_display(),
    ])

    return keymap


def km_face_mask(_params):
    items = []
    keymap = (
        "Face Mask",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        *_template_items_select_actions("paint.face_select_all"),
        ("paint.face_select_hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("paint.face_select_hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("paint.face_select_reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("paint.face_select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("paint.face_select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("deselect", False)]}),
        ("paint.face_select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("deselect", True)]}),
    ])

    return keymap


def km_weight_paint_vertex_selection(_params):
    items = []
    keymap = (
        "Weight Paint Vertex Selection",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        *_template_items_select_actions("paint.vert_select_all"),
        ("view3d.select_box", {"type": 'B', "value": 'PRESS'}, None),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_A', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_circle", {"type": 'C', "value": 'PRESS'}, None),
    ])

    return keymap


def km_pose(params):
    items = []
    keymap = (
        "Pose",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("object.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        op_menu("VIEW3D_MT_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        ("pose.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("pose.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("pose.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        op_menu("VIEW3D_MT_pose_apply", {"type": 'A', "value": 'PRESS', "ctrl": True}),
        ("pose.rot_clear", {"type": 'R', "value": 'PRESS', "alt": True}, None),
        ("pose.loc_clear", {"type": 'G', "value": 'PRESS', "alt": True}, None),
        ("pose.scale_clear", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        ("pose.quaternions_flip", {"type": 'F', "value": 'PRESS', "alt": True}, None),
        ("pose.rotation_mode_set", {"type": 'R', "value": 'PRESS', "ctrl": True}, None),
        ("pose.copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("pose.paste", {"type": 'V', "value": 'PRESS', "ctrl": True},
         {"properties": [("flipped", False)]}),
        ("pose.paste", {"type": 'V', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("flipped", True)]}),
        *_template_items_select_actions("pose.select_all"),
        ("pose.select_parent", {"type": 'P', "value": 'PRESS', "shift": True}, None),
        ("pose.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'PARENT'), ("extend", False)]}),
        ("pose.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'PARENT'), ("extend", True)]}),
        ("pose.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'CHILD'), ("extend", False)]}),
        ("pose.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'CHILD'), ("extend", True)]}),
        ("pose.select_linked", {"type": 'L', "value": 'PRESS'}, None),
        ("pose.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        ("pose.select_mirror", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("pose.constraint_add_with_targets", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("pose.constraints_clear", {"type": 'C', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("pose.ik_add", {"type": 'I', "value": 'PRESS', "shift": True}, None),
        ("pose.ik_clear", {"type": 'I', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        op_menu("VIEW3D_MT_pose_group", {"type": 'G', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_bone_options_toggle", {"type": 'W', "value": 'PRESS', "shift": True}),
        op_menu("VIEW3D_MT_bone_options_enable", {"type": 'W', "value": 'PRESS', "shift": True, "ctrl": True}),
        op_menu("VIEW3D_MT_bone_options_disable", {"type": 'W', "value": 'PRESS', "alt": True}),
        ("armature.layers_show_all", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True}, None),
        ("armature.armature_layers", {"type": 'M', "value": 'PRESS', "shift": True}, None),
        ("pose.bone_layers", {"type": 'M', "value": 'PRESS'}, None),
        ("wm.context_toggle", {"type": 'Z', "value": 'PRESS'},
         {"properties": [("data_path", 'space_data.overlay.show_bone_select')]}),
        ("transform.transform", {"type": 'S', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("mode", 'BONE_SIZE')]}),
        ("anim.keyframe_insert_menu", {"type": 'I', "value": 'PRESS'}, None),
        ("anim.keyframe_delete_v3d", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("anim.keying_set_active_set", {"type": 'I', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("poselib.browse_interactive", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("poselib.pose_add", {"type": 'L', "value": 'PRESS', "shift": True}, None),
        ("poselib.pose_remove", {"type": 'L', "value": 'PRESS', "alt": True}, None),
        ("poselib.pose_rename", {"type": 'L', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("pose.push", {"type": 'E', "value": 'PRESS', "ctrl": True}, None),
        ("pose.relax", {"type": 'E', "value": 'PRESS', "alt": True}, None),
        ("pose.breakdown", {"type": 'E', "value": 'PRESS', "shift": True}, None),
        op_menu("VIEW3D_MT_pose_specials", {"type": 'W', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_pose_propagate", {"type": 'P', "value": 'PRESS', "alt": True}),
    ])

    if params.apple:
        items.extend([
            ("pose.copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("pose.paste", {"type": 'V', "value": 'PRESS', "oskey": True},
             {"properties": [("flipped", False)]}),
            ("pose.paste", {"type": 'V', "value": 'PRESS', "shift": True, "oskey": True},
             {"properties": [("flipped", True)]}),
        ])

    return keymap


def km_object_mode(params):
    items = []
    keymap = (
        "Object Mode",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        op_menu_pie("VIEW3D_MT_proportional_editing_falloff_pie", {"type": 'O', "value": 'PRESS', "shift": True}),
        ("wm.context_toggle", {"type": 'O', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.use_proportional_edit_objects')]}),
        *_template_items_select_actions("object.select_all"),
        ("object.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("object.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("object.select_linked", {"type": 'L', "value": 'PRESS', "shift": True}, None),
        ("object.select_grouped", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        ("object.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'PARENT'), ("extend", False)]}),
        ("object.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'PARENT'), ("extend", True)]}),
        ("object.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'CHILD'), ("extend", False)]}),
        ("object.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'CHILD'), ("extend", True)]}),
        ("object.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        ("object.parent_clear", {"type": 'P', "value": 'PRESS', "alt": True}, None),
        ("object.location_clear", {"type": 'G', "value": 'PRESS', "alt": True},
         {"properties": [("clear_delta", False)]}),
        ("object.rotation_clear", {"type": 'R', "value": 'PRESS', "alt": True},
         {"properties": [("clear_delta", False)]}),
        ("object.scale_clear", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("clear_delta", False)]}),
        ("object.delete", {"type": 'X', "value": 'PRESS'},
         {"properties": [("use_global", False)]}),
        ("object.delete", {"type": 'X', "value": 'PRESS', "shift": True},
         {"properties": [("use_global", True)]}),
        ("object.delete", {"type": 'DEL', "value": 'PRESS'},
         {"properties": [("use_global", False)]}),
        ("object.delete", {"type": 'DEL', "value": 'PRESS', "shift": True},
         {"properties": [("use_global", True)]}),
        op_menu("VIEW3D_MT_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        op_menu("VIEW3D_MT_object_apply", {"type": 'A', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_make_links", {"type": 'L', "value": 'PRESS', "ctrl": True}),
        ("object.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("object.duplicate_move_linked", {"type": 'D', "value": 'PRESS', "alt": True}, None),
        ("object.join", {"type": 'J', "value": 'PRESS', "ctrl": True}, None),
        ("anim.keyframe_insert_menu", {"type": 'I', "value": 'PRESS'}, None),
        ("anim.keyframe_delete_v3d", {"type": 'I', "value": 'PRESS', "alt": True}, None),
        ("anim.keying_set_active_set", {"type": 'I', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("collection.create", {"type": 'G', "value": 'PRESS', "ctrl": True}, None),
        ("collection.objects_remove", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("collection.objects_remove_all", {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ("collection.objects_add_active", {"type": 'G', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("collection.objects_remove_active", {"type": 'G', "value": 'PRESS', "shift": True, "alt": True}, None),
        op_menu("VIEW3D_MT_object_specials", {"type": 'W', "value": 'PRESS'}),
        *_template_items_object_subdivision_set(),
        ("object.move_to_collection", {"type": 'M', "value": 'PRESS'}, None),
        ("object.link_to_collection", {"type": 'M', "value": 'PRESS', "shift": True}, None),
        ("object.hide_view_clear", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("object.hide_view_set", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("object.hide_view_set", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("object.hide_collection", {"type": 'H', "value": 'PRESS', "ctrl": True}, None),
        *(
            (("object.hide_collection",
              {"type": NUMBERS_1[i], "value": 'PRESS', "any": True},
              {"properties": [("collection_index", i + 1)]})
             for i in range(10)
             )
        ),
    ])

    if params.legacy:
        items.extend([
            ("object.select_mirror", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True}, None),
            ("object.parent_no_inverse_set", {"type": 'P', "value": 'PRESS', "shift": True, "ctrl": True}, None),
            ("object.track_set", {"type": 'T', "value": 'PRESS', "ctrl": True}, None),
            ("object.track_clear", {"type": 'T', "value": 'PRESS', "alt": True}, None),
            ("object.constraint_add_with_targets", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True}, None),
            ("object.constraints_clear", {"type": 'C', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("object.origin_clear", {"type": 'O', "value": 'PRESS', "alt": True}, None),
            ("object.duplicates_make_real", {"type": 'A', "value": 'PRESS', "shift": True, "ctrl": True}, None),
            op_menu("VIEW3D_MT_make_single_user", {"type": 'U', "value": 'PRESS'}),
            ("object.convert", {"type": 'C', "value": 'PRESS', "alt": True}, None),
            ("object.proxy_make", {"type": 'P', "value": 'PRESS', "ctrl": True, "alt": True}, None),
            ("object.make_local", {"type": 'L', "value": 'PRESS'}, None),
            ("object.data_transfer", {"type": 'T', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ])

    return keymap


def km_paint_curve(params):
    items = []
    keymap = (
        "Paint Curve",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("paintcurve.add_point_slide", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True}, None),
        ("paintcurve.select", {"type": params.select_mouse, "value": 'PRESS'}, None),
        ("paintcurve.select", {"type": params.select_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("extend", True)]}),
        ("paintcurve.slide", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("paintcurve.slide", {"type": params.action_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("align", True)]}),
        ("paintcurve.select", {"type": 'A', "value": 'PRESS'},
         {"properties": [("toggle", True)]}),
        ("paintcurve.cursor", {"type": params.action_mouse, "value": 'PRESS'}, None),
        ("paintcurve.delete_point", {"type": 'X', "value": 'PRESS'}, None),
        ("paintcurve.delete_point", {"type": 'DEL', "value": 'PRESS'}, None),
        ("paintcurve.draw", {"type": 'RET', "value": 'PRESS'}, None),
        ("paintcurve.draw", {"type": 'NUMPAD_ENTER', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.translate", {"type": 'EVT_TWEAK_S', "value": 'ANY'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
    ])

    return keymap


def km_curve(params):
    items = []
    keymap = (
        "Curve",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        op_menu("VIEW3D_MT_curve_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        ("curve.handle_type_set", {"type": 'V', "value": 'PRESS'}, None),
        ("curve.vertex_add", {"type": params.action_mouse, "value": 'CLICK', "ctrl": True}, None),
        ("curve.draw", {"type": params.action_mouse, "value": 'PRESS', "shift": True},
         {"properties": [("wait_for_input", False)]}),
        ("curve.draw", {"type": 'PEN', "value": 'PRESS', "shift": True},
         {"properties": [("wait_for_input", False)]}),
        *_template_items_select_actions("curve.select_all"),
        ("curve.select_row", {"type": 'R', "value": 'PRESS', "shift": True}, None),
        ("curve.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("curve.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("curve.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("curve.select_similar", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        ("curve.select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("deselect", False)]}),
        ("curve.select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("deselect", True)]}),
        ("curve.shortest_path_pick", {"type": params.select_mouse, "value": 'CLICK', "ctrl": True}, None),
        ("curve.separate", {"type": 'P', "value": 'PRESS'}, None),
        ("curve.split", {"type": 'Y', "value": 'PRESS'}, None),
        ("curve.extrude_move", {"type": 'E', "value": 'PRESS'}, None),
        ("curve.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("curve.make_segment", {"type": 'F', "value": 'PRESS'}, None),
        ("curve.cyclic_toggle", {"type": 'C', "value": 'PRESS', "alt": True}, None),
        op_menu("VIEW3D_MT_edit_curve_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_edit_curve_delete", {"type": 'DEL', "value": 'PRESS'}),
        ("curve.dissolve_verts", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("curve.dissolve_verts", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
        ("curve.tilt_clear", {"type": 'T', "value": 'PRESS', "alt": True}, None),
        ("transform.tilt", {"type": 'T', "value": 'PRESS', "ctrl": True}, None),
        ("transform.transform", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'CURVE_SHRINKFATTEN')]}),
        ("curve.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("curve.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("curve.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("curve.normals_make_consistent", {"type": 'N', "value": 'PRESS', "ctrl" if params.legacy else "shift": True}, None),
        ("object.vertex_parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        op_menu("VIEW3D_MT_edit_curve_specials", {"type": 'W', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_hook", {"type": 'H', "value": 'PRESS', "ctrl": True}),
        *_template_items_proportional_editing(connected=True),
    ])

    return keymap

# Radial control setup helpers, this operator has a lot of properties.


def radial_control_properties(paint, prop, secondary_prop, secondary_rotation=False, color=False, zoom=False):
    brush_path = 'tool_settings.' + paint + '.brush'
    unified_path = 'tool_settings.unified_paint_settings'
    rotation = 'mask_texture_slot.angle' if secondary_rotation else 'texture_slot.angle'
    return {
        "properties": [
            ("data_path_primary", brush_path + '.' + prop),
            ("data_path_secondary", unified_path + '.' + prop if secondary_prop else ''),
            ("use_secondary", unified_path + '.' + secondary_prop if secondary_prop else ''),
            ("rotation_path", brush_path + '.' + rotation),
            ("color_path", brush_path + '.cursor_color_add'),
            ("fill_color_path", brush_path + '.color' if color else ''),
            ("fill_color_override_path", unified_path + '.color' if color else ''),
            ("fill_color_override_test_path", unified_path + '.use_unified_color' if color else ''),
            ("zoom_path", 'space_data.zoom' if zoom else ''),
            ("image_id", brush_path + ''),
            ("secondary_tex", secondary_rotation),
        ],
    }

# Radial controls for the paint and sculpt modes.


def _template_paint_radial_control(paint, rotation=False, secondary_rotation=False, color=False, zoom=False):
    items = []

    items.extend([
        ("wm.radial_control", {"type": 'F', "value": 'PRESS'},
         radial_control_properties(paint, 'size', 'use_unified_size', secondary_rotation=secondary_rotation, color=color, zoom=zoom)),
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "shift": True},
         radial_control_properties(paint, 'strength', 'use_unified_strength', secondary_rotation=secondary_rotation, color=color)),
    ])

    if rotation:
        items.extend([
            ("wm.radial_control", {"type": 'F', "value": 'PRESS', "ctrl": True},
             radial_control_properties(paint, 'texture_slot.angle', None, color=color)),
        ])

    if secondary_rotation:
        items.extend([
            ("wm.radial_control", {"type": 'F', "value": 'PRESS', "ctrl": True, "alt": True},
             radial_control_properties(paint, 'mask_texture_slot.angle', None, secondary_rotation=secondary_rotation, color=color)),
        ])

    return items


def km_image_paint(_params):
    items = []
    keymap = (
        "Image Paint",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("paint.image_paint", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'NORMAL')]}),
        ("paint.image_paint", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'INVERT')]}),
        ("paint.brush_colors_flip", {"type": 'X', "value": 'PRESS'}, None),
        ("paint.grab_clone", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
        ("paint.sample_color", {"type": 'S', "value": 'PRESS'}, None),
        ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 0.9)]}),
        ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 1.0 / 0.9)]}),
        *_template_paint_radial_control("image_paint", color=True, zoom=True, rotation=True, secondary_rotation=True),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'TRANSLATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'SCALE')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'ROTATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'TRANSLATION'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("mode", 'SCALE'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("mode", 'ROTATION'), ("texmode", 'SECONDARY')]}),
        ("wm.context_toggle", {"type": 'M', "value": 'PRESS'},
         {"properties": [("data_path", 'image_paint_object.data.use_paint_mask')]}),
        ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.image_paint.brush.use_smooth_stroke')]}),
        op_menu("VIEW3D_MT_angle_control", {"type": 'R', "value": 'PRESS'}),
        ("wm.context_menu_enum", {"type": 'E', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.image_paint.brush.stroke_method')]}),
    ])

    return keymap


def km_vertex_paint(_params):
    items = []
    keymap = (
        "Vertex Paint",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("paint.vertex_paint", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("paint.brush_colors_flip", {"type": 'X', "value": 'PRESS'}, None),
        ("paint.sample_color", {"type": 'S', "value": 'PRESS'}, None),
        ("paint.vertex_color_set", {"type": 'K', "value": 'PRESS', "shift": True}, None),
        ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 0.9)]}),
        ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 1.0 / 0.9)]}),
        *_template_paint_radial_control("vertex_paint", color=True, rotation=True),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'TRANSLATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'SCALE')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'ROTATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'TRANSLATION'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("mode", 'SCALE'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("mode", 'ROTATION'), ("texmode", 'SECONDARY')]}),
        ("wm.context_toggle", {"type": 'M', "value": 'PRESS'},
         {"properties": [("data_path", 'vertex_paint_object.data.use_paint_mask')]}),
        ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.vertex_paint.brush.use_smooth_stroke')]}),
        op_menu("VIEW3D_MT_angle_control", {"type": 'R', "value": 'PRESS'}),
        ("wm.context_menu_enum", {"type": 'E', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.vertex_paint.brush.stroke_method')]}),
    ])

    return keymap


def km_weight_paint(params):
    items = []
    keymap = (
        "Weight Paint",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("paint.weight_paint", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("paint.weight_sample", {"type": params.action_mouse, "value": 'PRESS', "ctrl": True}, None),
        ("paint.weight_sample_group", {"type": params.action_mouse, "value": 'PRESS', "shift": True}, None),
        ("paint.weight_gradient", {"type": 'LEFTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("type", 'LINEAR')]}),
        ("paint.weight_gradient", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("type", 'RADIAL')]}),
        ("paint.weight_set", {"type": 'K', "value": 'PRESS', "shift": True}, None),
        ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 0.9)]}),
        ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 1.0 / 0.9)]}),
        *_template_paint_radial_control("weight_paint"),
        ("wm.radial_control", {"type": 'W', "value": 'PRESS'},
         radial_control_properties("weight_paint", 'weight', 'use_unified_weight')),
        ("wm.context_menu_enum", {"type": 'E', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.vertex_paint.brush.stroke_method')]}),
        ("wm.context_toggle", {"type": 'M', "value": 'PRESS'},
         {"properties": [("data_path", 'weight_paint_object.data.use_paint_mask')]}),
        ("wm.context_toggle", {"type": 'V', "value": 'PRESS'},
         {"properties": [("data_path", 'weight_paint_object.data.use_paint_mask_vertex')]}),
        ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.weight_paint.brush.use_smooth_stroke')]}),
    ])

    return keymap


def km_sculpt(_params):
    items = []
    keymap = (
        "Sculpt",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Brush strokes
        ("sculpt.brush_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'NORMAL')]}),
        ("sculpt.brush_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'INVERT')]}),
        ("sculpt.brush_stroke", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'SMOOTH')]}),
        # Partial Visibility Show/hide
        ("paint.hide_show", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("action", 'SHOW'), ("area", 'INSIDE')]}),
        ("paint.hide_show", {"type": 'H', "value": 'PRESS'},
         {"properties": [("action", 'HIDE'), ("area", 'INSIDE')]}),
        ("paint.hide_show", {"type": 'H', "value": 'PRESS', "alt": True},
         {"properties": [("action", 'SHOW'), ("area", 'ALL')]}),
        # Subdivision levels
        *_template_items_object_subdivision_set(),
        ("object.subdivision_set", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("level", 1), ("relative", True)]}),
        ("object.subdivision_set", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("level", -1), ("relative", True)]}),
        # Mask
        ("paint.mask_flood_fill", {"type": 'M', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'VALUE'), ("value", 0.0)]}),
        ("paint.mask_flood_fill", {"type": 'I', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'INVERT')]}),
        ("paint.mask_lasso_gesture", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("wm.context_toggle", {"type": 'M', "value": 'PRESS', "ctrl": True},
         {"properties": [("data_path", 'scene.tool_settings.sculpt.show_mask')]}),
        # Dynamic topology
        ("sculpt.dynamic_topology_toggle", {"type": 'D', "value": 'PRESS', "ctrl": True}, None),
        ("sculpt.set_detail_size", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        # Brush properties
        ("brush.scale_size", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 0.9)]}),
        ("brush.scale_size", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("scalar", 1.0 / 0.9)]}),
        *_template_paint_radial_control("sculpt", rotation=True),
        # Stencil
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS'},
         {"properties": [("mode", 'TRANSLATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'SCALE')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'ROTATION')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'TRANSLATION'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("mode", 'SCALE'), ("texmode", 'SECONDARY')]}),
        ("brush.stencil_control", {"type": 'RIGHTMOUSE', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("mode", 'ROTATION'), ("texmode", 'SECONDARY')]}),
        # Tools
        ("paint.brush_select", {"type": 'X', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'DRAW')]}),
        ("paint.brush_select", {"type": 'S', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'SMOOTH')]}),
        ("paint.brush_select", {"type": 'P', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'PINCH')]}),
        ("paint.brush_select", {"type": 'I', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'INFLATE')]}),
        ("paint.brush_select", {"type": 'G', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'GRAB')]}),
        ("paint.brush_select", {"type": 'L', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'LAYER')]}),
        ("paint.brush_select", {"type": 'T', "value": 'PRESS', "shift": True},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'FLATTEN')]}),
        ("paint.brush_select", {"type": 'C', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'CLAY')]}),
        ("paint.brush_select", {"type": 'C', "value": 'PRESS', "shift": True},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'CREASE')]}),
        ("paint.brush_select", {"type": 'K', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'SNAKE_HOOK')]}),
        ("paint.brush_select", {"type": 'M', "value": 'PRESS'},
         {"properties": [("paint_mode", 'SCULPT'), ("sculpt_tool", 'MASK'), ("toggle", True), ("create_missing", True)]}),
        # Menus
        ("wm.context_menu_enum", {"type": 'E', "value": 'PRESS'},
         {"properties": [("data_path", 'tool_settings.sculpt.brush.stroke_method')]}),
        ("wm.context_toggle", {"type": 'S', "value": 'PRESS', "shift": True},
         {"properties": [("data_path", 'tool_settings.sculpt.brush.use_smooth_stroke')]}),
        op_menu("VIEW3D_MT_angle_control", {"type": 'R', "value": 'PRESS'}),
    ])

    return keymap


# Mesh edit mode.
def km_mesh(params):
    items = []
    keymap = (
        "Mesh",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Tools.
        ("mesh.loopcut_slide", {"type": 'R', "value": 'PRESS', "ctrl": True},
         {"properties": [("TRANSFORM_OT_edge_slide", [("release_confirm", False), ],)]}),
        ("mesh.offset_edge_loops_slide", {"type": 'R', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("TRANSFORM_OT_edge_slide", [("release_confirm", False), ],)]}),
        ("mesh.inset", {"type": 'I', "value": 'PRESS'}, None),
        ("mesh.bevel", {"type": 'B', "value": 'PRESS', "ctrl": True},
         {"properties": [("vertex_only", False)]}),
        ("mesh.bevel", {"type": 'B', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("vertex_only", True)]}),
        # Selection modes.
        *_template_items_editmode_mesh_select_mode(),
        # Selection.
        ("mesh.loop_select", {"type": params.select_mouse, "value": 'PRESS', "alt": True},
         {"properties": [("extend", False), ("deselect", False), ("toggle", False)]}),
        ("mesh.loop_select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "alt": True},
         {"properties": [("extend", False), ("deselect", False), ("toggle", True)]}),
        ("mesh.edgering_select", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("extend", False), ("deselect", False), ("toggle", False)]}),
        ("mesh.edgering_select", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True, "alt": True},
         {"properties": [("extend", False), ("deselect", False), ("toggle", True)]}),
        ("mesh.shortest_path_pick", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True},
         {"properties": [("use_fill", False)]}),
        ("mesh.shortest_path_pick", {"type": params.select_mouse, "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("use_fill", True)]}),
        *_template_items_select_actions("mesh.select_all"),
        ("mesh.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("mesh.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("mesh.select_next_item", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("mesh.select_prev_item", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        ("mesh.select_linked", {"type": 'L', "value": 'PRESS', "ctrl": True}, None),
        ("mesh.select_linked_pick", {"type": 'L', "value": 'PRESS'},
         {"properties": [("deselect", False)]}),
        ("mesh.select_linked_pick", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("deselect", True)]}),
        ("mesh.select_mirror", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True}, None),
        op_menu("VIEW3D_MT_edit_mesh_select_similar", {"type": 'G', "value": 'PRESS', "shift": True}),
        # Hide/reveal.
        ("mesh.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("mesh.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("mesh.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        # Tools.
        ("mesh.normals_make_consistent", {"type": 'N', "value": 'PRESS', "ctrl" if params.legacy else "shift": True},
         {"properties": [("inside", False)]}),
        ("mesh.normals_make_consistent", {"type": 'N', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("inside", True)]}),
        ("view3d.edit_mesh_extrude_move_normal", {"type": 'E', "value": 'PRESS'}, None),
        op_menu("VIEW3D_MT_edit_mesh_extrude", {"type": 'E', "value": 'PRESS', "alt": True}),
        ("transform.edge_crease", {"type": 'E', "value": 'PRESS', "shift": True}, None),
        ("mesh.fill", {"type": 'F', "value": 'PRESS', "alt": True}, None),
        ("mesh.quads_convert_to_tris", {"type": 'T', "value": 'PRESS', "ctrl": True},
         {"properties": [("quad_method", 'BEAUTY'), ("ngon_method", 'BEAUTY')]}),
        ("mesh.quads_convert_to_tris", {"type": 'T', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("quad_method", 'FIXED'), ("ngon_method", 'CLIP')]}),
        ("mesh.tris_convert_to_quads", {"type": 'J', "value": 'PRESS', "alt": True}, None),
        ("mesh.rip_move", {"type": 'V', "value": 'PRESS'},
         {"properties": [("MESH_OT_rip", [("use_fill", False), ],)]}),
        ("mesh.rip_move", {"type": 'V', "value": 'PRESS', "alt": True},
         {"properties": [("MESH_OT_rip", [("use_fill", True), ],)]}),
        ("mesh.rip_edge_move", {"type": 'D', "value": 'PRESS', "alt": True}, None),
        ("mesh.merge", {"type": 'M', "value": 'PRESS', "alt": True}, None),
        ("transform.shrink_fatten", {"type": 'S', "value": 'PRESS', "alt": True}, None),
        ("mesh.edge_face_add", {"type": 'F', "value": 'PRESS'}, None),
        ("mesh.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        op_menu("VIEW3D_MT_mesh_add", {"type": 'A', "value": 'PRESS', "shift": True}),
        ("mesh.separate", {"type": 'P', "value": 'PRESS'}, None),
        ("mesh.split", {"type": 'Y', "value": 'PRESS'}, None),
        ("mesh.vert_connect_path", {"type": 'J', "value": 'PRESS'}, None),
        ("mesh.point_normals", {"type": 'L', "value": 'PRESS', "alt": True}, None),
        ("transform.vert_slide", {"type": 'V', "value": 'PRESS', "shift": True}, None),
        ("mesh.dupli_extrude_cursor", {"type": params.action_mouse, "value": 'CLICK', "ctrl": True},
         {"properties": [("rotate_source", True)]}),
        ("mesh.dupli_extrude_cursor", {"type": params.action_mouse, "value": 'CLICK', "shift": True, "ctrl": True},
         {"properties": [("rotate_source", False)]}),
        op_menu("VIEW3D_MT_edit_mesh_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_edit_mesh_delete", {"type": 'DEL', "value": 'PRESS'}),
        ("mesh.dissolve_mode", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("mesh.dissolve_mode", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
        ("mesh.knife_tool", {"type": 'K', "value": 'PRESS'},
         {"properties": [("use_occlude_geometry", True), ("only_selected", False)]}),
        ("object.vertex_parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        # Menus.
        op_menu("VIEW3D_MT_edit_mesh_specials", {"type": 'W', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_edit_mesh_faces", {"type": 'F', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_edit_mesh_edges", {"type": 'E', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_edit_mesh_vertices", {"type": 'V', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_hook", {"type": 'H', "value": 'PRESS', "ctrl": True}),
        op_menu("VIEW3D_MT_uv_map", {"type": 'U', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_vertex_group", {"type": 'G', "value": 'PRESS', "ctrl": True}),
        ("object.vertex_group_remove_from", {"type": 'G', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        *_template_items_proportional_editing(connected=True),
    ])

    if params.legacy:
        items.extend([
            ("mesh.poke", {"type": 'P', "value": 'PRESS', "alt": True}, None),
            ("mesh.select_non_manifold", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
            ("mesh.faces_select_linked_flat", {"type": 'F', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
            ("mesh.spin", {"type": 'R', "value": 'PRESS', "alt": True}, None),
            ("mesh.beautify_fill", {"type": 'F', "value": 'PRESS', "shift": True, "alt": True}, None),
            ("mesh.knife_tool", {"type": 'K', "value": 'PRESS', "shift": True},
             {"properties": [("use_occlude_geometry", False), ("only_selected", True)]}),
            *_template_items_object_subdivision_set(),
        ])

    return keymap


# Armature edit mode
def km_armature(params):
    items = []
    keymap = (
        "Armature",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        # Hide/reveal.
        ("armature.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("armature.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("armature.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        # Align & roll.
        ("armature.align", {"type": 'A', "value": 'PRESS', "ctrl": True, "alt": True}, None),
        ("armature.calculate_roll", {"type": 'N', "value": 'PRESS', "ctrl" if params.legacy else "shift": True}, None),
        ("armature.roll_clear", {"type": 'R', "value": 'PRESS', "alt": True}, None),
        ("armature.switch_direction", {"type": 'F', "value": 'PRESS', "alt": True}, None),
        # Add.
        ("armature.bone_primitive_add", {"type": 'A', "value": 'PRESS', "shift": True}, None),
        # Parenting.
        ("armature.parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        ("armature.parent_clear", {"type": 'P', "value": 'PRESS', "alt": True}, None),
        # Selection.
        *_template_items_select_actions("armature.select_all"),
        ("armature.select_mirror", {"type": 'M', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("extend", False)]}),
        ("armature.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'PARENT'), ("extend", False)]}),
        ("armature.select_hierarchy", {"type": 'LEFT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'PARENT'), ("extend", True)]}),
        ("armature.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS'},
         {"properties": [("direction", 'CHILD'), ("extend", False)]}),
        ("armature.select_hierarchy", {"type": 'RIGHT_BRACKET', "value": 'PRESS', "shift": True},
         {"properties": [("direction", 'CHILD'), ("extend", True)]}),
        ("armature.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("armature.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("armature.select_similar", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        ("armature.select_linked", {"type": 'L', "value": 'PRESS'}, None),
        ("armature.shortest_path_pick", {"type": params.select_mouse, "value": 'PRESS', "ctrl": True}, None),
        # Editing.
        op_menu("VIEW3D_MT_edit_armature_delete", {"type": 'X', "value": 'PRESS'}),
        op_menu("VIEW3D_MT_edit_armature_delete", {"type": 'DEL', "value": 'PRESS'}),
        ("armature.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        ("armature.dissolve", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("armature.dissolve", {"type": 'DEL', "value": 'PRESS', "ctrl": True}, None),
        ("armature.extrude_move", {"type": 'E', "value": 'PRESS'}, None),
        ("armature.extrude_forked", {"type": 'E', "value": 'PRESS', "shift": True}, None),
        ("armature.click_extrude", {"type": params.action_mouse, "value": 'CLICK', "ctrl": True}, None),
        ("armature.fill", {"type": 'F', "value": 'PRESS'}, None),
        ("armature.merge", {"type": 'M', "value": 'PRESS', "alt": True}, None),
        ("armature.split", {"type": 'Y', "value": 'PRESS'}, None),
        ("armature.separate", {"type": 'P', "value": 'PRESS'}, None),
        # Set flags.
        op_menu("VIEW3D_MT_bone_options_toggle", {"type": 'W', "value": 'PRESS', "shift": True}),
        op_menu("VIEW3D_MT_bone_options_enable", {"type": 'W', "value": 'PRESS', "shift": True, "ctrl": True}),
        op_menu("VIEW3D_MT_bone_options_disable", {"type": 'W', "value": 'PRESS', "alt": True}),
        # Armature/bone layers.
        ("armature.layers_show_all", {"type": 'ACCENT_GRAVE', "value": 'PRESS', "ctrl": True}, None),
        ("armature.armature_layers", {"type": 'M', "value": 'PRESS', "shift": True}, None),
        ("armature.bone_layers", {"type": 'M', "value": 'PRESS'}, None),
        # Special transforms.
        ("transform.transform", {"type": 'S', "value": 'PRESS', "ctrl": True, "alt": True},
         {"properties": [("mode", 'BONE_SIZE')]}),
        ("transform.transform", {"type": 'S', "value": 'PRESS', "alt": True},
         {"properties": [("mode", 'BONE_ENVELOPE')]}),
        ("transform.transform", {"type": 'R', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'BONE_ROLL')]}),
        # Menus.
        op_menu("VIEW3D_MT_armature_specials", {"type": 'W', "value": 'PRESS'}),
    ])

    return keymap


# Metaball edit mode.
def km_metaball(_params):
    items = []
    keymap = (
        "Metaball",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("object.metaball_add", {"type": 'A', "value": 'PRESS', "shift": True}, None),
        ("mball.reveal_metaelems", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("mball.hide_metaelems", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("mball.hide_metaelems", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("mball.delete_metaelems", {"type": 'X', "value": 'PRESS'}, None),
        ("mball.delete_metaelems", {"type": 'DEL', "value": 'PRESS'}, None),
        ("mball.duplicate_move", {"type": 'D', "value": 'PRESS', "shift": True}, None),
        *_template_items_select_actions("mball.select_all"),
        ("mball.select_similar", {"type": 'G', "value": 'PRESS', "shift": True}, None),
        *_template_items_proportional_editing(connected=True),
    ])

    return keymap


# Lattice edit mode.
def km_lattice(_params):
    items = []
    keymap = (
        "Lattice",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        *_template_items_select_actions("lattice.select_all"),
        ("lattice.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("lattice.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("object.vertex_parent_set", {"type": 'P', "value": 'PRESS', "ctrl": True}, None),
        ("lattice.flip", {"type": 'F', "value": 'PRESS', "alt": True}, None),
        op_menu("VIEW3D_MT_hook", {"type": 'H', "value": 'PRESS', "ctrl": True}),
        *_template_items_proportional_editing(connected=False),
    ])

    return keymap


# Particle edit mode.
def km_particle(_params):
    items = []
    keymap = (
        "Particle",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        *_template_items_select_actions("particle.select_all"),
        ("particle.select_more", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "ctrl": True}, None),
        ("particle.select_less", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "ctrl": True}, None),
        ("particle.select_linked", {"type": 'L', "value": 'PRESS'},
         {"properties": [("deselect", False)]}),
        ("particle.select_linked", {"type": 'L', "value": 'PRESS', "shift": True},
         {"properties": [("deselect", True)]}),
        ("particle.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("particle.delete", {"type": 'DEL', "value": 'PRESS'}, None),
        ("particle.reveal", {"type": 'H', "value": 'PRESS', "alt": True}, None),
        ("particle.hide", {"type": 'H', "value": 'PRESS'},
         {"properties": [("unselected", False)]}),
        ("particle.hide", {"type": 'H', "value": 'PRESS', "shift": True},
         {"properties": [("unselected", True)]}),
        ("particle.brush_edit", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("particle.brush_edit", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, None),
        ("wm.radial_control", {"type": 'F', "value": 'PRESS'},
         {"properties": [("data_path_primary", 'tool_settings.particle_edit.brush.size')]}),
        ("wm.radial_control", {"type": 'F', "value": 'PRESS', "shift": True},
         {"properties": [("data_path_primary", 'tool_settings.particle_edit.brush.strength')]}),
        op_menu("VIEW3D_MT_particle_specials", {"type": 'W', "value": 'PRESS'}),
        ("particle.weight_set", {"type": 'K', "value": 'PRESS', "shift": True}, None),
        *_template_items_proportional_editing(connected=False),
    ])

    return keymap


# Text edit mode.
def km_font(params):
    items = []
    keymap = (
        "Font",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("font.style_toggle", {"type": 'B', "value": 'PRESS', "ctrl": True},
         {"properties": [("style", 'BOLD')]}),
        ("font.style_toggle", {"type": 'I', "value": 'PRESS', "ctrl": True},
         {"properties": [("style", 'ITALIC')]}),
        ("font.style_toggle", {"type": 'U', "value": 'PRESS', "ctrl": True},
         {"properties": [("style", 'UNDERLINE')]}),
        ("font.style_toggle", {"type": 'P', "value": 'PRESS', "ctrl": True},
         {"properties": [("style", 'SMALL_CAPS')]}),
        ("font.delete", {"type": 'DEL', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_OR_SELECTION')]}),
        ("font.delete", {"type": 'DEL', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("font.delete", {"type": 'BACK_SPACE', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_OR_SELECTION')]}),
        ("font.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_OR_SELECTION')]}),
        ("font.delete", {"type": 'BACK_SPACE', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("font.move", {"type": 'HOME', "value": 'PRESS'},
         {"properties": [("type", 'LINE_BEGIN')]}),
        ("font.move", {"type": 'END', "value": 'PRESS'},
         {"properties": [("type", 'LINE_END')]}),
        ("font.move", {"type": 'LEFT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("font.move", {"type": 'RIGHT_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("font.move", {"type": 'LEFT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("font.move", {"type": 'RIGHT_ARROW', "value": 'PRESS', "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("font.move", {"type": 'UP_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_LINE')]}),
        ("font.move", {"type": 'DOWN_ARROW', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_LINE')]}),
        ("font.move", {"type": 'PAGE_UP', "value": 'PRESS'},
         {"properties": [("type", 'PREVIOUS_PAGE')]}),
        ("font.move", {"type": 'PAGE_DOWN', "value": 'PRESS'},
         {"properties": [("type", 'NEXT_PAGE')]}),
        ("font.move_select", {"type": 'HOME', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'LINE_BEGIN')]}),
        ("font.move_select", {"type": 'END', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'LINE_END')]}),
        ("font.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_CHARACTER')]}),
        ("font.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_CHARACTER')]}),
        ("font.move_select", {"type": 'LEFT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'PREVIOUS_WORD')]}),
        ("font.move_select", {"type": 'RIGHT_ARROW', "value": 'PRESS', "shift": True, "ctrl": True},
         {"properties": [("type", 'NEXT_WORD')]}),
        ("font.move_select", {"type": 'UP_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_LINE')]}),
        ("font.move_select", {"type": 'DOWN_ARROW', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_LINE')]}),
        ("font.move_select", {"type": 'PAGE_UP', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'PREVIOUS_PAGE')]}),
        ("font.move_select", {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True},
         {"properties": [("type", 'NEXT_PAGE')]}),
        ("font.change_spacing", {"type": 'LEFT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("delta", -1)]}),
        ("font.change_spacing", {"type": 'RIGHT_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("delta", 1)]}),
        ("font.change_character", {"type": 'UP_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("delta", 1)]}),
        ("font.change_character", {"type": 'DOWN_ARROW', "value": 'PRESS', "alt": True},
         {"properties": [("delta", -1)]}),
        ("font.select_all", {"type": 'A', "value": 'PRESS', "ctrl": True}, None),
        ("font.text_copy", {"type": 'C', "value": 'PRESS', "ctrl": True}, None),
        ("font.text_cut", {"type": 'X', "value": 'PRESS', "ctrl": True}, None),
        ("font.text_paste", {"type": 'V', "value": 'PRESS', "ctrl": True}, None),
        ("font.line_break", {"type": 'RET', "value": 'PRESS'}, None),
        ("font.text_insert", {"type": 'TEXTINPUT', "value": 'ANY', "any": True}, None),
        ("font.text_insert", {"type": 'BACK_SPACE', "value": 'PRESS', "alt": True},
         {"properties": [("accent", True)]}),
    ])

    if params.apple:
        items.extend([
            ("font.select_all", {"type": 'A', "value": 'PRESS', "oskey": True}, None),
            ("font.text_copy", {"type": 'C', "value": 'PRESS', "oskey": True}, None),
            ("font.text_cut", {"type": 'X', "value": 'PRESS', "oskey": True}, None),
            ("font.text_paste", {"type": 'V', "value": 'PRESS', "oskey": True}, None),
        ])

    return keymap


def km_object_non_modal(params):
    items = []
    keymap = (
        "Object Non-modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("object.mode_set", {"type": 'TAB', "value": 'PRESS'},
         {"properties": [("mode", 'EDIT'), ("toggle", True)]}),
        ("view3d.object_mode_pie_or_toggle", {"type": 'TAB', "value": 'PRESS', "ctrl": True}, None),
    ])

    if params.legacy:
        items.extend([
            ("object.origin_set", {"type": 'C', "value": 'PRESS', "shift": True, "ctrl": True, "alt": True}, None),
        ])

    return keymap


# ------------------------------------------------------------------------------
# Modal Maps and Gizmos


def km_eyedropper_modal_map(_params):
    items = []
    keymap = (
        "Eyedropper Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'RET', "value": 'RELEASE', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'RELEASE', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'LEFTMOUSE', "value": 'RELEASE', "any": True}, None),
        ("SAMPLE_BEGIN", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
        ("SAMPLE_RESET", {"type": 'SPACE', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_eyedropper_colorband_pointsampling_map(_params):
    items = []
    keymap = (
        "Eyedropper ColorBand PointSampling Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'BACK_SPACE', "value": 'PRESS', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'RET', "value": 'RELEASE', "any": True}, None),
        ("SAMPLE_CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'RELEASE', "any": True}, None),
        ("SAMPLE_SAMPLE", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
        ("SAMPLE_RESET", {"type": 'SPACE', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_transform_modal_map(_params):
    items = []
    keymap = (
        "Transform Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CONFIRM", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("AXIS_X", {"type": 'X', "value": 'PRESS'}, None),
        ("AXIS_Y", {"type": 'Y', "value": 'PRESS'}, None),
        ("AXIS_Z", {"type": 'Z', "value": 'PRESS'}, None),
        ("PLANE_X", {"type": 'X', "value": 'PRESS', "shift": True}, None),
        ("PLANE_Y", {"type": 'Y', "value": 'PRESS', "shift": True}, None),
        ("PLANE_Z", {"type": 'Z', "value": 'PRESS', "shift": True}, None),
        ("CONS_OFF", {"type": 'C', "value": 'PRESS'}, None),
        ("TRANSLATE", {"type": 'G', "value": 'PRESS'}, None),
        ("ROTATE", {"type": 'R', "value": 'PRESS'}, None),
        ("RESIZE", {"type": 'S', "value": 'PRESS'}, None),
        ("SNAP_TOGGLE", {"type": 'TAB', "value": 'PRESS', "shift": True}, None),
        ("SNAP_INV_ON", {"type": 'LEFT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_INV_OFF", {"type": 'LEFT_CTRL', "value": 'RELEASE', "any": True}, None),
        ("SNAP_INV_ON", {"type": 'RIGHT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_INV_OFF", {"type": 'RIGHT_CTRL', "value": 'RELEASE', "any": True}, None),
        ("ADD_SNAP", {"type": 'A', "value": 'PRESS'}, None),
        ("REMOVE_SNAP", {"type": 'A', "value": 'PRESS', "alt": True}, None),
        ("PROPORTIONAL_SIZE_UP", {"type": 'PAGE_UP', "value": 'PRESS'}, None),
        ("PROPORTIONAL_SIZE_DOWN", {"type": 'PAGE_DOWN', "value": 'PRESS'}, None),
        ("PROPORTIONAL_SIZE_UP", {"type": 'PAGE_UP', "value": 'PRESS', "shift": True}, None),
        ("PROPORTIONAL_SIZE_DOWN", {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True}, None),
        ("PROPORTIONAL_SIZE_UP", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'}, None),
        ("PROPORTIONAL_SIZE_DOWN", {"type": 'WHEELUPMOUSE', "value": 'PRESS'}, None),
        ("PROPORTIONAL_SIZE_UP", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True}, None),
        ("PROPORTIONAL_SIZE_DOWN", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True}, None),
        ("PROPORTIONAL_SIZE", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("EDGESLIDE_EDGE_NEXT", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "alt": True}, None),
        ("EDGESLIDE_PREV_NEXT", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "alt": True}, None),
        ("AUTOIK_CHAIN_LEN_UP", {"type": 'PAGE_UP', "value": 'PRESS', "shift": True}, None),
        ("AUTOIK_CHAIN_LEN_DOWN", {"type": 'PAGE_DOWN', "value": 'PRESS', "shift": True}, None),
        ("AUTOIK_CHAIN_LEN_UP", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "shift": True}, None),
        ("AUTOIK_CHAIN_LEN_DOWN", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "shift": True}, None),
        ("INSERTOFS_TOGGLE_DIR", {"type": 'T', "value": 'PRESS'}, None),
    ])

    return keymap


def km_backdrop_transform_widget_tweak_modal_map(_params):
    keymap = (
        "Backdrop Transform Widget Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_backdrop_crop_widget(_params):
    keymap = (
        "Backdrop Crop Widget",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": _template_items_gizmo_tweak_value()},
    )
    return keymap


def km_backdrop_crop_widget_tweak_modal_map(_params):
    keymap = (
        "Backdrop Crop Widget Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_sun_beams_widget(_params):
    keymap = (
        "Sun Beams Widget",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": _template_items_gizmo_tweak_value()},
    )
    return keymap


def km_sun_beams_widget_tweak_modal_map(_params):
    keymap = (
        "Sun Beams Widget Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_corner_pin_widget(_params):
    items = []
    keymap = (
        "Corner Pin Widget",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_corner_pin_widget_tweak_modal_map(_params):
    keymap = (
        "Corner Pin Widget Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_uv_transform_gizmo(_params):
    keymap = (
        "UV Transform Gizmo",
        {"space_type": 'IMAGE_EDITOR', "region_type": 'WINDOW'},
        {"items": _template_items_gizmo_tweak_value()},
    )
    return keymap


def km_uv_transform_gizmo_tweak_modal_map(_params):
    keymap = (
        "UV Transform Gizmo Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_spot_light_widgets(_params):
    items = []
    keymap = (
        "Spot Light Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_spot_light_widgets_tweak_modal_map(_params):
    keymap = (
        "Spot Light Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_area_light_widgets(_params):
    items = []
    keymap = (
        "Area Light Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_area_light_widgets_tweak_modal_map(_params):
    keymap = (
        "Area Light Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_target_light_widgets(_params):
    items = []
    keymap = (
        "Target Light Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_target_light_widgets_tweak_modal_map(_params):
    keymap = (
        "Target Light Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_force_field_widgets(_params):
    items = []
    keymap = (
        "Force Field Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_force_field_widgets_tweak_modal_map(_params):
    keymap = (
        "Force Field Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_camera_widgets(_params):
    items = []
    keymap = (
        "Camera Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_camera_widgets_tweak_modal_map(_params):
    keymap = (
        "Camera Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_camera_view_widgets(_params):
    items = []
    keymap = (
        "Camera View Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_camera_view_widgets_tweak_modal_map(_params):
    keymap = (
        "Camera View Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_armature_spline_widgets(_params):
    items = []
    keymap = (
        "Armature Spline Widgets",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_armature_spline_widgets_tweak_modal_map(_params):
    keymap = (
        "Armature Spline Widgets Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_view3d_navigate(_params):
    items = []
    keymap = (
        "View3D Navigate",
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_view3d_navigate_tweak_modal_map(_params):
    keymap = (
        "View3D Navigate Tweak Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": _template_items_gizmo_tweak_modal()},
    )
    return keymap


def km_view3d_gesture_circle(_params):
    items = []
    keymap = (
        "View3D Gesture Circle",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        # Note: use 'KM_ANY' for release, so the circle exits on any mouse release,
        # this is needed when circle select is activated as a tool.
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'ANY', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS'}, None),
        ("SELECT", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("DESELECT", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, None),
        ("NOP", {"type": 'LEFTMOUSE', "value": 'RELEASE', "any": True}, None),
        ("DESELECT", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("NOP", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("SUBTRACT", {"type": 'WHEELUPMOUSE', "value": 'PRESS'}, None),
        ("SUBTRACT", {"type": 'NUMPAD_MINUS', "value": 'PRESS'}, None),
        ("ADD", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS'}, None),
        ("ADD", {"type": 'NUMPAD_PLUS', "value": 'PRESS'}, None),
        ("SIZE", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
    ])

    return keymap


def km_gesture_border(_params):
    items = []
    keymap = (
        "Gesture Box",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("SELECT", {"type": 'RIGHTMOUSE', "value": 'RELEASE', "any": True}, None),
        ("BEGIN", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, None),
        ("DESELECT", {"type": 'LEFTMOUSE', "value": 'RELEASE', "shift": True}, None),
        ("BEGIN", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("SELECT", {"type": 'LEFTMOUSE', "value": 'RELEASE', "any": True}, None),
        ("BEGIN", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("DESELECT", {"type": 'MIDDLEMOUSE', "value": 'RELEASE'}, None),
    ])

    return keymap


def km_gesture_zoom_border(_params):
    items = []
    keymap = (
        "Gesture Zoom Border",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'ANY', "any": True}, None),
        ("BEGIN", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("IN", {"type": 'LEFTMOUSE', "value": 'RELEASE'}, None),
        ("BEGIN", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("OUT", {"type": 'MIDDLEMOUSE', "value": 'RELEASE'}, None),
    ])

    return keymap


def km_gesture_straight_line(_params):
    items = []
    keymap = (
        "Gesture Straight Line",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'ANY', "any": True}, None),
        ("BEGIN", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("SELECT", {"type": 'LEFTMOUSE', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_standard_modal_map(_params):
    items = []
    keymap = (
        "Standard Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("APPLY", {"type": 'LEFTMOUSE', "value": 'ANY', "any": True}, None),
        ("APPLY", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("APPLY", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("SNAP", {"type": 'LEFT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_OFF", {"type": 'LEFT_CTRL', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_knife_tool_modal_map(_params):
    items = []
    keymap = (
        "Knife Tool Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("PANNING", {"type": 'MIDDLEMOUSE', "value": 'ANY', "any": True}, None),
        ("CANCEL", {"type": 'LEFTMOUSE', "value": 'DOUBLE_CLICK', "any": True}, None),
        ("ADD_CUT", {"type": 'LEFTMOUSE', "value": 'ANY', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'SPACE', "value": 'PRESS', "any": True}, None),
        ("NEW_CUT", {"type": 'E', "value": 'PRESS'}, None),
        ("SNAP_MIDPOINTS_ON", {"type": 'LEFT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_MIDPOINTS_OFF", {"type": 'LEFT_CTRL', "value": 'RELEASE', "any": True}, None),
        ("SNAP_MIDPOINTS_ON", {"type": 'RIGHT_CTRL', "value": 'PRESS', "any": True}, None),
        ("SNAP_MIDPOINTS_OFF", {"type": 'RIGHT_CTRL', "value": 'RELEASE', "any": True}, None),
        ("IGNORE_SNAP_ON", {"type": 'LEFT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("IGNORE_SNAP_OFF", {"type": 'LEFT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("IGNORE_SNAP_ON", {"type": 'RIGHT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("IGNORE_SNAP_OFF", {"type": 'RIGHT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("ANGLE_SNAP_TOGGLE", {"type": 'C', "value": 'PRESS'}, None),
        ("CUT_THROUGH_TOGGLE", {"type": 'Z', "value": 'PRESS'}, None),
    ])

    return keymap


def km_custom_normals_modal_map(_params):
    items = []
    keymap = (
        "Custom Normals Modal Map",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'PRESS'}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("RESET", {"type": 'R', "value": 'PRESS'}, None),
        ("INVERT", {"type": 'I', "value": 'PRESS'}, None),
        ("SPHERIZE", {"type": 'S', "value": 'PRESS'}, None),
        ("ALIGN", {"type": 'A', "value": 'PRESS'}, None),
        ("USE_MOUSE", {"type": 'M', "value": 'PRESS'}, None),
        ("USE_PIVOT", {"type": 'L', "value": 'PRESS'}, None),
        ("USE_OBJECT", {"type": 'O', "value": 'PRESS'}, None),
        ("SET_USE_3DCURSOR", {"type": 'LEFTMOUSE', "value": 'CLICK', "ctrl": True}, None),
        ("SET_USE_SELECTED", {"type": 'RIGHTMOUSE', "value": 'CLICK', "ctrl": True}, None),
    ])

    return keymap


def km_view3d_fly_modal(_params):
    items = []
    keymap = (
        "View3D Fly Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'ANY', "any": True}, None),
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'LEFTMOUSE', "value": 'ANY', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'SPACE', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("ACCELERATE", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "any": True}, None),
        ("DECELERATE", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "any": True}, None),
        ("ACCELERATE", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "any": True}, None),
        ("DECELERATE", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'TRACKPADPAN', "value": 'ANY'}, None),
        ("PAN_ENABLE", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "any": True}, None),
        ("PAN_DISABLE", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("FORWARD", {"type": 'W', "value": 'PRESS'}, None),
        ("BACKWARD", {"type": 'S', "value": 'PRESS'}, None),
        ("LEFT", {"type": 'A', "value": 'PRESS'}, None),
        ("RIGHT", {"type": 'D', "value": 'PRESS'}, None),
        ("UP", {"type": 'E', "value": 'PRESS'}, None),
        ("DOWN", {"type": 'Q', "value": 'PRESS'}, None),
        ("UP", {"type": 'R', "value": 'PRESS'}, None),
        ("DOWN", {"type": 'F', "value": 'PRESS'}, None),
        ("FORWARD", {"type": 'UP_ARROW', "value": 'PRESS'}, None),
        ("BACKWARD", {"type": 'DOWN_ARROW', "value": 'PRESS'}, None),
        ("LEFT", {"type": 'LEFT_ARROW', "value": 'PRESS'}, None),
        ("RIGHT", {"type": 'RIGHT_ARROW', "value": 'PRESS'}, None),
        ("AXIS_LOCK_X", {"type": 'X', "value": 'PRESS'}, None),
        ("AXIS_LOCK_Z", {"type": 'Z', "value": 'PRESS'}, None),
        ("PRECISION_ENABLE", {"type": 'LEFT_ALT', "value": 'PRESS', "any": True}, None),
        ("PRECISION_DISABLE", {"type": 'LEFT_ALT', "value": 'RELEASE', "any": True}, None),
        ("PRECISION_ENABLE", {"type": 'LEFT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("PRECISION_DISABLE", {"type": 'LEFT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("FREELOOK_ENABLE", {"type": 'LEFT_CTRL', "value": 'PRESS', "any": True}, None),
        ("FREELOOK_DISABLE", {"type": 'LEFT_CTRL', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_view3d_walk_modal(_params):
    items = []
    keymap = (
        "View3D Walk Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'RIGHTMOUSE', "value": 'ANY', "any": True}, None),
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'LEFTMOUSE', "value": 'ANY', "any": True}, None),
        ("CONFIRM", {"type": 'RET', "value": 'PRESS', "any": True}, None),
        ("CONFIRM", {"type": 'NUMPAD_ENTER', "value": 'PRESS', "any": True}, None),
        ("FAST_ENABLE", {"type": 'LEFT_SHIFT', "value": 'PRESS', "any": True}, None),
        ("FAST_DISABLE", {"type": 'LEFT_SHIFT', "value": 'RELEASE', "any": True}, None),
        ("SLOW_ENABLE", {"type": 'LEFT_ALT', "value": 'PRESS', "any": True}, None),
        ("SLOW_DISABLE", {"type": 'LEFT_ALT', "value": 'RELEASE', "any": True}, None),
        ("FORWARD", {"type": 'W', "value": 'PRESS', "any": True}, None),
        ("BACKWARD", {"type": 'S', "value": 'PRESS', "any": True}, None),
        ("LEFT", {"type": 'A', "value": 'PRESS', "any": True}, None),
        ("RIGHT", {"type": 'D', "value": 'PRESS', "any": True}, None),
        ("UP", {"type": 'E', "value": 'PRESS', "any": True}, None),
        ("DOWN", {"type": 'Q', "value": 'PRESS', "any": True}, None),
        ("FORWARD_STOP", {"type": 'W', "value": 'RELEASE', "any": True}, None),
        ("BACKWARD_STOP", {"type": 'S', "value": 'RELEASE', "any": True}, None),
        ("LEFT_STOP", {"type": 'A', "value": 'RELEASE', "any": True}, None),
        ("RIGHT_STOP", {"type": 'D', "value": 'RELEASE', "any": True}, None),
        ("UP_STOP", {"type": 'E', "value": 'RELEASE', "any": True}, None),
        ("DOWN_STOP", {"type": 'Q', "value": 'RELEASE', "any": True}, None),
        ("FORWARD", {"type": 'UP_ARROW', "value": 'PRESS'}, None),
        ("BACKWARD", {"type": 'DOWN_ARROW', "value": 'PRESS'}, None),
        ("LEFT", {"type": 'LEFT_ARROW', "value": 'PRESS'}, None),
        ("RIGHT", {"type": 'RIGHT_ARROW', "value": 'PRESS'}, None),
        ("FORWARD_STOP", {"type": 'UP_ARROW', "value": 'RELEASE', "any": True}, None),
        ("BACKWARD_STOP", {"type": 'DOWN_ARROW', "value": 'RELEASE', "any": True}, None),
        ("LEFT_STOP", {"type": 'LEFT_ARROW', "value": 'RELEASE', "any": True}, None),
        ("RIGHT_STOP", {"type": 'RIGHT_ARROW', "value": 'RELEASE', "any": True}, None),
        ("GRAVITY_TOGGLE", {"type": 'TAB', "value": 'PRESS'}, None),
        ("GRAVITY_TOGGLE", {"type": 'G', "value": 'PRESS'}, None),
        ("JUMP", {"type": 'V', "value": 'PRESS', "any": True}, None),
        ("JUMP_STOP", {"type": 'V', "value": 'RELEASE', "any": True}, None),
        ("TELEPORT", {"type": 'SPACE', "value": 'PRESS', "any": True}, None),
        ("TELEPORT", {"type": 'MIDDLEMOUSE', "value": 'ANY', "any": True}, None),
        ("ACCELERATE", {"type": 'NUMPAD_PLUS', "value": 'PRESS', "any": True}, None),
        ("DECELERATE", {"type": 'NUMPAD_MINUS', "value": 'PRESS', "any": True}, None),
        ("ACCELERATE", {"type": 'WHEELUPMOUSE', "value": 'PRESS', "any": True}, None),
        ("DECELERATE", {"type": 'WHEELDOWNMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_view3d_rotate_modal(_params):
    items = []
    keymap = (
        "View3D Rotate Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CONFIRM", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("CONFIRM", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
        ("AXIS_SNAP_ENABLE", {"type": 'LEFT_ALT', "value": 'PRESS', "any": True}, None),
        ("AXIS_SNAP_DISABLE", {"type": 'LEFT_ALT', "value": 'RELEASE', "any": True}, None),
    ])

    return keymap


def km_view3d_move_modal(_params):
    items = []
    keymap = (
        "View3D Move Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CONFIRM", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("CONFIRM", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_view3d_zoom_modal(_params):
    items = []
    keymap = (
        "View3D Zoom Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CONFIRM", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("CONFIRM", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_view3d_dolly_modal(_params):
    items = []
    keymap = (
        "View3D Dolly Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CONFIRM", {"type": 'MIDDLEMOUSE', "value": 'RELEASE', "any": True}, None),
        ("CONFIRM", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_paint_stroke_modal(_params):
    items = []
    keymap = (
        "Paint Stroke Modal",
        {"space_type": 'EMPTY', "region_type": 'WINDOW', "modal": True},
        {"items": items},
    )

    items.extend([
        ("CANCEL", {"type": 'ESC', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


def km_gizmos(_params):
    items = []
    keymap = (
        "Gizmos",
        {"space_type": 'EMPTY', "region_type": 'WINDOW'},
        {"items": items},
    )

    return keymap


def km_backdrop_transform_widget(_params):
    items = []
    keymap = (
        "Backdrop Transform Widget",
        {"space_type": 'NODE_EDITOR', "region_type": 'WINDOW'},
        {"items": items},
    )

    items.extend([
        ("gizmogroup.gizmo_tweak", {"type": 'LEFTMOUSE', "value": 'PRESS', "any": True}, None),
    ])

    return keymap


# ------------------------------------------------------------------------------
# Full Configuration

def generate_keymaps(params=None):
    if params is None:
        params = KeymapParams()
    return [
        # Window, screen, area, region.
        km_window(params),
        km_screen(params),
        km_screen_editing(params),
        km_header(params),
        km_view2d(params),
        km_view2d_buttons_list(params),
        km_user_interface(params),
        km_property_editor(params),

        # Editors.
        km_outliner(params),
        km_uv_editor(params),
        km_uv_sculpt(params),
        km_view3d_generic(params),
        km_view3d(params),
        km_mask_editing(params),
        km_markers(params),
        km_graph_editor_generic(params),
        km_graph_editor(params),
        km_image_generic(params),
        km_image(params),
        km_node_generic(params),
        km_node_editor(params),
        km_info(params),
        km_file_browser(params),
        km_file_browser_main(params),
        km_file_browser_buttons(params),
        km_dopesheet_generic(params),
        km_dopesheet(params),
        km_nla_generic(params),
        km_nla_channels(params),
        km_nla_editor(params),
        km_text_generic(params),
        km_text(params),
        km_sequencercommon(params),
        km_sequencer(params),
        km_sequencerpreview(params),
        km_console(params),
        km_clip(params),
        km_clip_editor(params),
        km_clip_graph_editor(params),
        km_clip_dopesheet_editor(params),

        # Animation.
        km_frames(params),
        km_animation(params),
        km_animation_channels(params),

        # Modes.
        km_grease_pencil(params),
        km_grease_pencil_stroke_edit_mode(params),
        km_grease_pencil_stroke_paint_mode(params),
        km_grease_pencil_stroke_paint_draw_brush(params),
        km_grease_pencil_stroke_paint_erase(params),
        km_grease_pencil_stroke_paint_fill(params),
        km_grease_pencil_stroke_sculpt_mode(params),
        km_grease_pencil_stroke_weight_mode(params),
        km_face_mask(params),
        km_weight_paint_vertex_selection(params),
        km_pose(params),
        km_object_mode(params),
        km_paint_curve(params),
        km_curve(params),
        km_image_paint(params),
        km_vertex_paint(params),
        km_weight_paint(params),
        km_sculpt(params),
        km_mesh(params),
        km_armature(params),
        km_metaball(params),
        km_lattice(params),
        km_particle(params),
        km_font(params),
        km_object_non_modal(params),

        # Modal maps.
        km_eyedropper_modal_map(params),
        km_eyedropper_colorband_pointsampling_map(params),
        km_transform_modal_map(params),
        km_view3d_navigate(params),
        km_view3d_navigate_tweak_modal_map(params),
        km_view3d_gesture_circle(params),
        km_gesture_border(params),
        km_gesture_zoom_border(params),
        km_gesture_straight_line(params),
        km_standard_modal_map(params),
        km_knife_tool_modal_map(params),
        km_custom_normals_modal_map(params),
        km_view3d_fly_modal(params),
        km_view3d_walk_modal(params),
        km_view3d_rotate_modal(params),
        km_view3d_move_modal(params),
        km_view3d_zoom_modal(params),
        km_view3d_dolly_modal(params),
        km_paint_stroke_modal(params),

        # Gizmos.
        km_gizmos(params),
        km_backdrop_transform_widget_tweak_modal_map(params),
        km_backdrop_crop_widget(params),
        km_backdrop_crop_widget_tweak_modal_map(params),
        km_sun_beams_widget(params),
        km_sun_beams_widget_tweak_modal_map(params),
        km_corner_pin_widget(params),
        km_corner_pin_widget_tweak_modal_map(params),
        km_uv_transform_gizmo(params),
        km_uv_transform_gizmo_tweak_modal_map(params),
        km_spot_light_widgets(params),
        km_spot_light_widgets_tweak_modal_map(params),
        km_area_light_widgets(params),
        km_area_light_widgets_tweak_modal_map(params),
        km_target_light_widgets(params),
        km_target_light_widgets_tweak_modal_map(params),
        km_force_field_widgets(params),
        km_force_field_widgets_tweak_modal_map(params),
        km_camera_widgets(params),
        km_camera_widgets_tweak_modal_map(params),
        km_camera_view_widgets(params),
        km_camera_view_widgets_tweak_modal_map(params),
        km_armature_spline_widgets(params),
        km_armature_spline_widgets_tweak_modal_map(params),
        km_backdrop_transform_widget(params),
    ]

# ------------------------------------------------------------------------------
# Refactoring (Testing Only)
#
# Allows running outside of Blender to generate data for diffing
#
# To compare:
#
#    python3 release/scripts/presets/keyconfig/keymap_data/blender_default.py && \
#      diff -u keymap_default.py.orig keymap_default.py && \
#      diff -u keymap_legacy.py.orig  keymap_legacy.py
#
# # begin code:
# import pprint
# for legacy in (False, True):
#     with open("keymap_default.py" if not legacy else "keymap_legacy.py", 'w') as fh:
#         fh.write(pprint.pformat(generate_keymaps(KeymapParams(legacy=legacy)), indent=2, width=80))
# import sys
# sys.exit()
# # end code


# ------------------------------------------------------------------------------
# PyLint (Testing Only)
#
# Command to lint:
#
#    pylint release/scripts/presets/keyconfig/keymap_data/blender_default.py --disable=C0111,C0301,C0302,R0903,R0913


if __name__ == "__main__":
    from bpy_extras.keyconfig_utils import keyconfig_import_from_data
    keyconfig_import_from_data("Blender", generate_keymaps())
    keyconfig_import_from_data("Blender 27X", generate_keymaps(KeymapParams(legacy=True)))
