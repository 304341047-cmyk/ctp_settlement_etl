PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_file_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    file_md5 TEXT NOT NULL UNIQUE,
    parser_name TEXT,
    process_status TEXT NOT NULL DEFAULT 'SUCCESS',
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Account Summary
CREATE TABLE IF NOT EXISTS account_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    creation_date TEXT,
    date_from TEXT,
    date_to TEXT,

    client_id TEXT,
    client_name TEXT,
    account_id TEXT,
    currency TEXT,

    balance_b_f REAL,
    balance_c_f REAL,
    deposit_withdrawal REAL,
    initial_margin REAL,
    realized_p_l REAL,
    mtm_p_l REAL,
    market_value_equity REAL,
    client_equity REAL,
    exercise_p_l REAL,
    fx_pledge_occ REAL,
    commission REAL,
    exercise_fee REAL,
    margin_occupied REAL,
    delivery_margin REAL,
    market_value_short REAL,
    market_value_long REAL,
    new_fx_pledge REAL,
    fx_redemption REAL,
    delivery_fee REAL,
    pledge_amount REAL,
    chg_in_pledge_amt REAL,
    fund_avail REAL,
    premium_received REAL,
    premium_paid REAL,
    risk_degree REAL,
    margin_call REAL,
    delivery_p_l REAL,
    chg_in_fx_pledge REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Record
CREATE TABLE IF NOT EXISTS transaction_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    date TEXT,
    invest_unit TEXT,
    exchange TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    b_s TEXT,
    s_h TEXT,
    price REAL,
    lots REAL,
    turnover REAL,
    o_c TEXT,
    fee REAL,
    realized_p_l REAL,
    premium_r_p REAL,
    trans_no TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Exercise Statement
CREATE TABLE IF NOT EXISTS exercise_statement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    date TEXT,
    invest_unit TEXT,
    exchange TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    s_h TEXT,
    b_s TEXT,
    exercise_abandon TEXT,
    volume_exercised REAL,
    ex_price REAL,
    amount_exercised REAL,
    exercise_p_l REAL,
    exercise_fee REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Position Closed
CREATE TABLE IF NOT EXISTS position_closed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    close_date TEXT,
    invest_unit TEXT,
    exchange TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    open_date TEXT,
    s_h TEXT,
    b_s TEXT,
    lots REAL,
    pos_open_price REAL,
    prev_sttl REAL,
    trans_price REAL,
    realized_p_l REAL,
    premium_received_paid REAL,
    premium_netting REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Positions Detail
CREATE TABLE IF NOT EXISTS positions_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    invest_unit TEXT,
    exchange TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    open_date TEXT,
    s_h TEXT,
    b_s TEXT,
    positon REAL,
    open_price REAL,
    prev_sttl REAL,
    sttl_today REAL,
    accum_p_l REAL,
    mtm_p_l REAL,
    margin REAL,
    market_val REAL,
    market_val_chg REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Positions
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    invest_unit TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    long_pos REAL,
    avg_buy_price REAL,
    s_pos REAL,
    avg_sell_price REAL,
    prev_sttl REAL,
    sttl_today REAL,
    mtm_p_l REAL,
    margin_occupied REAL,
    s_h TEXT,
    market_value_long REAL,
    market_value_short REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS validation_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    rule_code TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    status TEXT NOT NULL,             -- PASS / WARN / FAIL
    actual_value TEXT,
    expected_value TEXT,
    diff_value REAL,
    message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validation_result_source_file
ON validation_result(source_file);

CREATE INDEX IF NOT EXISTS idx_source_file_record_md5
ON source_file_record(file_md5);

CREATE INDEX IF NOT EXISTS idx_account_summary_source_file
ON account_summary(source_file);

CREATE INDEX IF NOT EXISTS idx_transaction_record_source_file
ON transaction_record(source_file);

CREATE INDEX IF NOT EXISTS idx_exercise_statement_source_file
ON exercise_statement(source_file);

CREATE INDEX IF NOT EXISTS idx_position_closed_source_file
ON position_closed(source_file);

CREATE INDEX IF NOT EXISTS idx_positions_detail_source_file
ON positions_detail(source_file);

CREATE INDEX IF NOT EXISTS idx_positions_source_file
ON positions(source_file);

CREATE INDEX IF NOT EXISTS idx_validation_result_source_file
ON validation_result(source_file);