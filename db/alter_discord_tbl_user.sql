ALTER TABLE tbl_user
ADD COLUMN discord_user_id BIGINT NOT NULL DEFAULT 0;

ALTER TABLE tbl_user
ADD COLUMN discord_roles JSON;