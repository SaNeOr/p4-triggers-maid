from dataclasses import dataclass


@dataclass
class P4ConnectConfig:
    p4_port: str
    p4_user: str
    p4_password: str = None

    @staticmethod
    def get_inner_config():
        inner_config = P4ConnectConfig("ssl:1666", "your_admin_user",
                                       "your_admin_password")
        return inner_config

    @staticmethod
    def get_test_config():
        test_config = P4ConnectConfig("ssl:1666", "your_test_user",
                                      "your_test_password")
        return test_config
