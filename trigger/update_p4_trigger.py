import ast
import inspect
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from trigger.p4_trigger import P4Trigger, TriggerResult
import main

TriggerOn = main.TriggerOn
command_prefix = "python3 /p4/triggers/main.py"


def enum_to_str(enum_value):
    if isinstance(enum_value, TriggerOn):
        return enum_value.value[0]
    return str(enum_value)


@dataclass
class Command:
    trigger_name: str
    trigger_on: str
    depot_path: str
    command: str

    def to_string(self) -> str:
        return f'{self.trigger_name} {self.trigger_on} {self.depot_path} {self.command}'


def parse_command_string(command_string: str) -> Command:
    parts = command_string.split(' ', 3)
    return Command(
        trigger_name=parts[0],
        trigger_on=parts[1],
        depot_path=parts[2],
        command=parts[3],
    )


def deserialize_commands(command_strings: List[str]) -> List[Command]:
    return [parse_command_string(cs) for cs in command_strings]


def serialize_commands(commands: List[Command]) -> List[str]:
    return [command.to_string() for command in commands]


def get_metadata(func):
    return getattr(func, "__metadata__", [])


def is_p4_trigger_decorator(decorator) -> bool:
    if isinstance(decorator, ast.Name):
        return decorator.id == 'p4_trigger'
    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
        return decorator.func.id == 'p4_trigger'
    elif isinstance(decorator, ast.Attribute):
        return decorator.attr == 'p4_trigger'
    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
        return decorator.func.attr == 'p4_trigger'
    return False


def get_decorator_args(decorator, module) -> Dict[str, Any]:
    args = {}
    if isinstance(decorator, ast.Call):
        for keyword in decorator.keywords:
            value = keyword.value
            if isinstance(value, ast.Attribute) and value.attr in TriggerOn.__members__:
                args[keyword.arg] = getattr(module.TriggerOn, value.attr)
            else:
                args[keyword.arg] = ast.literal_eval(keyword.value)
        for i, arg in enumerate(decorator.args):
            if isinstance(arg, ast.Attribute) and arg.attr in TriggerOn.__members__:
                args[f'arg{i + 1}'] = getattr(module.TriggerOn, arg.attr)
            else:
                args[f'arg{i + 1}'] = ast.literal_eval(arg)
    return args


def get_function_info(node) -> Tuple[str, List[str]]:
    func_name = node.name
    func_args = [arg.arg for arg in node.args.args]
    return func_name, func_args


def get_p4_trigger_functions_info(module) -> List[Dict[str, Any]]:
    source = inspect.getsource(module)
    tree = ast.parse(source)
    functions_info = []

    class P4TriggerVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            command_name = ""
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr == 'command'):
                    decorator_args = get_decorator_args(decorator, module)
                    command_name = list(decorator_args.values())[0]
                    break

            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Name)
                        and decorator.func.id == 'p4_trigger'):
                    decorator_args = get_decorator_args(decorator, module)
                    func_name, func_args = get_function_info(node)
                    functions_info.append({
                        # 'function_name': func_name,
                        'function_name': command_name,
                        'function_args': func_args,
                        'decorator_args': decorator_args,
                    })

            self.generic_visit(node)

    visitor = P4TriggerVisitor()
    visitor.visit(tree)

    return functions_info


def create_command_from_info(info: Dict[str, Any]) -> Command:
    trigger_name = f"auto.{info['decorator_args']['arg1']}"
    trigger_on = enum_to_str(info['decorator_args']['arg2'])
    depot_path = info['decorator_args']['arg3']

    if 'arg4' in info['decorator_args']:
        command_param = info['decorator_args']['arg4']
    else:
        command_param = " ".join([f"%{arg}%" for arg in info['function_args']])
    command = (f"\"{command_prefix} {info['function_name']} " +
               command_param +
               "\"")
    return Command(trigger_name, trigger_on, depot_path, command)


def mix_commands(original_commands: List[Command], new_commands: List[Command]) -> List[Command]:
    add_commands = []

    filtered_list = [item for item in original_commands if not item.trigger_name.startswith("auto.")]

    for command in new_commands:
        is_exist = False
        for original_command in filtered_list:
            if (command.trigger_on == original_command.trigger_on
                    and command.depot_path == original_command.depot_path
                    and command.command == original_command.command):
                is_exist = True
                break
        if not is_exist:
            add_commands.append(command)

    filtered_list += add_commands
    return filtered_list


@dataclass
class UpdateP4Trigger(P4Trigger):
    p4_triggers: [] = None

    def _on_trigger(self) -> TriggerResult:
        origin_commands = deserialize_commands(self.p4_triggers)
        functions_info = get_p4_trigger_functions_info(main)
        # commands = origin_commands + [create_command_from_info(info) for info in functions_info]
        commands = mix_commands(origin_commands, [create_command_from_info(info) for info in functions_info])
        self.p4_triggers = serialize_commands(commands)
        return self.trigger_result
