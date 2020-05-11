CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createTable`(IN tblName varchar(50))
BEGIN
	DECLARE EXIT HANDLER FOR 1050 SELECT 'Table Already exists' Message; 
    DECLARE EXIT HANDLER FOR SQLEXCEPTION SELECT 'SQLException encountered' Message; 
    
	SET @sql_ = CONCAT('CREATE TABLE `TradingDB`.`', tblName, 
     '` ( `date` DATE NOT NULL,
	  `open` FLOAT NOT NULL,
	  `high` FLOAT NOT NULL,
	  `low` FLOAT NOT NULL,
	  `close` FLOAT NOT NULL,
	  `volume` FLOAT NOT NULL,
	  PRIMARY KEY (`date`))');
    
	PREPARE stmt1 FROM @sql_;
	EXECUTE stmt1;
    DEALLOCATE PREPARE stmt1;
    
END