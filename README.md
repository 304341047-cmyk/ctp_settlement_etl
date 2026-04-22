# CTP Settlement ETL

基于 CTP 期货/期权交易结算单的 ETL 工具，用于批量解析结算单文本、标准化字段、写入 SQLite，并自动生成核验结果与日报。

## 项目简介

这个项目面向日常结算单处理场景，目标是把原始文本结算单转成可查询、可校验、可追溯的数据资产，减少手工整理和重复核对的工作量。

核心能力包括：

- 批量解析 CTP 结算单文本
- 标准化不同区块和字段格式
- 写入 SQLite 数据库
- 自动执行数据一致性核验
- 生成 Markdown / CSV 日报
- 基于文件 MD5 防止重复入库

## 功能特性

### 1. 结算单解析

当前支持解析的主要区块：

- 资金状况
- 出入金明细
- 成交记录
- 行权明细
- 平仓明细
- 持仓明细
- 持仓汇总

已适配部分新版结算单字段：

- `Premium Received/Paid`
- `Pos. Open Price / Trans. Price`
- `Settlement Price`
- `Market Value(Options)`
- `Long Pos. / Short Pos.`

### 2. 数据入库

解析结果会写入 SQLite，当前包含以下核心表：

- `account_summary`
- `deposit_withdrawal`
- `transaction_record`
- `exercise_statement`
- `position_closed`
- `positions_detail`
- `positions`
- `validation_result`
- `source_file_record`

其中 `source_file_record` 用于记录源文件与 MD5，避免重复处理。

### 3. 数据核验

当前已实现的核验项包括：

- 客户权益勾稽
- 市值权益勾稽
- 风险度校验
- 出入金一致性检查
- 手续费检查
- 持仓市值检查

核验规则说明：

- 无相关区块时自动跳过，不记为告警
- 字段缺失记为 `WARN`
- 数值异常记为 `FAIL`

### 4. 日报生成

处理完成后会自动生成日报，支持：

- Markdown 报表
- CSV 导出

日报内容包括：

- 总览
- 盈亏归因
- 期权市值
- 交易概览
- 持仓概览
- 行权概览
- 核验结果

### 5. 防重复处理

系统基于文件内容 MD5 做去重：

- 自动识别重复文件
- 已处理文件不会重复入库
- 重复文件仍会归档保存

## 快速开始

### 环境要求

- Python 3.10+
- SQLite（Python 内置 `sqlite3` 即可）

### 安装

项目当前没有额外第三方依赖，克隆后即可直接运行。

```bash
python --version
```

### 准备输入文件

将待处理的结算单文本放入 `input/` 目录，例如：

```text
input/
├─ 结算单_20251020.txt
└─ 结算单_20251024.txt
```

### 运行

```bash
python -m app.main
```

首次运行会自动完成以下动作：

- 创建数据目录
- 初始化 SQLite 表结构
- 扫描 `input/*.txt`
- 解析并入库
- 执行核验
- 生成日报

## 输出结果

处理结果会落到以下目录：

| 类型 | 位置 |
| --- | --- |
| SQLite 数据库 | `data/settlement.db` |
| 成功归档文件 | `processed_data/archive/` |
| 失败文件 | `processed_data/error/` |
| 日报输出 | `processed_data/output/` |
| 日志 | `logs/` |

## 项目结构

```text
ctp_settlement_etl/
├─ app/
│  ├─ extractors/
│  ├─ models/
│  ├─ normalizers/
│  ├─ parsers/
│  ├─ reports/
│  ├─ repositories/
│  ├─ services/
│  ├─ sql/
│  ├─ utils/
│  ├─ config.py
│  ├─ db.py
│  ├─ db_writer.py
│  └─ main.py
├─ data/
│  └─ settlement.db
├─ input/
├─ logs/
├─ processed_data/
│  ├─ archive/
│  ├─ error/
│  └─ output/
├─ README.md
└─ requirements.txt
```

## 处理流程

```text
结算单文本 -> 读取与解析 -> 字段标准化 -> 写入 SQLite -> 数据核验 -> 生成日报 -> 文件归档
```

## 设计原则

- 字段统一化：避免源账单字段直接污染内部数据模型
- 宽容解析：尽可能兼容字段增减，不因轻微格式变化直接阻断流程
- 原始数据保留：保留原始载荷，便于追溯与排查
- 结果可核验：数据入库后附带一致性校验
- 防重复处理：同内容文件不会重复入库

## 当前适用场景

目前项目已经覆盖以下数据能力：

- 单日完整交易数据处理
- 持仓数据处理
- 行权数据处理
- 资金变动处理
- 手续费统计

如果后续需要扩展更多结算单格式或新增报表维度，可以继续在 `parsers/`、`normalizers/`、`reports/` 下迭代。

## License

当前仓库内容仅供个人学习与数据分析使用。
