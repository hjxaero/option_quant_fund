"""Verify core package and submodules import without error."""


def test_import_option_quant_fund():
    import option_quant_fund

    assert option_quant_fund.__version__ == "0.1.0"


def test_import_data_loader():
    from option_quant_fund.data import loader

    assert hasattr(loader, "DataLoader")


def test_import_option_chain_builder():
    from option_quant_fund.option_chain import chain_builder

    assert hasattr(chain_builder, "ChainBuilder")


def test_import_greeks_black_scholes():
    from option_quant_fund.greeks import black_scholes

    assert hasattr(black_scholes, "GreeksCalculator")


def test_import_backtest_engine():
    from option_quant_fund.backtest import engine

    assert hasattr(engine, "BacktestEngine")


def test_import_risk_limits():
    from option_quant_fund.risk import limits

    assert hasattr(limits, "RiskLimits")
