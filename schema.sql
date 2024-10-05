PRAGMA FOREIGN_KEYS = ON;
PRAGMA JOURNAL_MODE = WAL;
PRAGMA SYNCHRONOUS = 1;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS `USERS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `EMAIL`     VARCHAR(255)    UNIQUE          NOT NULL,
    `PASSWORD`  CHAR(64)        NOT NULL,
    `NAME`      VARCHAR(255)    NOT NULL,
    `ROLE`      CHAR(5)         DEFAULT        'USER',
    `ADDRESS`   TEXT            NOT NULL,
    `PHONE`     CHAR(10)        NOT NULL,

    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `PRODUCTS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `UNIQUE_ID` VARCHAR(16)     NOT NULL,
    `NAME`      VARCHAR(255)    NOT NULL,
    `PRICE`     DECIMAL(10, 2)  NOT NULL,
    `DISPLAY_PRICE` DECIMAL(10, 2),
    `DESCRIPTION` TEXT          NOT NULL,
    `STOCK`     INTEGER         DEFAULT         -1,
    `SIZE`      TEXT            DEFAULT         NULL,
    `CATEGORY`  INTEGER         NOT NULL,
    `KEYWORDS`  TEXT            DEFAULT         "",

    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

    FOREIGN KEY (`CATEGORY`)    REFERENCES `CATEGORIES`(`ID`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `CARTS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `USER_ID`   INTEGER         NOT NULL,
    `PRODUCT_ID` INTEGER        NOT NULL,
    `QUANTITY`  INTEGER         NOT NULL,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
    FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE,

    CONSTRAINT `UNIQUE_CART`    UNIQUE (`USER_ID`, `PRODUCT_ID`)
);

CREATE TABLE IF NOT EXISTS `ORDERS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `USER_ID`   INTEGER         NOT NULL,
    `PRODUCT_ID` INTEGER        NOT NULL,
    `QUANTITY`  INTEGER         NOT NULL,
    `TOTAL_PRICE` DECIMAL(10, 2) NOT NULL,
    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,
    `STATUS`    CHAR(4)         DEFAULT         'PEND',
    `RAZORPAY_ORDER_ID` TEXT    DEFAULT         NULL,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
    FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `REVIEWS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `USER_ID`   INTEGER         NOT NULL,
    `PRODUCT_ID` INTEGER        NOT NULL,
    `STARS`     INTEGER         NOT NULL,
    `REVIEW`    VARCHAR(255)    NOT NULL,
    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
    FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `FAVOURITES` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `USER_ID`   INTEGER         NOT NULL,
    `PRODUCT_UNIQUE_ID` VARCHAR(16)        NOT NULL,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,

    CONSTRAINT `UNIQUE_FAVORITE` UNIQUE (`USER_ID`, `PRODUCT_UNIQUE_ID`) ON CONFLICT REPLACE
);

CREATE TABLE IF NOT EXISTS `GIFT_CARDS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `PRICE`     INTEGER         NOT NULL,
    `USER_ID`   INTEGER         NOT NULL,
    `CODE`      TEXT            NOT NULL,
    `USED`      BOOLEAN         DEFAULT         0,
    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,
    `USED_AT`   TIMESTAMP       DEFAULT         NULL,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,

    CONSTRAINT `UNIQUE_CODES`   UNIQUE (`CODE`)
);

CREATE TABLE IF NOT EXISTS `LOGS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `MESSAGE`   TEXT            NOT NULL,
    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,
    `LEVEL`     CHAR(5)         DEFAULT         'INFO',
    `NAME`      TEXT            DEFAULT         NULL
);

CREATE TABLE IF NOT EXISTS `CATEGORIES` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `NAME`      TEXT            UNIQUE          NOT NULL,
    `DESCRIPTION` TEXT          NOT NULL
);

CREATE TABLE IF NOT EXISTS `CAROUSEL` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `IMAGE`     TEXT            NOT NULL,
    `HEADING`   TEXT            NOT NULL,
    `DESCRIPTION` TEXT          NOT NULL
);

CREATE TABLE IF NOT EXISTS `NEWSLETTERS` (
    ID          INTEGER         PRIMARY KEY     AUTOINCREMENT,
    EMAIL       TEXT            DEFAULT         "",

    CONSTRAINT `UNIQUE_EMAIL`    UNIQUE (`EMAIL`)
);

CREATE TABLE IF NOT EXISTS `TICKETS` (
    `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
    `REPLIED_TO` INTEGER        DEFAULT         NULL,
    `USER_ID`   INTEGER         NOT NULL,
    `SUBJECT`   TEXT            NOT NULL,
    `MESSAGE`   TEXT            NOT NULL,
    -- OPEN, PROC, CLOS
    `STATUS`    CHAR(4)         DEFAULT         'OPEN',
    `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

    FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
    FOREIGN KEY (`REPLIED_TO`)  REFERENCES `TICKETS`(`ID`)  ON DELETE CASCADE
);

COMMIT;
