"""Unit tests for VR controller Event handling (issue #7)."""
import numpy as np
import pytest

import PlotVR as pvr
from PlotVR._base import Event
from PlotVR._artists import Scene, MarkerSet


# ---------------------------------------------------------------------------
# Event class – constants and construction
# ---------------------------------------------------------------------------

class TestEventConstants:
    def test_hover_start_constant(self):
        assert Event.HOVER_START == 'hover-start'

    def test_hover_end_constant(self):
        assert Event.HOVER_END == 'hover-end'

    def test_grip_down_constant(self):
        assert Event.GRIP_DOWN == 'gripdown'

    def test_grip_up_constant(self):
        assert Event.GRIP_UP == 'gripup'

    def test_trigger_down_constant(self):
        assert Event.TRIGGER_DOWN == 'triggerdown'

    def test_trigger_up_constant(self):
        assert Event.TRIGGER_UP == 'triggerup'

    def test_starts_with_empty_bindings(self):
        ev = Event()
        assert ev._bindings == []

    def test_starts_with_no_annotation(self):
        ev = Event()
        assert ev._annotation is None


# ---------------------------------------------------------------------------
# Event.on() – binding registration
# ---------------------------------------------------------------------------

class TestEventOn:
    def test_on_returns_self_for_chaining(self):
        ev = Event()
        result = ev.on(Event.HOVER_START, 'material.color', '#FF0')
        assert result is ev

    def test_on_stores_binding(self):
        ev = Event()
        ev.on(Event.HOVER_START, 'material.color', '#FF0')
        assert ev._bindings == [('hover-start', 'material.color', '#FF0')]

    def test_multiple_bindings(self):
        ev = Event()
        ev.on(Event.HOVER_START, 'material.color', '#FF0')
        ev.on(Event.HOVER_END,   'material.color', '#FFF')
        assert len(ev._bindings) == 2

    def test_chained_bindings(self):
        ev = (Event()
              .on(Event.GRIP_DOWN,    'material.color', '#F00')
              .on(Event.GRIP_UP,      'material.color', '#FFF')
              .on(Event.TRIGGER_DOWN, 'visible', 'false'))
        assert len(ev._bindings) == 3


# ---------------------------------------------------------------------------
# Event.to_aframe_attrs()
# ---------------------------------------------------------------------------

class TestToAframeAttrs:
    def test_empty_event_returns_empty_dict(self):
        assert Event().to_aframe_attrs() == {}

    def test_single_binding_key(self):
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        attrs = ev.to_aframe_attrs()
        assert 'event-set__0' in attrs

    def test_single_binding_value_format(self):
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        assert ev.to_aframe_attrs()['event-set__0'] == '_event: hover-start; material.color: #FF0'

    def test_multiple_bindings_distinct_keys(self):
        ev = (Event()
              .on(Event.HOVER_START, 'material.color', '#FF0')
              .on(Event.HOVER_END,   'material.color', '#FFF'))
        attrs = ev.to_aframe_attrs()
        assert 'event-set__0' in attrs
        assert 'event-set__1' in attrs

    def test_grip_down_binding(self):
        ev = Event().on(Event.GRIP_DOWN, 'scale', '1.2 1.2 1.2')
        assert ev.to_aframe_attrs()['event-set__0'] == '_event: gripdown; scale: 1.2 1.2 1.2'


# ---------------------------------------------------------------------------
# Event.annotate()
# ---------------------------------------------------------------------------

class TestEventAnnotate:
    def test_annotate_returns_self(self):
        ev = Event()
        assert ev.annotate('hello') is ev

    def test_annotate_stores_annotation(self):
        ev = Event().annotate('label')
        assert ev._annotation is not None

    def test_annotate_stores_texts(self):
        ev = Event().annotate('label')
        texts, _, _ = ev._annotation
        assert texts == 'label'

    def test_annotate_default_trigger_is_triggerdown(self):
        ev = Event().annotate('label')
        _, trigger, _ = ev._annotation
        assert trigger == Event.TRIGGER_DOWN

    def test_annotate_custom_trigger(self):
        ev = Event().annotate('label', trigger_event=Event.HOVER_START)
        _, trigger, _ = ev._annotation
        assert trigger == Event.HOVER_START

    def test_annotate_default_color_is_white(self):
        ev = Event().annotate('label')
        _, _, color = ev._annotation
        assert color == '#FFFFFF'

    def test_annotate_custom_color(self):
        ev = Event().annotate('label', color='#F00')
        _, _, color = ev._annotation
        assert color == '#F00'


# ---------------------------------------------------------------------------
# Event.make_annotation_tag()
# ---------------------------------------------------------------------------

class TestMakeAnnotationTag:
    def _soup(self):
        from bs4 import BeautifulSoup
        return BeautifulSoup('<html></html>', features='html.parser')

    def test_returns_none_when_no_annotation(self):
        ev = Event()
        assert ev.make_annotation_tag(self._soup(), 'x') is None

    def test_returns_a_text_tag(self):
        ev = Event().annotate('hello')
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert tag.name == 'a-text'

    def test_a_text_value(self):
        ev = Event().annotate('my label')
        tag = ev.make_annotation_tag(self._soup(), 'my label')
        assert tag['value'] == 'my label'

    def test_a_text_starts_invisible(self):
        ev = Event().annotate('hello')
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert tag['visible'] == 'false'

    def test_a_text_has_show_event(self):
        ev = Event().annotate('hello', trigger_event=Event.TRIGGER_DOWN)
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert 'event-set__show' in tag.attrs
        assert 'triggerdown' in tag['event-set__show']

    def test_a_text_has_hide_event_on_release(self):
        ev = Event().annotate('hello', trigger_event=Event.TRIGGER_DOWN)
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert 'event-set__hide' in tag.attrs
        assert 'triggerup' in tag['event-set__hide']

    def test_hover_annotation_releases_on_hover_end(self):
        ev = Event().annotate('hello', trigger_event=Event.HOVER_START)
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert 'hover-end' in tag['event-set__hide']

    def test_grip_annotation_releases_on_grip_up(self):
        ev = Event().annotate('hello', trigger_event=Event.GRIP_DOWN)
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert 'gripup' in tag['event-set__hide']

    def test_a_text_color(self):
        ev = Event().annotate('hello', color='#0F0')
        tag = ev.make_annotation_tag(self._soup(), 'hello')
        assert tag['color'] == '#0F0'


# ---------------------------------------------------------------------------
# MarkerSet integration
# ---------------------------------------------------------------------------

class TestMarkerSetWithEvent:
    def _scene_and_markerset(self, x, y, z, **kwargs):
        s = Scene()
        axes = s.gcf().gca()
        ms = MarkerSet(parent=axes, x=x, y=y, z=z, **kwargs)
        return s, ms

    def test_no_event_no_event_set_attrs(self):
        x = np.array([0.0, 0.5])
        s, _ = self._scene_and_markerset(x, x, x)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert not any(k.startswith('event-set__') for k in sp.attrs)

    def test_event_adds_event_set_to_each_marker(self):
        x = np.array([0.0, 0.5, 1.0])
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert 'event-set__0' in sp.attrs

    def test_event_attr_value_correct(self):
        x = np.array([0.5])
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        sp = s.soup.find(id='markerset').find('a-sphere')
        assert sp['event-set__0'] == '_event: hover-start; material.color: #FF0'

    def test_multiple_bindings_all_present_on_markers(self):
        x = np.array([0.0, 1.0])
        ev = (Event()
              .on(Event.HOVER_START, 'material.color', '#FF0')
              .on(Event.HOVER_END,   'material.color', '#FFF'))
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert 'event-set__0' in sp.attrs
            assert 'event-set__1' in sp.attrs

    def test_annotation_adds_a_text_child_to_each_marker(self):
        x = np.array([0.0, 0.5])
        labels = ['pt0', 'pt1']
        ev = Event().annotate(labels)
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert sp.find('a-text') is not None

    def test_annotation_per_point_text(self):
        x = np.array([0.0, 0.5, 1.0])
        labels = ['alpha', 'beta', 'gamma']
        ev = Event().annotate(labels)
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp, expected in zip(spheres, labels):
            assert sp.find('a-text')['value'] == expected

    def test_annotation_single_string_broadcast(self):
        x = np.array([0.0, 0.5, 1.0])
        ev = Event().annotate('data point')
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert sp.find('a-text')['value'] == 'data point'

    def test_no_annotation_no_a_text(self):
        x = np.array([0.0, 0.5])
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        s, _ = self._scene_and_markerset(x, x, x, event=ev)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        for sp in spheres:
            assert sp.find('a-text') is None


# ---------------------------------------------------------------------------
# Scripting-layer integration
# ---------------------------------------------------------------------------

class TestScatterEventParam:
    def test_scatter_accepts_event_kwarg(self):
        x = np.array([0.0, 1.0])
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        pvr.scatter(x, x, x, event=ev)  # must not raise

    def test_scatter_stores_event_in_raw_data(self):
        x = np.array([0.0, 1.0])
        ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
        pvr.scatter(x, x, x, event=ev)
        axes = pvr.figure(num=1).gcf().gca()
        stored_event = axes._raw_data[0][6]
        assert stored_event is ev

    def test_event_exported_from_package(self):
        assert hasattr(pvr, 'Event')
        assert pvr.Event is Event

    def test_event_survives_show(self, tmp_path, monkeypatch):
        from unittest.mock import patch
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            x = np.array([0.0, 0.5, 1.0])
            ev = Event().on(Event.HOVER_START, 'material.color', '#FF0')
            pvr.scatter(x, x, x, event=ev)
            pvr.show()
        html = (tmp_path / 'PlotVR_Figure 1.html').read_text()
        assert 'event-set__0' in html
        assert 'hover-start' in html

    def test_annotation_in_html_after_show(self, tmp_path, monkeypatch):
        from unittest.mock import patch
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            x = np.array([0.0, 1.0])
            ev = Event().annotate(['pt0', 'pt1'])
            pvr.scatter(x, x, x, event=ev)
            pvr.show()
        html = (tmp_path / 'PlotVR_Figure 1.html').read_text()
        assert 'a-text' in html
        assert 'pt0' in html
        assert 'pt1' in html
