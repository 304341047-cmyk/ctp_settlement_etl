# CTP Settlement ETL

基于 CTP 期货/期权交易结算单文本的轻量级 ETL 工具。项目用于批量解析结算单、标准化字段、写入 SQLite，并生成数据校验结果和 Markdown/CSV 日报。

## 功能概览

- 批量读取 `input/` 目录下的 CTP 结算单文本
- 解析资金状况、出入金、成交、平仓、行权、持仓明细、持仓汇总等区块
- 标准化中英文表头和金额字段
- 写入本地 SQLite 数据库
- 基于文件 MD5 防止同一内容重复入库
- 自动执行数据一致性校验
- 自动生成 Markdown 和 CSV 日报
- 支持同一天多个账户的结算单分账户入库和统计

## 适用场景

这个项目适合日常结算单处理、复盘和核对：

- 将原始文本结算单沉淀为可查询的结构化数据
- 快速核对客户权益、风险度、出入金、手续费等关键指标
- 汇总多日、多账户的交易和持仓情况
- 保留源文件、解析结果、校验结果，方便追溯问题

## 目录结构

```text
ctp_settlement_etl/
├─ app/
│  ├─ extractors/       # 文本读取、区块切分、表格提取
│  ├─ models/           # 数据模型
│  ├─ normalizers/      # 字段名和值清洗
│  ├─ parsers/          # CTP 结算单解析器
│  ├─ reports/          # 日报查询和 Markdown 构建
│  ├─ repositories/     # SQLite 写入层
│  ├─ services/         # 校验服务
│  ├─ sql/              # 建表和报表 SQL
│  ├─ utils/            # 文件、日志、哈希工具
│  ├─ config.py
│  ├─ db.py
│  ├─ db_writer.py
│  └─ main.py
├─ data/                # SQLite 数据库输出目录
├─ input/               # 待处理结算单
├─ logs/                # 运行日志
├─ processed_data/
│  ├─ archive/          # 成功处理后的归档文件
│  ├─ error/            # 处理失败文件
│  └─ output/           # Markdown/CSV 日报
├─ README.md
├─ LICENSE
└─ requirements.txt
```

## 环境要求

- Python 3.10+
- SQLite，使用 Python 标准库 `sqlite3`

当前项目没有额外第三方依赖。

## 快速开始

1. 克隆项目：

```bash
git clone <your-repo-url>
cd ctp_settlement_etl
```

2. 检查 Python 版本：

```bash
python --version
```

3. 将结算单文本放入 `input/`：

```text
input/
├─ 结算单_20260414_81183126.txt
└─ 结算单_20260414_88189277.txt
```

4. 运行 ETL：

```bash
python -m app.main
```

首次运行会自动创建所需目录、初始化 SQLite 表结构、扫描 `input/*.txt`、解析入库、执行校验并生成日报。

## 多账户处理说明

同一天多个账户可以一起放入 `input/`。建议文件名带上日期和账户号：

```text
结算单_20260414_81183126.txt
结算单_20260414_88189277.txt
```

程序会从结算单头部提取 `AccountID`，并回填到明细记录中。日报 SQL 会按 `account_id` 分账户聚合，避免不同账户之间的成交、持仓、上一日市值互相串账。

注意事项：

- 文件去重基于文件内容 MD5，而不是文件名。
- 同一份内容即使改名，也会被识别为重复文件并跳过入库。
- 建议不同账户、不同日期使用清晰且唯一的文件名，便于归档和追溯。

## 输出结果

| 类型 | 位置 |
| --- | --- |
| SQLite 数据库 | `data/settlement.db` |
| 成功归档文件 | `processed_data/archive/` |
| 失败文件 | `processed_data/error/` |
| Markdown/CSV 日报 | `processed_data/output/` |
| 日志 | `logs/` |

这些运行产物默认已在 `.gitignore` 中排除，上传 GitHub 前不建议提交真实结算单、数据库、日志或报表输出。

## 数据表

主要表包括：

- `account_summary`
- `deposit_withdrawal`
- `transaction_record`
- `exercise_statement`
- `position_closed`
- `positions_detail`
- `positions`
- `validation_result`
- `source_file_record`

其中 `source_file_record` 记录源文件名、MD5 和处理状态，用于避免重复处理。

## 校验规则

当前实现的校验项包括：

- 客户权益勾稽
- 市值权益勾稽
- 风险度检查
- 出入金一致性检查
- 手续费非负检查
- 持仓市值非负检查

校验状态：

- `PASS`：校验通过
- `WARN`：字段缺失或业务条件不足，无法严格校验
- `FAIL`：数值差异超过容忍度

## 处理流程

```text
结算单文本
  -> 读取与区块切分
  -> 表格解析
  -> 字段标准化
  -> 写入 SQLite
  -> 数据校验
  -> 生成日报
  -> 文件归档
```

## 开发说明

常用命令：

```bash
python -m app.main
python -m compileall app
```

如果需要扩展新的结算单格式，优先查看：

- `app/parsers/ctp_settlement_parser.py`
- `app/normalizers/field_mapper.py`
- `app/extractors/table_parser.py`

如果需要扩展日报口径，优先查看：

- `app/sql/report_daily_summary_v2.sql`
- `app/reports/daily_report_service.py`
- `app/reports/markdown_builder.py`

## 隐私和合规提醒

结算单可能包含账户、客户姓名、交易流水和资金信息。公开仓库前请确认：

- 不提交 `data/*.db`
- 不提交 `input/*.txt`
- 不提交 `processed_data/archive/*`
- 不提交 `processed_data/output/*`
- 不提交 `logs/*.log`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
