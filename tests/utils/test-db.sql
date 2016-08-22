CREATE TABLE result (
  id          INT(12) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  transaction VARCHAR(100) NOT NULL,
  request     VARCHAR(100) NOT NULL,
  start_time  TIMESTAMP(6) NOT NULL,
  latency     FLOAT        NOT NULL,
  http_code   INT          NOT NULL
);

