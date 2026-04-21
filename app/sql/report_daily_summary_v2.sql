WITH base AS (
    SELECT
        a.source_file,
        a.creation_date,
        a.date_from,
        a.date_to,
        a.client_id,
        a.client_name,
        a.account_id,
        a.currency,

        a.balance_b_f,
        a.balance_c_f,
        a.deposit_withdrawal,
        a.realized_p_l,
        a.mtm_p_l,
        a.market_value_short,
        a.market_value_long,
        a.market_value_equity,
        a.client_equity,
        a.commission,
        a.exercise_fee,
        a.delivery_fee,
        a.premium_received,
        a.premium_paid,
        a.fund_avail,
        a.margin_occupied,
        a.risk_degree,

        -- 当日期权市值
        COALESCE(a.market_value_long, 0) - COALESCE(a.market_value_short, 0) AS option_market_value,

        -- 当日权利金变动
        COALESCE(a.premium_received, 0) - COALESCE(a.premium_paid, 0) AS premium_change,

        -- 当日期货盈亏
        COALESCE(a.realized_p_l, 0) + COALESCE(a.mtm_p_l, 0) AS futures_pnl,

        -- 手续费总额
        COALESCE(a.commission, 0) + COALESCE(a.exercise_fee, 0) + COALESCE(a.delivery_fee, 0) AS total_fee
    FROM account_summary a
),
base_with_prev AS (
    SELECT
        b.*,
        LAG(b.option_market_value) OVER (
            PARTITION BY b.account_id
            ORDER BY b.date_from, b.source_file
        ) AS prev_option_market_value_raw
    FROM base b
),
transaction_record_agg AS (
    SELECT
        source_file,
        COUNT(*) AS transaction_count,
        COALESCE(SUM(lots), 0) AS transaction_lots_sum,
        COALESCE(SUM(turnover), 0) AS transaction_turnover_sum
    FROM transaction_record
    GROUP BY source_file
),
exercise_statement_agg AS (
    SELECT
        source_file,
        COUNT(*) AS exercise_statement_count,
        COALESCE(SUM(volume_exercised), 0) AS exercise_volume_sum,
        COALESCE(SUM(exercise_p_l), 0) AS exercise_p_l_sum
    FROM exercise_statement
    GROUP BY source_file
),
positions_agg AS (
    SELECT
        source_file,
        COUNT(*) AS positions_count,
        COALESCE(SUM(long_pos), 0) AS positions_long_pos_sum,
        COALESCE(SUM(s_pos), 0) AS positions_s_pos_sum
    FROM positions
    GROUP BY source_file
),
validation_agg AS (
    SELECT
        source_file,
        COUNT(*) AS validation_total,
        SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS validation_pass,
        SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS validation_warn,
        SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS validation_fail
    FROM validation_result
    GROUP BY source_file
)
SELECT
    b.source_file,
    b.creation_date,
    b.date_from,
    b.date_to,
    b.client_id,
    b.client_name,
    b.account_id,
    b.currency,

    -- 资金核心
    b.balance_b_f,
    b.balance_c_f,
    b.deposit_withdrawal,
    b.client_equity,
    b.market_value_equity,
    b.market_value_long,
    b.market_value_short,
    b.option_market_value,
    b.fund_avail,
    b.margin_occupied,
    b.risk_degree,

    -- 费用与收支
    b.commission,
    b.exercise_fee,
    b.delivery_fee,
    b.total_fee,
    b.premium_received,
    b.premium_paid,
    b.premium_change,

    -- 盈亏归因
    b.realized_p_l,
    b.mtm_p_l,
    b.futures_pnl,
    COALESCE(b.prev_option_market_value_raw, 0) AS prev_option_market_value,
    b.option_market_value - COALESCE(b.prev_option_market_value_raw, 0) AS option_market_value_change,
    b.premium_change + (
        b.option_market_value - COALESCE(b.prev_option_market_value_raw, 0)
    ) AS option_pnl,
    b.futures_pnl + b.premium_change + (
        b.option_market_value - COALESCE(b.prev_option_market_value_raw, 0)
    ) AS total_pnl,

    -- 客户权益勾稽
    (
        COALESCE(b.balance_b_f, 0)
        + COALESCE(b.deposit_withdrawal, 0)
        - COALESCE(b.total_fee, 0)
        + COALESCE(b.premium_change, 0)
        + COALESCE(b.futures_pnl, 0)
    ) AS customer_equity_calc_value,
    (
        (
            COALESCE(b.balance_b_f, 0)
            + COALESCE(b.deposit_withdrawal, 0)
            - COALESCE(b.total_fee, 0)
            + COALESCE(b.premium_change, 0)
            + COALESCE(b.futures_pnl, 0)
        ) - COALESCE(b.client_equity, 0)
    ) AS customer_equity_check_diff,

    -- 市值权益勾稽
    (
        COALESCE(b.client_equity, 0)
        + (
            b.option_market_value - COALESCE(b.prev_option_market_value_raw, 0)
        )
    ) AS market_value_equity_calc_value,
    (
        (
            COALESCE(b.client_equity, 0)
            + (
                b.option_market_value - COALESCE(b.prev_option_market_value_raw, 0)
            )
        ) - COALESCE(b.market_value_equity, 0)
    ) AS market_value_equity_check_diff,

    -- 交易概览
    COALESCE(tr.transaction_count, 0) AS transaction_count,
    COALESCE(tr.transaction_lots_sum, 0) AS transaction_lots_sum,
    COALESCE(tr.transaction_turnover_sum, 0) AS transaction_turnover_sum,

    -- 行权概览
    COALESCE(es.exercise_statement_count, 0) AS exercise_statement_count,
    COALESCE(es.exercise_volume_sum, 0) AS exercise_volume_sum,
    COALESCE(es.exercise_p_l_sum, 0) AS exercise_p_l_sum,

    -- 持仓概览
    COALESCE(p.positions_count, 0) AS positions_count,
    COALESCE(p.positions_long_pos_sum, 0) AS positions_long_pos_sum,
    COALESCE(p.positions_s_pos_sum, 0) AS positions_s_pos_sum,

    -- 核验概览
    COALESCE(v.validation_total, 0) AS validation_total,
    COALESCE(v.validation_pass, 0) AS validation_pass,
    COALESCE(v.validation_warn, 0) AS validation_warn,
    COALESCE(v.validation_fail, 0) AS validation_fail

FROM base_with_prev b
LEFT JOIN transaction_record_agg tr
    ON b.source_file = tr.source_file
LEFT JOIN exercise_statement_agg es
    ON b.source_file = es.source_file
LEFT JOIN positions_agg p
    ON b.source_file = p.source_file
LEFT JOIN validation_agg v
    ON b.source_file = v.source_file
ORDER BY b.date_from, b.account_id, b.source_file;