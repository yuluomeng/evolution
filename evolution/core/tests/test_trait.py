from evolution.core.trait import Trait


def test_trait_order():
    assert Trait.carnivore < Trait.foraging < Trait.symbiosis
