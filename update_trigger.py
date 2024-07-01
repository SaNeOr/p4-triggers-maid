import sys
import os
from dataclasses import dataclass
from P4 import P4, P4Exception


@dataclass
class Config:
    p4_port: str
    p4_user: str
    p4_password: str = None
    trigger_dir: str = None
    trigger_depot_root: str = None
    changelist_id: str = None


def connect(config: Config) -> P4:
    try:
        p4 = P4()
        p4.port = config.p4_port
        p4.user = config.p4_user
        if config.p4_password is not None:
            p4.password = config.p4_password

        p4.connect()
        return p4
    except P4Exception:
        for e in p4.errors:  # Display errors
            print("p4 error", e)
            raise P4Exception
    except Exception as e:
        print(e)
        raise Exception


def get_content(config: Config, depot_path: str) -> str:
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


def get_submit_files(config: Config) -> []:
    try:
        p4 = connect(config)
        changelist_id = config.changelist_id
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


def write_trigger(config: Config, files):
    for file in files:
        # file_name = os.path.basename(file)
        root = config.trigger_depot_root
        if root not in file:
            print(f"{file} is not under {root}, trigger scripts update is not triggered")
            continue

        file_path = str.replace(file, config.trigger_depot_root, config.trigger_dir)
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        # target_path = os.path.abspath(trigger_dir + "/" + file_path)
        doc = get_content(config, file)
        with open(file_path, "w", encoding='utf-8') as file:
            if doc is None:
                doc = ""
            file.write(doc)

        print(f"trigger update: {file_path}")


def main():
    # config: Config = Config(trigger_dir="./temp", trigger_depot_root="depot",
    #                         changelist_id=9527, p4_port="ssl:1666", p4_user="your_test_user")

    config: Config = Config(trigger_dir="/p4/triggers", trigger_depot_root="//repo/scripts/trigger_maid",
                            changelist_id=sys.argv[1], p4_port="ssl:1666", p4_user="your_admin_user",
                            p4_password="your_admin_password")

    files = get_submit_files(config)
    if not files:
        print("No submission files found")
        exit(0)

    write_trigger(config, files)
    print("===> update completed <====")


if __name__ == "__main__":
    main()
