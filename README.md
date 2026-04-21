# CTP Settlement ETL & Daily Report

## 项目简介

本项目用于解析 **CTP 结算单（txt）**，并完成：

* 结算单结构化解析
* 多表入库（SQLite）
* 数据核验（勾稽规则）
* 日报生成（CSV + Markdown）

目标是将“账单文本”转化为“可分析的数据与报告”。

---

## 当前功能

### 1. 结算单解析入库

支持解析以下区块（与账单英文名称一致）：

* Account Summary（资金状况）
* Transaction Record（成交记录）
* Exercise Statement（行权明细）
* Position Closed（平仓明细）
* Positions Detail（持仓明细）
* Positions（持仓汇总）

所有字段尽量完整入库，并保留：

* `source_file`（来源文件）
* 原始 payload（用于排查）

---

### 2. 数据库存储（SQLite）

默认数据库：

```
data/settlement.db
```

主要表：

* account_summary
* transaction_record
* exercise_statement
* position_closed
* positions_detail
* positions
* validation_result
* source_file

---

### 3. 去重机制

基于文件 MD5：

* 已处理文件不会重复入库
* 文件处理状态记录在 `source_file` 表

---

### 4. 数据核验（Validation）

包含基础勾稽规则，例如：

* 平仓盈亏 vs account_summary.realized_p_l
* 持仓盯市盈亏 vs mtm_p_l
* 保证金占用 vs margin_occupied
* 多头/空头市值 vs account_summary

核验结果写入：

```
validation_result
```

并在日志中输出：

```
核验结果: total=11, pass=11, warn=0, fail=0
```

---

### 5. 日报生成（核心功能）

日报基于 SQL 生成：

```
app/sql/report_daily_summary_v2.sql
```

输出：

```
output/
├─ daily_report.csv
├─ daily_report_YYYY-MM-DD.md
```

---

## 日报逻辑（核心口径）

### 1. 期货盈亏

```
futures_pnl = realized_p_l + mtm_p_l
```

---

### 2. 期权相关

#### 当日期权市值

```
option_market_value = market_value_long - market_value_short
```

#### 权利金变动

```
premium_change = premium_received - premium_paid
```

#### 上日期权市值

* 使用窗口函数 LAG
* 首日默认 = 0

#### 期权市值变动

```
option_market_value_change = option_market_value - prev_option_market_value
```

#### 期权盈亏

```
option_pnl = premium_change + option_market_value_change
```

---

### 3. 当日总盈亏

```
total_pnl = futures_pnl + option_pnl
```

---

### 4. 客户权益勾稽

（使用结存作为上日权益近似）

```
balance_b_f
+ deposit_withdrawal
- total_fee
+ premium_change
+ futures_pnl
= client_equity
```

---

### 5. 市值权益勾稽

```
client_equity
+ option_market_value_change
= market_value_equity
```

---

## 日志设计

分两层：

### 控制台（INFO）

* 文件处理
* 入库结果
* 核验结果
* 日报生成

### 文件日志（DEBUG）

路径：

```
logs/app.log
```

包含：

* 区块解析详情
* 调试信息

---

## 项目结构

```
app/
├─ main.py
├─ config.py
├─ db/
├─ parsers/
├─ services/
├─ reports/
│  ├─ daily_report_service.py
│  ├─ markdown_builder.py
│  └─ sql_loader.py
├─ sql/
│  ├─ init_tables.sql
│  ├─ report_daily_summary.sql
│  └─ report_daily_summary_v2.sql
├─ utils/
```

---

## 使用方式

### 1. 放入结算单

```
input/
```

---

### 2. 运行

```
python -m app.main
```

---

### 3. 输出结果

```
archive/      已处理文件
error/        失败文件
output/       日报
logs/         日志
```

---

## 当前进度

已完成：

* ETL 入库
* 核验规则
* 日报（归因版）
* Markdown 报告（带颜色）

---

## 下一步计划

1. **按品类分析（重点）**

   * 生猪 + 生猪期权 → 生猪
   * 输出品类盈亏贡献

2. 多日收益分析

3. 风险预警（高风险度提示）

4. Excel 报表输出

---

## 说明

本项目当前为单账户/多账单场景设计，已具备扩展为：

* 多账户系统
* 报表系统
* 风控系统

的基础能力。
