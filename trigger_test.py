import unittest
import maid
import typer
from typer.testing import CliRunner
import main
from main import app
import maid.utils

runner = CliRunner()


class TriggerCase(unittest.TestCase):
    def setUp(self):
        main.config = maid.utils.P4ConnectConfig.get_test_config()

    def test_desc_limit(self):
        result = runner.invoke(app, ["desc_limit", "9527", "maid"])
        typer.echo(result.stdout)
        self.assertEqual(result.exit_code, 0)

    def test_save_submit(self):
        result = runner.invoke(app, ["save_submit", "9527", "./temp/"])
        typer.echo(result.stdout)
        self.assertEqual(result.exit_code, 0)

    def test_submit_forbid(self):
        result = runner.invoke(app, ["submit_forbid"])
        self.assertEqual(result.exit_code, 1)
        typer.echo(result.stdout)
        assert "==> The current branch cannot be submitted temporarily, you can contact the god <==" in result.stdout

    def test_update_p4_trigger(self):
        result = runner.invoke(app, ["update_p4_trigger"])
        typer.echo(result.stdout)
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
