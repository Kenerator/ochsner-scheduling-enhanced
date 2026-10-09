import unittest
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from scheduling_core_fixtures import MemoryApi, ScriptModel, ready
try:
    from guarded_scheduling.ui_adapter import UiController, DISCLOSURE
except ImportError:
    UiController=None
    DISCLOSURE=''

class UiTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(UiController,'Thin UI controller not implemented')
        self.api=MemoryApi()
        self.model=ScriptModel([Interpretation('book','primary_care','downtown')])
        self.session=SchedulingSession(self.api,self.model)
        self.ui=UiController(self.session)
    def test_render_is_effect_free_and_discloses_boundaries(self):
        for _ in range(3):
            view=self.ui.snapshot()
            self.assertEqual(view['state'],'clarify')
            self.assertIn('AI',view['disclosure'])
            self.assertIn('synthetic',view['disclosure'])
            self.assertIn('local',view['disclosure'])
        self.assertEqual(self.api.calls,[])
        self.assertEqual(self.model.inputs,[])
    def test_exact_proposal_confirm_and_replayed_events_book_once(self):
        ready(self.session)
        chosen=self.ui.dispatch('choose-1','choose',{'index':1})
        proposal=chosen['proposal_id']
        self.assertEqual(len(self.api.bookings),0)
        self.ui.snapshot()
        self.ui.dispatch('confirm-1','confirm',{'proposal_id':proposal})
        self.ui.dispatch('confirm-1','confirm',{'proposal_id':proposal})
        self.ui.dispatch('confirm-double-click','confirm',{'proposal_id':proposal})
        self.assertEqual(len(self.api.bookings),1)
        self.assertEqual(self.ui.snapshot()['state'],'booked')
    def test_correction_invalidates_rendered_old_confirmation(self):
        ready(self.session)
        old=self.ui.dispatch('choose-1','choose',{'index':1})['proposal_id']
        self.ui.dispatch('correct-1','preferences',{'end_date':'2026-10-10'})
        self.ui.dispatch('confirm-old','confirm',{'proposal_id':old})
        self.assertEqual(len(self.api.bookings),0)
        self.assertIsNone(self.ui.snapshot()['proposal_id'])
    def test_unknown_outcome_survives_reset_and_ui_events(self):
        ready(self.session)
        proposal=self.ui.dispatch('choose-1','choose',{'index':1})['proposal_id']
        self.api.unknown=True
        self.ui.dispatch('confirm-1','confirm',{'proposal_id':proposal})
        attempted=len(self.api.calls)
        for action,payload in [('reset',{}),('decline',{}),('choose',{'index':1}),('confirm',{'proposal_id':proposal}),('message',{'text':'Find providers'})]:
            self.ui.dispatch('later-'+action,action,payload)
            self.assertEqual(self.ui.snapshot()['state'],'unresolved')
        self.assertEqual(len(self.api.calls),attempted)
    def test_private_identity_control_is_not_a_model_message_or_view(self):
        self.ui.dispatch('message-1','message',{'text':'Book primary care downtown'})
        self.ui.dispatch('phone-1','identity',{'phone':'555-0101'})
        self.ui.dispatch('dob-1','identity',{'dob':'1985-04-12'})
        rendered=repr(self.ui.snapshot())
        inputs=repr(self.model.inputs)
        for private in ['555-0101','1985-04-12','70112','patient1']:
            self.assertNotIn(private,rendered)
            self.assertNotIn(private,inputs)
        self.assertEqual(len(self.model.inputs),1)
    def test_only_newest_message_no_history_or_silent_replay(self):
        self.model.results=[Interpretation('provider_lookup','primary_care','downtown'),Interpretation('provider_lookup','primary_care','downtown')]
        self.ui.dispatch('message-1','message',{'text':'Find primary care providers downtown'})
        self.ui.dispatch('message-1','message',{'text':'Find primary care providers downtown'})
        self.ui.dispatch('message-2','message',{'text':'Find primary care providers downtown'})
        self.assertEqual(len(self.model.inputs),2)
        self.assertTrue(all(isinstance(text,str) for text,context in self.model.inputs))
        self.assertTrue(all('history' not in context for text,context in self.model.inputs))

class MarimoButtonTests(unittest.TestCase):
    def test_rendered_actions_retain_real_buttons_and_dispatch_click_once(self):
        import gc
        import weakref
        import marimo as mo
        import guarded_scheduling.ui_adapter as ui_module
        self.assertTrue(hasattr(ui_module,'action_buttons'),'Retained Marimo actions not implemented')
        api=MemoryApi()
        session=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(session)
        controller=ui_module.UiController(session)
        proposal=controller.dispatch('choose','choose',{'index':1})['proposal_id']
        import uuid
        def emit(action,payload=None):
            controller.dispatch(uuid.uuid4().hex,action,payload)
        controls=ui_module.action_buttons(mo,emit,proposal,False)
        confirm,decline,refresh,reset=controls
        references={key:weakref.ref(button) for key,button in zip(('confirm','decline','refresh','reset'),controls)}
        layout=mo.hstack(controls)
        from marimo._plugins.ui._core.registry import UIElementRegistry
        registry=UIElementRegistry()
        self.assertEqual(registry._find_bindings_in_namespace(confirm._id,{'confirm':confirm,'layout':layout}),{'confirm'})
        gc.collect()
        self.assertTrue(all(reference() is not None for reference in references.values()))
        # This is Marimo's actual frontend event path, including value conversion/on_change.
        confirm._update(1)
        confirm._update(2)
        self.assertEqual(len(api.bookings),1)
        self.assertEqual(controller.snapshot()['state'],'booked')
    def test_real_decline_refresh_reset_callbacks_are_live(self):
        import marimo as mo
        import guarded_scheduling.ui_adapter as ui_module
        self.assertTrue(hasattr(ui_module,'action_buttons'),'Retained Marimo actions not implemented')
        calls=[]
        controls=ui_module.action_buttons(mo,lambda action,payload=None:calls.append((action,payload)),None,False)
        confirm,decline,refresh,reset=controls
        for button in (refresh,reset):
            button._update(1)
        self.assertEqual([action for action,payload in calls],['refresh','reset'])

class ActualNotebookBindingTests(unittest.TestCase):
    def test_actual_render_cell_exports_live_confirmation_controls(self):
        import gc
        import runpy
        from pathlib import Path
        import marimo as mo
        from guarded_scheduling.ui_adapter import UiController, action_buttons
        api=MemoryApi()
        session=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(session)
        controller=UiController(session)
        controller.dispatch('select','choose',{'index':1})
        import uuid
        def emit(action,payload=None):controller.dispatch(uuid.uuid4().hex,action,payload)
        path=Path(__file__).resolve().parents[1]/'apps/scheduling.py'
        app=runpy.run_path(str(path))['app']
        render_cell=list(app._cell_manager.cells())[-1]
        output,namespace=render_cell.run(action_buttons=action_buttons,controller=controller,emit=emit,mo=mo,snapshot=controller.snapshot())
        self.assertIn('action_widgets',namespace,'Actual notebook discarded its action widgets after rendering')
        self.assertIn('confirm_button',namespace,'Actual notebook did not export a direct UIElement binding')
        gc.collect()
        namespace['confirm_button']._update(1)
        namespace['confirm_button']._update(2)
        self.assertEqual(len(api.bookings),1)
        self.assertEqual(controller.snapshot()['state'],'booked')
