from conftest import reload_module


class DummyProvider:
    def generate_response(self, prompt: str) -> str:
        return "ok"


def test_main_prints_response(monkeypatch, capsys):
    main_module = reload_module("main")

    monkeypatch.setattr(main_module, "LLMProvider", lambda: DummyProvider())
    main_module.main()

    captured = capsys.readouterr()
    assert "LLM response: ok" in captured.out
