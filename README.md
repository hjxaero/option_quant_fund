# option_quant_fund

期权量化研究平台 MVP（Control Lane / TASK-001）。

本项目用于期权数据读取、期权链构建、Greeks 计算、回测与基础风险限制的**研究与回测骨架**。

**当前版本不是实盘交易系统。** 不包含券商接口、自动下单、OMS/EMS 或任何真实账户配置。

## 模块结构

| 模块 | 职责 |
|------|------|
| `data` | 数据读取与标准化接口占位 |
| `option_chain` | 期权链构建接口占位 |
| `greeks` | Greeks 计算接口占位 |
| `backtest` | 回测流程接口占位 |
| `risk` | 基础风险限制接口占位 |
| `experiments` | Fast Lane 实验区（可丢弃原型） |
| `notebooks` | 研究演示与数据探索 |

## 开发

```bash
python -m pytest
```

## 目录说明

- `src/option_quant_fund/` — Python package 根目录
- `configs/` — 基础占位配置（无生产/账户信息）
- `docs/` — 架构、数据字典、路线图
- `data/` — 原始、处理后与 sample 数据目录
- `tests/` — 最小结构与健康检查测试
