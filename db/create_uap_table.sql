-- テーブル: tbl_group
CREATE TABLE tbl_group (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL
);

-- テーブル: tbl_user
CREATE TABLE tbl_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    group_id INT,
    FOREIGN KEY (group_id) REFERENCES tbl_group(group_id)
);

-- テーブル: tbl_fit
CREATE TABLE tbl_fit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    datetime DATETIME NOT NULL,
    steps INT,
    distance FLOAT,
    weight FLOAT,
    fat FLOAT,
    FOREIGN KEY (user_id) REFERENCES tbl_user(user_id),
    UNIQUE (user_id, datetime)
);

-- インデックスの追加 (オプション)
CREATE INDEX idx_user_datetime ON tbl_fit (user_id, datetime);

