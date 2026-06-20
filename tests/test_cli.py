"""CLI dispatch 健壮性——手写参数解析的边角，坏输入不该悄悄做错事。"""
from seogeo.cli import main


def test_audit_rejects_flag_as_url(capsys):
    # `seogeo audit --format`：--format 不该被当成 URL 去体检（旧版会体检 "https://--format"），
    # 应识别出"缺少 URL"并提示用法。
    code = main(["audit", "--format"])
    assert code == 2
    assert "用法" in capsys.readouterr().out


def test_audit_empty_prints_usage(capsys):
    code = main(["audit"])
    assert code == 2
    assert "用法" in capsys.readouterr().out
