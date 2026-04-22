PRAGMA foreign_keys = OFF;

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
    deposit_withdrawal REAL,
    realized_p_l REAL,
    mtm_p_l REAL,
    exercise_p_l REAL,
    commission REAL,
    exercise_fee REAL,
    delivery_fee REAL,
    new_fx_pledge REAL,
    fx_redemption REAL,
    chg_in_pledge_amt REAL,
    premium_received REAL,
    premium_paid REAL,
    delivery_p_l REAL,

    initial_margin REAL,
    balance_c_f REAL,
    pledge_amount REAL,
    client_equity REAL,
    fx_pledge_occ REAL,
    margin_occupied REAL,
    delivery_margin REAL,
    market_value_long REAL,
    market_value_short REAL,
    market_value_equity REAL,
    fund_avail REAL,
    risk_degree REAL,
    margin_call REAL,
    chg_in_fx_pledge REAL,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_summary_source_file
ON account_summary(source_file);

CREATE INDEX IF NOT EXISTS idx_account_summary_date_from
ON account_summary(date_from);


CREATE TABLE IF NOT EXISTS deposit_withdrawal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    deposit REAL,
    withdrawal REAL,
    exchange_rate REAL,
    account_id TEXT,
    note TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deposit_withdrawal_source_file
ON deposit_withdrawal(source_file);

CREATE INDEX IF NOT EXISTS idx_deposit_withdrawal_date
ON deposit_withdrawal(date);


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
    premium_received_paid REAL,
    trans_no TEXT,
    account_id TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transaction_record_source_file
ON transaction_record(source_file);

CREATE INDEX IF NOT EXISTS idx_transaction_record_date
ON transaction_record(date);

CREATE INDEX IF NOT EXISTS idx_transaction_record_instrument
ON transaction_record(instrument);


CREATE TABLE IF NOT EXISTS exercise_statement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    invest_unit TEXT,
    exchange TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    b_s TEXT,
    strike_price REAL,
    exercise_price REAL,
    lots REAL,
    turnover REAL,
    exercise_p_l REAL,
    exercise_fee REAL,
    account_id TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exercise_statement_source_file
ON exercise_statement(source_file);

CREATE INDEX IF NOT EXISTS idx_exercise_statement_date
ON exercise_statement(date);


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
    account_id TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_position_closed_source_file
ON position_closed(source_file);

CREATE INDEX IF NOT EXISTS idx_position_closed_close_date
ON position_closed(close_date);

CREATE INDEX IF NOT EXISTS idx_position_closed_instrument
ON position_closed(instrument);


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
    position_qty REAL,
    pos_open_price REAL,
    prev_sttl REAL,
    settlement_price REAL,
    accum_p_l REAL,
    mtm_p_l REAL,
    margin REAL,
    market_value REAL,
    account_id TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_positions_detail_source_file
ON positions_detail(source_file);

CREATE INDEX IF NOT EXISTS idx_positions_detail_instrument
ON positions_detail(instrument);

CREATE INDEX IF NOT EXISTS idx_positions_detail_open_date
ON positions_detail(open_date);


CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invest_unit TEXT,
    trading_code TEXT,
    product TEXT,
    instrument TEXT,
    long_pos REAL,
    avg_buy_price REAL,
    short_pos REAL,
    avg_sell_price REAL,
    prev_sttl REAL,
    sttl_today REAL,
    mtm_p_l REAL,
    margin_occupied REAL,
    s_h TEXT,
    market_value_long REAL,
    market_value_short REAL,
    account_id TEXT,

    source_file TEXT NOT NULL,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_positions_source_file
ON positions(source_file);

CREATE INDEX IF NOT EXISTS idx_positions_instrument
ON positions(instrument);


CREATE TABLE IF NOT EXISTS validation_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL,
    actual_value REAL,
    expected_value REAL,
    diff_value REAL,
    tolerance REAL,
    details TEXT,
    source_file TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validation_result_source_file
ON validation_result(source_file);

CREATE INDEX IF NOT EXISTS idx_validation_result_status
ON validation_result(status);

CREATE TABLE IF NOT EXISTS source_file_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    file_md5 TEXT NOT NULL UNIQUE,
    parser_name TEXT,
    process_status TEXT NOT NULL DEFAULT 'SUCCESS',
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_source_file_record_source_file
ON source_file_record(source_file);