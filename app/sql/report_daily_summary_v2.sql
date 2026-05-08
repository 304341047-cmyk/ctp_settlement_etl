WITH latest_date AS (
    SELECT MAX(date_from) AS date_from
    FROM account_summary
),

latest_account AS (
    SELECT
        a.*
    FROM account_summary a
    JOIN latest_date ld
        ON a.date_from = ld.date_from
),

prev_account AS (
    SELECT
        pa.*
    FROM account_summary pa
    JOIN (
        SELECT
            la.account_id,
            MAX(pa2.date_from) AS prev_date_from
        FROM latest_account la
        LEFT JOIN account_summary pa2
            ON COALESCE(pa2.account_id, '') = COALESCE(la.account_id, '')
           AND pa2.date_from < la.date_from
        GROUP BY la.account_id
    ) p
        ON COALESCE(pa.account_id, '') = COALESCE(p.account_id, '')
       AND pa.date_from = p.prev_date_from
),

txn AS (
    SELECT
        account_id,
        source_file,
        date,
        COUNT(*) AS trade_count,
        COALESCE(SUM(lots), 0) AS trade_lots,
        COALESCE(SUM(turnover), 0) AS turnover,
        COALESCE(SUM(fee), 0) AS txn_fee,
        COALESCE(SUM(realized_p_l), 0) AS txn_realized_p_l,
        COALESCE(SUM(premium_received_paid), 0) AS premium_change
    FROM transaction_record
    WHERE date = (SELECT date_from FROM latest_date)
    GROUP BY account_id, source_file, date
),

pos_detail AS (
    SELECT
        account_id,
        source_file,
        COUNT(*) AS position_detail_count,
        COALESCE(SUM(CASE WHEN TRIM(b_s) IN ('买', 'Buy', 'B') THEN position_qty ELSE 0 END), 0) AS long_position_qty,
        COALESCE(SUM(CASE WHEN TRIM(b_s) IN ('卖', 'Sell', 'S') THEN position_qty ELSE 0 END), 0) AS short_position_qty
    FROM positions_detail
    GROUP BY account_id, source_file
),

pos AS (
    SELECT
        account_id,
        source_file,
        COUNT(*) AS position_count,
        COALESCE(SUM(long_pos), 0) AS long_pos_total,
        COALESCE(SUM(short_pos), 0) AS short_pos_total,
        COALESCE(SUM(market_value_long), 0) AS market_value_long_total,
        COALESCE(SUM(market_value_short), 0) AS market_value_short_total,
        COALESCE(SUM(mtm_p_l), 0) AS total_mtm_p_l,
        COALESCE(SUM(margin_occupied), 0) AS total_margin_occupied
    FROM positions
    GROUP BY account_id, source_file
),

closed AS (
    SELECT
        account_id,
        source_file,
        close_date,
        COUNT(*) AS close_count,
        COALESCE(SUM(lots), 0) AS close_lots,
        COALESCE(SUM(realized_p_l), 0) AS close_realized_p_l,
        COALESCE(SUM(premium_received_paid), 0) AS close_premium_change
    FROM position_closed
    WHERE close_date = (SELECT date_from FROM latest_date)
    GROUP BY account_id, source_file, close_date
),

exercise AS (
    SELECT
        account_id,
        source_file,
        date,
        COUNT(*) AS exercise_count,
        COALESCE(SUM(lots), 0) AS exercise_lots,
        COALESCE(SUM(exercise_p_l), 0) AS exercise_p_l_total,
        COALESCE(SUM(exercise_fee), 0) AS exercise_fee_total
    FROM exercise_statement
    WHERE date = (SELECT date_from FROM latest_date)
    GROUP BY account_id, source_file, date
),

validation AS (
    SELECT
        source_file,
        COUNT(*) AS validation_total,
        COALESCE(SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END), 0) AS validation_pass,
        COALESCE(SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END), 0) AS validation_warn,
        COALESCE(SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END), 0) AS validation_fail
    FROM validation_result
    GROUP BY source_file
),

base AS (
    SELECT
        la.source_file,
        la.date_from,
        la.client_id,
        la.client_name,
        la.account_id,

        la.balance_b_f,
        la.balance_c_f,
        la.deposit_withdrawal,
        la.client_equity,
        la.market_value_equity,
        la.margin_occupied,
        la.fund_avail,
        la.risk_degree,

        la.realized_p_l,
        la.mtm_p_l,
        la.exercise_p_l,
        la.commission,
        la.exercise_fee,
        la.delivery_fee,
        la.premium_received,
        la.premium_paid,
        la.delivery_p_l,

        COALESCE(la.market_value_long, 0) AS market_value_long,
        COALESCE(la.market_value_short, 0) AS market_value_short,
        COALESCE(pa.market_value_long, 0) + COALESCE(pa.market_value_short, 0) AS prev_option_market_value,

        COALESCE(txn.trade_count, 0) AS trade_count,
        COALESCE(txn.trade_lots, 0) AS trade_lots,
        COALESCE(txn.turnover, 0) AS turnover,
        COALESCE(txn.premium_change, 0) AS premium_change,

        COALESCE(pos_detail.position_detail_count, 0) AS position_detail_count,
        COALESCE(pos_detail.long_position_qty, 0) AS long_position_qty,
        COALESCE(pos_detail.short_position_qty, 0) AS short_position_qty,

        COALESCE(pos.position_count, 0) AS position_count,
        COALESCE(pos.long_pos_total, 0) AS long_pos_total,
        COALESCE(pos.short_pos_total, 0) AS short_pos_total,
        COALESCE(pos.market_value_long_total, 0) AS market_value_long_total,
        COALESCE(pos.market_value_short_total, 0) AS market_value_short_total,

        COALESCE(closed.close_count, 0) AS close_count,
        COALESCE(closed.close_lots, 0) AS close_lots,
        COALESCE(closed.close_realized_p_l, 0) AS close_realized_p_l,
        COALESCE(closed.close_premium_change, 0) AS close_premium_change,

        COALESCE(exercise.exercise_count, 0) AS exercise_count,
        COALESCE(exercise.exercise_lots, 0) AS exercise_lots,
        COALESCE(exercise.exercise_p_l_total, 0) AS exercise_p_l_total,
        COALESCE(exercise.exercise_fee_total, 0) AS exercise_fee_total,

        COALESCE(validation.validation_total, 0) AS validation_total,
        COALESCE(validation.validation_pass, 0) AS validation_pass,
        COALESCE(validation.validation_warn, 0) AS validation_warn,
        COALESCE(validation.validation_fail, 0) AS validation_fail

    FROM latest_account la
    LEFT JOIN prev_account pa
        ON COALESCE(pa.account_id, '') = COALESCE(la.account_id, '')
    LEFT JOIN txn
        ON txn.source_file = la.source_file
       AND txn.date = la.date_from
       AND (
            COALESCE(txn.account_id, '') = COALESCE(la.account_id, '')
            OR COALESCE(txn.account_id, '') = ''
       )
    LEFT JOIN pos_detail
        ON pos_detail.source_file = la.source_file
       AND (
            COALESCE(pos_detail.account_id, '') = COALESCE(la.account_id, '')
            OR COALESCE(pos_detail.account_id, '') = ''
       )
    LEFT JOIN pos
        ON pos.source_file = la.source_file
       AND (
            COALESCE(pos.account_id, '') = COALESCE(la.account_id, '')
            OR COALESCE(pos.account_id, '') = ''
       )
    LEFT JOIN closed
        ON closed.source_file = la.source_file
       AND closed.close_date = la.date_from
       AND (
            COALESCE(closed.account_id, '') = COALESCE(la.account_id, '')
            OR COALESCE(closed.account_id, '') = ''
       )
    LEFT JOIN exercise
        ON exercise.source_file = la.source_file
       AND exercise.date = la.date_from
       AND (
            COALESCE(exercise.account_id, '') = COALESCE(la.account_id, '')
            OR COALESCE(exercise.account_id, '') = ''
       )
    LEFT JOIN validation
        ON validation.source_file = la.source_file
)

SELECT
    source_file,
    date_from,
    client_id,
    client_name,
    account_id,

    balance_b_f,
    balance_c_f,
    deposit_withdrawal,
    client_equity,
    market_value_equity,
    margin_occupied,
    fund_avail,
    risk_degree,

    trade_count,
    trade_lots,
    turnover,

    position_count,
    position_detail_count,
    long_position_qty,
    short_position_qty,
    long_pos_total,
    short_pos_total,
    market_value_long_total,
    market_value_short_total,

    close_count,
    close_lots,
    close_realized_p_l,
    close_premium_change,

    exercise_count,
    exercise_lots,
    exercise_p_l_total,
    exercise_fee_total,

    premium_change,

    COALESCE(commission, 0)
      + COALESCE(exercise_fee, 0)
      + COALESCE(delivery_fee, 0) AS total_fee,

    COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0) AS option_market_value,

    prev_option_market_value,

    (COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0))
      - COALESCE(prev_option_market_value, 0) AS option_market_value_change,

    COALESCE(premium_change, 0)
      + (
          (COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0))
          - COALESCE(prev_option_market_value, 0)
        ) AS option_pnl,

    COALESCE(realized_p_l, 0)
      + COALESCE(mtm_p_l, 0)
      + COALESCE(delivery_p_l, 0) AS futures_pnl,

    COALESCE(realized_p_l, 0)
      + COALESCE(mtm_p_l, 0)
      + COALESCE(delivery_p_l, 0)
      + COALESCE(premium_change, 0)
      + (
          (COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0))
          - COALESCE(prev_option_market_value, 0)
        ) AS pnl,

    (
      COALESCE(realized_p_l, 0)
      + COALESCE(mtm_p_l, 0)
      + COALESCE(delivery_p_l, 0)
      + COALESCE(premium_change, 0)
      + (
          (COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0))
          - COALESCE(prev_option_market_value, 0)
        )
    )
    - (
      COALESCE(commission, 0)
      + COALESCE(exercise_fee, 0)
      + COALESCE(delivery_fee, 0)
    ) AS total_pnl,

    balance_b_f
      + COALESCE(deposit_withdrawal, 0)
      + (
          COALESCE(realized_p_l, 0)
          + COALESCE(mtm_p_l, 0)
          + COALESCE(delivery_p_l, 0)
        )
      + COALESCE(premium_change, 0)
      - (
          COALESCE(commission, 0)
          + COALESCE(exercise_fee, 0)
          + COALESCE(delivery_fee, 0)
        ) AS customer_equity_calc_value,

    (
      balance_b_f
      + COALESCE(deposit_withdrawal, 0)
      + (
          COALESCE(realized_p_l, 0)
          + COALESCE(mtm_p_l, 0)
          + COALESCE(delivery_p_l, 0)
        )
      + COALESCE(premium_change, 0)
      - (
          COALESCE(commission, 0)
          + COALESCE(exercise_fee, 0)
          + COALESCE(delivery_fee, 0)
        )
    ) - COALESCE(client_equity, 0) AS customer_equity_check_diff,

    COALESCE(client_equity, 0)
      + (COALESCE(market_value_long, 0) + COALESCE(market_value_short, 0))
      - COALESCE(prev_option_market_value, 0) AS market_value_equity_calc_value,

    (
      COALESCE(client_equity, 0)
      + (COALESCE(market_value_long, 0) - COALESCE(market_value_short, 0))
    ) - COALESCE(market_value_equity, 0) AS market_value_equity_check_diff,

    validation_total,
    validation_pass,
    validation_warn,
    validation_fail

FROM base
ORDER BY account_id, source_file;
