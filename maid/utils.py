from P4 import P4, P4Exception
from maid.p4_connect_config import P4ConnectConfig


def connect(config: P4ConnectConfig) -> P4:
    try:
        p4 = P4()
        if p4.connected():
            p4.disconnect()
        p4.port = config.p4_port
        p4.user = config.p4_user
        if config.p4_password is not None:
            p4.password = config.p4_password

        p4.connect()
        try:
            p4.run_login("-s")
        except P4Exception:
            p4.run_login()

        return p4
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            raise P4Exception
    except Exception as e:
        print(e)
        raise Exception


def get_content(config: P4ConnectConfig, depot_path: str) -> str:
    try:
        p4 = connect(config)

        run_result = p4.run("print", depot_path)
        doc = run_result[1].decode(encoding='utf8')
        p4.disconnect()
        return doc
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            return ""
    except Exception as e:
        print(e)


def get_submit_files(config: P4ConnectConfig, changelist_id: int) -> []:
    try:
        p4 = connect(config)
        ret = p4.run("describe", changelist_id)
        ret_files = []
        if len(ret) > 0 and 'depotFile' in ret[0]:
            ret_files = ret[0]["depotFile"]
            for f in ret_files[:]:
                print("file:", f)

        if len(ret_files) == 0:
            shelved_files = p4.run(f"files", f"@={changelist_id}")
            for file_info in shelved_files:
                depot_file = file_info["depotFile"]
                # file_name, file_extension = os.path.splitext(depotFile)
                print(f"shelved file: {depot_file}")
                ret_files.append(depot_file)

        p4.disconnect()
        return ret_files
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            exit(0)

    return []


def get_describe(config: P4ConnectConfig, changelist_id: int) -> {}:
    try:
        p4 = connect(config)
        ret = p4.run("describe", changelist_id)
        p4.disconnect()
        return ret[0]
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            exit(0)

    return {'desc': ""}


def get_stream(config: P4ConnectConfig, client: str) -> str:
    try:
        p4 = connect(config)

        stream = ""
        run_result = p4.run("client", "-o", client)
        if len(run_result) > 0 and 'Stream' in run_result[0]:
            stream = run_result[0]["Stream"]
        p4.disconnect()
        return stream
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            return ""
    except Exception as e:
        print(e)


def get_submit_description(config: P4ConnectConfig, changelist_id: int) -> str:
    try:
        p4 = connect(config)
        details = p4.fetch_change(changelist_id)
        description = details['Description']

        p4.disconnect()
        return description
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            exit(0)

    return ""


def get_p4_trigger(config: P4ConnectConfig) -> str:
    try:
        p4 = connect(config)
        triggers = p4.run("triggers", "-o")

        p4.disconnect()
        return triggers[0]['Triggers']
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            exit(0)

    return ""


def set_p4_trigger(config: P4ConnectConfig, job_triggers: []):
    try:
        p4 = connect(config)
        triggers = p4.fetch_triggers()
        triggers._triggers = job_triggers
        p4.save_triggers(triggers)
        p4.disconnect()
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            exit(0)
