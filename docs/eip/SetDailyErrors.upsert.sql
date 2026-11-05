/* SetDailyErrors 要做的事（給 EIP 端寫 API 參考；測試區驗證用的也是這一段）。
   收到一包：一站一天一個包裝方式。errors 是那天這個包裝方式所有出過錯的步驟；空陣列＝那天沒出錯。
   做法：同一把鍵（日期＋產線＋站別＋包裝方式）底下，不在這包裡的步驟刪掉，在的照覆蓋鍵更新或新增。同一包重送結果一樣。
   範例：
   {"recordDate": "2026-11-04", "factoryCode": "BYI", "departmentID": 1493, "station": "PACK01",
    "methodName": "310222 01_歐洲", "errors": [{"name": "盒端貼紙", "missed": 4, "timeout": 1}]} */
DECLARE @j nvarchar(max) = $(PAYLOAD);

DECLARE @d   date          = JSON_VALUE(@j, '$.recordDate'),
        @f   nvarchar(5)   = JSON_VALUE(@j, '$.factoryCode'),
        @dep int           = JSON_VALUE(@j, '$.departmentID'),
        @st  nvarchar(50)  = JSON_VALUE(@j, '$.station'),
        @m   nvarchar(100) = JSON_VALUE(@j, '$.methodName');

IF @d IS NULL OR @f IS NULL OR @dep IS NULL OR @st IS NULL OR @m IS NULL
    THROW 50001, N'recordDate、factoryCode、departmentID、station、methodName 都要有', 1;

SET XACT_ABORT ON;
BEGIN TRAN;

DELETE e
FROM mes.PackingGuardDailyErrors e
WHERE e.RecordDate = @d AND e.DepartmentID = @dep AND e.Station = @st AND e.MethodName = @m
  AND e.StepName NOT IN (SELECT x.name FROM OPENJSON(@j, '$.errors') WITH (name nvarchar(100) '$.name') x);

MERGE mes.PackingGuardDailyErrors AS t
USING (SELECT name, ISNULL(missed, 0) AS missed, ISNULL(timeout, 0) AS timeout
       FROM OPENJSON(@j, '$.errors') WITH (name nvarchar(100) '$.name', missed int '$.missed', timeout int '$.timeout')
       WHERE ISNULL(missed, 0) > 0 OR ISNULL(timeout, 0) > 0) AS s
   ON t.RecordDate = @d AND t.DepartmentID = @dep AND t.Station = @st AND t.MethodName = @m AND t.StepName = s.name
WHEN MATCHED THEN
    UPDATE SET MissedCount = s.missed, TimeoutCount = s.timeout, FactoryCode = @f, UpdatedAt = GETUTCDATE()
WHEN NOT MATCHED THEN
    INSERT (RecordDate, FactoryCode, DepartmentID, Station, MethodName, StepName, MissedCount, TimeoutCount, UpdatedAt)
    VALUES (@d, @f, @dep, @st, @m, s.name, s.missed, s.timeout, GETUTCDATE());

COMMIT;
