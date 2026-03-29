# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 20:47:13 2020

@author: mark.shovman
"""

class Artist():
    def __init__(self, parent=None):
        self._parent = parent
        self._kids = []
        self._a_entity = None
        if self._parent is not None:
            self.soup = self._parent.soup

    def add_artist(self, a):
        self._kids.append(a)

    def show(self):
        for kid in self._kids:
            kid.show()

    def get_a_entity(self):
        return self._a_entity


class Renderer():
    """
  	* draw_path - same, but in 3D
  	* draw_image - same, but in 3D, so needs a 3D rect to draw on
  	* draw_text - same, but in 3D - anchor point, blackboarding behaviour, etc
  	* get_text_width_height_descent - same (wow)
  	* draw_markers - same, but the markers are most likely 3D glyphs
  	* draw_path_collection - same
  	* draw_quad_mesh - same in 3D

  	need to add:
  	* draw_3D_mesh - the main primitive for 3D
  	* draw_volumetric_data - tricky, but important to get right (later)
    """
    pass

class Event():
    """
    Event handlers for VR controllers.

    Maps A-Frame controller events (hover, grip, trigger) to attribute changes
    and text annotations on data-point markers.  Because PlotVR generates static
    HTML, handlers are translated to A-Frame ``event-set__`` attributes and
    ``<a-text>`` child elements at render time.

    Usage example::

        import PlotVR as pvr
        import numpy as np

        pos = np.random.rand(20, 3)
        ev = pvr.Event()
        ev.on(pvr.Event.HOVER_START, 'material.color', '#FFFF00')
        ev.on(pvr.Event.HOVER_END,   'material.color', '#EF2D5E')
        ev.annotate([f'point {i}' for i in range(20)])
        pvr.scatter(pos[:,0], pos[:,1], pos[:,2], event=ev)
        pvr.show()
    """

    # ---------------------------------------------------------------------------
    # Event-type constants
    # ---------------------------------------------------------------------------
    HOVER_START   = 'hover-start'
    HOVER_END     = 'hover-end'
    GRIP_DOWN     = 'gripdown'
    GRIP_UP       = 'gripup'
    TRIGGER_DOWN  = 'triggerdown'
    TRIGGER_UP    = 'triggerup'

    # Maps a "start" / "down" event to the matching "end" / "up" event used to
    # dismiss annotations.
    _RELEASE = {
        'hover-start':  'hover-end',
        'gripdown':     'gripup',
        'triggerdown':  'triggerup',
    }

    def __init__(self):
        self._bindings   = []   # list of (event_type, attribute, value)
        self._annotation = None # (texts, trigger_event, color) or None

    # ---------------------------------------------------------------------------
    # Builder methods
    # ---------------------------------------------------------------------------

    def on(self, event_type, attribute, value):
        """Register an A-Frame attribute change triggered by a controller event.

        Parameters
        ----------
        event_type : str
            A-Frame event name (use the class constants or a raw string).
        attribute : str
            A-Frame component/attribute to set, e.g. ``'material.color'``.
        value : str
            Value to assign, e.g. ``'#FF0'``.

        Returns
        -------
        self
            Supports method chaining.
        """
        self._bindings.append((event_type, attribute, value))
        return self

    def annotate(self, texts, trigger_event=None, color='#FFFFFF'):
        """Show per-point text labels when a controller event fires.

        Parameters
        ----------
        texts : str or sequence of str
            Label text.  A single string is shared by every marker; a sequence
            must match the number of data points.
        trigger_event : str, optional
            A-Frame event that reveals the label.  Defaults to
            ``Event.TRIGGER_DOWN``.  The label is hidden on the corresponding
            release event (e.g. ``triggerup`` for ``triggerdown``).
        color : str
            CSS color for the label text (default ``'#FFFFFF'``).

        Returns
        -------
        self
            Supports method chaining.
        """
        if trigger_event is None:
            trigger_event = Event.TRIGGER_DOWN
        self._annotation = (texts, trigger_event, color)
        return self

    # ---------------------------------------------------------------------------
    # HTML-generation helpers (used by _artists.py)
    # ---------------------------------------------------------------------------

    def to_aframe_attrs(self):
        """Return a dict of ``event-set__n`` HTML attributes for all bindings.

        The returned dict can be unpacked directly into ``soup.new_tag()``.
        """
        attrs = {}
        for i, (event_type, attribute, value) in enumerate(self._bindings):
            attrs[f'event-set__{i}'] = f'_event: {event_type}; {attribute}: {value}'
        return attrs

    def make_annotation_tag(self, soup, text):
        """Create an ``<a-text>`` child element for a single data point.

        Parameters
        ----------
        soup : BeautifulSoup
            The document to use for tag creation.
        text : str
            Label text for this specific point.

        Returns
        -------
        bs4.element.Tag or None
            The ``<a-text>`` element, or ``None`` if no annotation is set.
        """
        if self._annotation is None:
            return None
        _, trigger_event, color = self._annotation
        release_event = Event._RELEASE.get(trigger_event, trigger_event + 'up')
        tag = soup.new_tag('a-text',
                           value=str(text),
                           color=color,
                           visible='false',
                           position='0 0.08 0',
                           align='center',
                           scale='0.1 0.1 0.1')
        tag['event-set__show'] = f'_event: {trigger_event}; visible: true'
        tag['event-set__hide'] = f'_event: {release_event}; visible: false'
        return tag

