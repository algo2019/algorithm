DECLARE @YM CHAR(6);
DECLARE @delete_database int;
DECLARE @delete_table int;

SET @YM= '201608';
SET @delete_database = 0
SET @delete_table = 0

DECLARE @myDataBase  NVARCHAR(50);
SET @myDataBase = 'GTA_MFL1_TRDMIN_' + @YM;

DECLARE @SQL  NVARCHAR(1000);
DECLARE @USESQL  NVARCHAR(100);
IF (@delete_database = 1)
BEGIN
	SET @SQL = 'DROP DATABASE ' + @myDataBase;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = 'CREATE DATABASE ' + @myDataBase;
PRINT @SQL;
EXECUTE sp_executesql @SQL;

SET @USESQL = 'USE ' + @myDataBase + ';';

DECLARE @HEAD NVARCHAR(50);
DECLARE @TAIL NVARCHAR(500);
SET @HEAD='create table ';
SET @TAIL=' (CONTRACTID	nvarchar(8)	,
	TDATETIME	datetime	,
	OPENPX	decimal(9, 3)	,
	HIGHPX	decimal(9, 3)	,
	LOWPX	decimal(9, 3)	,
	LASTPX	decimal(9, 3)	,
	MINQTY	decimal(10, 0)	,
	TURNOVER	decimal(20, 3)	,
	OPENINTS	decimal(8, 0)	,
	CHGMIN	decimal(9, 2)	,
	CHGPCTMIN	decimal(6, 3)	,
	VARIETIES	nvarchar(8)	,
	MFLXID	nvarchar(8)	,
	MARKET	nvarchar(4)	,
	UNIX	bigint	,
	primary key (CONTRACTID,TDATETIME)
	)';
DECLARE @tableName  NVARCHAR(100);
DECLARE @preTable NVARCHAR(50);
SET @preTable = 'MFL1_TRDMIN';
SET @tableName = @preTable + '01_' + @YM;


IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;

SET @tableName = @preTable + '05_' + @YM;

IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;

SET @tableName = @preTable + '10_' + @YM;

IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;

SET @tableName = @preTable + '15_' + @YM;

IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;

SET @tableName = @preTable + '30_' + @YM;

IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;

SET @tableName = @preTable + '60_' + @YM;

IF (@delete_database = 1)
BEGIN
	SET @SQL = @USESQL + 'DROP TABLE ' + @tableName;
	PRINT @SQL;
	EXECUTE sp_executesql @SQL;
END

SET @SQL = @USESQL + @HEAD + @tableName + @TAIL;
PRINT @tableName;
EXECUTE sp_executesql @SQL;
