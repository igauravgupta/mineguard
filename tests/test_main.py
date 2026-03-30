from conftest import reload_module


class DummyAgent:
    def detect_intent(self, prompt: str) -> str:
        return "legal query"


def test_main_prints_response(monkeypatch, capsys):
    main_module = reload_module("main")

    monkeypatch.setattr(main_module, "QueryUnderstandAgent", lambda: DummyAgent())
    main_module.main()

    captured = capsys.readouterr()
    assert "Detected intent: legal query" in captured.out
