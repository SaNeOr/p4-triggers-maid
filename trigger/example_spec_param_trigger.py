import os
from dataclasses import dataclass
from trigger.p4_trigger import P4Trigger, TriggerResult


@dataclass
class ExampleWithSpecParamTrigger(P4Trigger):
    spec_dir: str = ""
    changelist_id: int = 0

    def _on_trigger(self) -> TriggerResult:
        file_path = os.path.join(self.spec_dir, str(self.changelist_id))
        os.makedirs(self.spec_dir, exist_ok=True)
        file = open(file_path, "w")
        file.close()
        return self.trigger_result
