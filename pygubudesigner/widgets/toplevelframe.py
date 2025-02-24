# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import tkinter as tk

from pygubu.builder.builderobject import BuilderObject, register_widget
from pygubu.builder.tkstdwidgets import TKToplevel


class ToplevelFramePreview(tk.Frame):
    def __init__(self, master=None, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.tl_attrs = {}
        self._w_set = False
        self._h_set = False

    def configure(self, cnf=None, **kw):
        if kw:
            cnf = tk._cnfmerge((cnf, kw))
        elif cnf:
            cnf = tk._cnfmerge(cnf)
        key = 'width'
        if key in cnf:
            value = int(cnf[key])
            minsize = self.tl_attrs.get('minsize', None)
            maxsize = self.tl_attrs.get('maxsize', None)
            #            print(value, minsize, maxsize)
            remove = False
            #            print('tl_attrs:', self.tl_attrs)
            if minsize and value < minsize[0]:
                remove = True
            if maxsize and value > maxsize[0]:
                remove = True
            if self._w_set:
                resizable = self.tl_attrs.get('resizable', None)
                if resizable and not TKToplevel.RESIZABLE[resizable][0]:
                    remove = True
            if remove:
                #                print('rm', key, value)
                cnf.pop(key)
            else:
                self._w_set = True
        key = 'height'
        if key in cnf:
            value = int(cnf[key])
            minsize = self.tl_attrs.get('minsize', None)
            maxsize = self.tl_attrs.get('maxsize', None)
            #            print(value, minsize, maxsize)
            remove = False
            if minsize and value < minsize[1]:
                remove = True
            if maxsize and value > maxsize[1]:
                remove = True
            if self._h_set:
                resizable = self.tl_attrs.get('resizable', None)
                if resizable and not TKToplevel.RESIZABLE[resizable][1]:
                    remove = True
            if remove:
                #                print('rm', key, value)
                cnf.pop(key)
            else:
                self._h_set = True
        key = 'menu'
        if key in cnf:
            # No menu preview available
            cnf.pop(key)

        return tk.Frame.configure(self, cnf)


class ToplevelFramePreviewBO(BuilderObject):
    class_ = ToplevelFramePreview
    container = True
    container_layout = True
    # Add fake 'modal' property for Dialog preview
    properties = TKToplevel.properties + ('modal',)
    ro_properties = TKToplevel.ro_properties

    def configure(self, target=None):
        # setup width and height properties if
        # geometry is defined.
        geom = 'geometry'
        if geom in self.wmeta.properties:
            w, h = self._get_dimwh(self.wmeta.properties[geom])
            if w and h:
                self.wmeta.properties['width'] = w
                self.wmeta.properties['height'] = h
        super().configure(target)

    def _get_dimwh(self, dimvalue: str):
        # get width and height from dimension string
        dim = dimvalue.split('+')[0]
        dim = dim.split('-')[0]
        w, h = dim.split('x')
        return (w, h)

    def _set_property(self, target_widget, pname, value):
        tw = target_widget
        tw.tl_attrs[pname] = value
        method_props = ('iconbitmap', 'iconphoto', 'overrideredirect', 'title')
        if pname in method_props:
            pass
        elif pname in ('maxsize', 'minsize'):
            if not value:
                del tw.tl_attrs[pname]
            elif '|' in value:
                w, h = value.split('|')
                if w and h:
                    tw.tl_attrs[pname] = (int(w), int(h))
                else:
                    del tw.tl_attrs[pname]
        elif pname == 'geometry':
            if value:
                w, h = self._get_dimwh(value)
                if w and h:
                    tw.tl_attrs['minsize'] = (int(w), int(h))
                    tw._h_set = tw._w_set = False
                    tw.configure(width=w, height=h)
                    if tw.pack_slaves():
                        tw.pack_propagate(0)
                    elif tw.grid_slaves():
                        tw.grid_propagate(0)
        elif pname == 'resizable':
            # Do nothing, fake 'resizable' property for Toplevel preview
            pass
        elif pname == 'modal':
            # Do nothing, fake 'modal' property for dialog preview
            pass
        else:
            super()._set_property(tw, pname, value)


register_widget(
    'pygubudesigner.ToplevelFramePreview',
    ToplevelFramePreviewBO,
    'ToplevelFramePreview',
    tuple(),
)
