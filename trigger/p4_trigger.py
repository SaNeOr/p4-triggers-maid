import re
from abc import ABC, abstractmethod
from typing import List
from typing import final
from dataclasses import dataclass

super_administrator = ["maid", "sero", "admin"]


@dataclass
class Whitelist:
    prefix: []
    users: []


@dataclass
class TriggerFilter:
    super_user: [] = None
    include_set: [] = None
    exclude_set: [] = None
    white_list: List[Whitelist] = None
    check_stream: [] = None


@dataclass
class TriggerResult:
    ret_code: int = 0
    log_info: str = ""


@dataclass
class P4Trigger(ABC):
    enable_filter: bool = False
    enable_super_administrator: bool = False
    user: str = None
    stream: str = None
    files: [] = None
    trigger_filter: TriggerFilter = None
    trigger_result: TriggerResult = TriggerResult(0, "")

    def __is_filtered(self) -> bool:
        if not self.files:
            return True

        if (self.trigger_filter.check_stream and self.stream
                and self.stream not in self.trigger_filter.check_stream):
            return True

        if self.trigger_filter.exclude_set is not None:
            is_ignore = True
            for path in self.files:
                current_file_is_ignore = False
                for pattern in self.trigger_filter.exclude_set:
                    if re.match(pattern, path):
                        current_file_is_ignore = True
                        break
                if not current_file_is_ignore:
                    is_ignore = False
                    break
            if is_ignore:
                return True

        if self.trigger_filter.include_set is None:
            return False
        is_white_user = False
        is_match = False
        for path in self.files:
            is_white_user = False
            for pattern in self.trigger_filter.include_set:
                match = re.match(pattern, path)
                if match:
                    is_match = True
                    if self.trigger_filter.white_list is None:
                        return False
                    match_prefix = match.group()
                    for white in self.trigger_filter.white_list:
                        if match_prefix in white.prefix and self.user and self.user in white.users:
                            is_white_user = True
                            break
                    if not is_white_user:
                        return False
                    break
        if not is_match:
            return True
        if is_white_user:
            return True
        return False

    @final
    def trigger(self) -> TriggerResult:
        if self.enable_super_administrator and self.user is not None:
            if self.user in super_administrator:
                return self.trigger_result

        if self.enable_filter:
            if self.__is_filtered():
                return self.trigger_result

        result = self._on_trigger()
        return result

    @abstractmethod
    def _on_trigger(self) -> TriggerResult:
        pass
