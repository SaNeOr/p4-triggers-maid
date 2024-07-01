import typer
from enum import Enum
from maid.p4_connect_config import P4ConnectConfig
import maid.utils
import maid

app = typer.Typer()
config = P4ConnectConfig.get_inner_config()


class TriggerOn(Enum):
    PreSubmit = "change-content",
    PostSubmit = "change-commit",


def p4_trigger(
        name: str,
        trigger_on: TriggerOn,
        depot_path: str,
        param: str = ""):
    def decorator(func):
        return func

    return decorator


@p4_trigger("desc_limit.release", TriggerOn.PreSubmit,
            "//repo/release/...")
@p4_trigger("desc_limit.dev", TriggerOn.PreSubmit,
            "//repo/dev/...")
@app.command("desc_limit")
def desc_limit(change, user):
    import example_filter
    from trigger.example_trigger import ExampleTrigger
    submit_files = maid.utils.get_submit_files(config, change)
    desc = maid.utils.get_submit_description(config, change).strip()
    command = ExampleTrigger(
        desc=desc,
        enable_filter=True, enable_super_administrator=True,
        user=user,
        files=submit_files,
        trigger_filter=example_filter.trigger_filter,
    )
    res = command.trigger()
    typer.echo(res.log_info)
    exit(res.ret_code)


@p4_trigger("save_submit", TriggerOn.PreSubmit,
            "//repo/dev/...",
            "%change%")
@app.command("save_submit")
def save_submit(change_id,
                spec_dir: str = typer.Option("/p4/spec_dir",
                                             "-r",
                                             help="spec dir root")):
    from trigger.example_spec_param_trigger import ExampleWithSpecParamTrigger

    desc_raw = maid.utils.get_submit_description(config, change_id).strip()
    try:
        changelist_id = int(desc_raw)
    except ValueError:
        typer.echo("description should be a single integer!")
        exit(1)

    command = ExampleWithSpecParamTrigger(
        spec_dir=spec_dir,
        changelist_id=changelist_id,
    )
    res = command.trigger()
    typer.echo(res.log_info)
    exit(res.ret_code)


@p4_trigger("submit_forbid", TriggerOn.PreSubmit,
            "//repo/release...")
@app.command(name="submit_forbid")
def submit_forbid():
    typer.echo("==> The current branch cannot be submitted temporarily, you can contact the god <==")
    exit(1)


# @p4_trigger("update_p4_triggers_table", TriggerOn.PostSubmit,
#             "//repo/.triggers/main.py")
@app.command("update_p4_trigger")
def update_p4_trigger():
    from trigger.update_p4_trigger import UpdateP4Trigger
    origin_p4_triggers = maid.utils.get_p4_trigger(config)
    command = UpdateP4Trigger(
        p4_triggers=origin_p4_triggers
    )
    res = command.trigger()
    typer.echo(res.log_info)
    if res.ret_code == 0:
        maid.utils.set_p4_trigger(config, command.p4_triggers)
        typer.echo("Triggers saved.")
    else:
        typer.echo("Triggers not changed.")
    exit(res.ret_code)


if __name__ == "__main__":
    app()
