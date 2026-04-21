WITH transaction_record_agg AS (
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
        COALESCE(SUM(amount_exercised), 0) AS exercise_amount_sum,
        COALESCE(SUM(exercise_p_l), 0) AS exercise_p_l_sum,
        COALESCE(SUM(exercise_fee), 0) AS exercise_fee_sum
    FROM exercise_statement
    GROUP BY source_file
),
positions_agg AS (
    SELECT
        source_file,
        COUNT(*) AS positions_count,
        COALESCE(SUM(long_pos), 0) AS positions_long_pos_sum,
        COALESCE(SUM(s_pos), 0) AS positions_s_pos_sum,
        COALESCE(SUM(mtm_p_l), 0) AS positions_mtm_p_l_sum,
        COALESCE(SUM(margin_occupied), 0) AS positions_margin_occupied_sum,
        COALESCE(SUM(market_value_long), 0) AS positions_market_value_long_sum,
        COALESCE(SUM(market_value_short), 0) AS positions_market_value_short_sum
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
    a.source_file,
    a.creation_date,
    a.date_from,
    a.date_to,
    a.client_id,
    a.client_name,
    a.account_id,
    a.currency,

    -- 资金概览
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
    a.premium_received,
    a.premium_paid,
    a.fund_avail,
    a.margin_occupied,
    a.risk_degree,

    -- 交易概览
    COALESCE(tr.transaction_count, 0) AS transaction_count,
    COALESCE(tr.transaction_lots_sum, 0) AS transaction_lots_sum,
    COALESCE(tr.transaction_turnover_sum, 0) AS transaction_turnover_sum,

    -- 行权概览
    COALESCE(es.exercise_statement_count, 0) AS exercise_statement_count,
    COALESCE(es.exercise_volume_sum, 0) AS exercise_volume_sum,
    COALESCE(es.exercise_amount_sum, 0) AS exercise_amount_sum,
    COALESCE(es.exercise_p_l_sum, 0) AS exercise_p_l_sum,
    COALESCE(es.exercise_fee_sum, 0) AS exercise_fee_sum,

    -- 持仓概览
    COALESCE(p.positions_count, 0) AS positions_count,
    COALESCE(p.positions_long_pos_sum, 0) AS positions_long_pos_sum,
    COALESCE(p.positions_s_pos_sum, 0) AS positions_s_pos_sum,
    COALESCE(p.positions_mtm_p_l_sum, 0) AS positions_mtm_p_l_sum,
    COALESCE(p.positions_margin_occupied_sum, 0) AS positions_margin_occupied_sum,
    COALESCE(p.positions_market_value_long_sum, 0) AS positions_market_value_long_sum,
    COALESCE(p.positions_market_value_short_sum, 0) AS positions_market_value_short_sum,

    -- 核验概览
    COALESCE(v.validation_total, 0) AS validation_total,
    COALESCE(v.validation_pass, 0) AS validation_pass,
    COALESCE(v.validation_warn, 0) AS validation_warn,
    COALESCE(v.validation_fail, 0) AS validation_fail

FROM account_summary a
LEFT JOIN transaction_record_agg tr
    ON a.source_file = tr.source_file
LEFT JOIN exercise_statement_agg es
    ON a.source_file = es.source_file
LEFT JOIN positions_agg p
    ON a.source_file = p.source_file
LEFT JOIN validation_agg v
    ON a.source_file = v.source_file
ORDER BY a.date_from, a.account_id, a.source_file;