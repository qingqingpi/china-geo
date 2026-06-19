"""规则自注册表——让"一规则一文件 + 装饰器注册"成立，新增检查只需写文件。

设计移植自 SEOmator `registry.ts`（Map 去重）+ `loader.ts`（import 即注册）。
用独立 Registry 实例测试，避免污染被真实规则填充的全局 REGISTRY。
"""
import pytest

from seogeo.rules.base import Registry


def test_register_adds_rule():
    reg = Registry()

    @reg.register(id="x-test", category="technical", weight=5)
    def _r(ctx):
        return None

    rules = reg.all()
    assert len(rules) == 1
    assert rules[0].id == "x-test"
    assert rules[0].category == "technical"
    assert rules[0].weight == 5


def test_duplicate_id_raises():
    reg = Registry()

    @reg.register(id="dup", category="technical", weight=1)
    def _a(ctx):
        return None

    with pytest.raises(ValueError):
        @reg.register(id="dup", category="domestic", weight=1)
        def _b(ctx):
            return None


def test_registered_function_stays_callable():
    reg = Registry()

    @reg.register(id="run-test", category="domestic", weight=3)
    def _r(ctx):
        return "ran"

    assert reg.all()[0].run(None) == "ran"


def test_get_by_id():
    reg = Registry()

    @reg.register(id="findme", category="discovery", weight=2)
    def _r(ctx):
        return None

    assert reg.get("findme").category == "discovery"
    assert reg.get("nope") is None
