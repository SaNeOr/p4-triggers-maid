from dataclasses import dataclass
from trigger.p4_trigger import P4Trigger, TriggerResult


@dataclass
class ExampleTrigger(P4Trigger):
    desc: str = ""

    def _on_trigger(self) -> TriggerResult:
        if "#" in self.desc:
            return self.trigger_result
        self.trigger_result = TriggerResult(1, "submit description invalid!")
        return self.trigger_result
