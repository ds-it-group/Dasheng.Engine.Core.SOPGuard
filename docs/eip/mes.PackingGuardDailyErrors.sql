/* SOP-Guard 當天統計：每天的錯誤原因和次數（EIP 端開卡用）
   2026-11-05 使用者定案：只有一張表；時間欄一律 UTC；RecordDate 是產線電腦的當地日期（date，00:00 換天，不分班別；使用者裁示 11-05）。
   一列＝一站（電腦）一天一個包裝方式一個錯誤原因（步驟）。次數都是 0 的步驟不存。
   上傳 API：POST /api/MES/PackingGuard/SetDailyErrors，內容見 upsert 那支腳本開頭的範例。 */

CREATE TABLE mes.PackingGuardDailyErrors (
    RecordID      int IDENTITY(1,1) NOT NULL CONSTRAINT PK_PackingGuardDailyErrors PRIMARY KEY,
    RecordDate    date          NOT NULL,                       -- 產線電腦的當地日期（00:00 換天，不分班別）
    FactoryCode   nvarchar(5)   NOT NULL,                       -- 跟 mes.DashboardRecords 一樣
    DepartmentID  int           NOT NULL,                       -- EIP 產線（部門檔）
    Station       nvarchar(50)  NOT NULL,                       -- 站別＝電腦名稱
    MethodName    nvarchar(100) NOT NULL,                       -- 包裝方式整個名字，例如 310222 01_歐洲（底線前是型體、後是地區）
    StepName      nvarchar(100) NOT NULL,                       -- 錯誤原因＝哪一步
    MissedCount   int           NOT NULL CONSTRAINT DF_PackingGuardDailyErrors_Missed  DEFAULT (0),   -- 漏做次數
    TimeoutCount  int           NOT NULL CONSTRAINT DF_PackingGuardDailyErrors_Timeout DEFAULT (0),   -- 超時次數
    UpdatedAt     datetime      NOT NULL CONSTRAINT DF_PackingGuardDailyErrors_Updated DEFAULT (GETUTCDATE())  -- 最後一次收到上傳（UTC）
);

-- 覆蓋鍵：同一天同一站同一個包裝方式同一步驟只有一列，重送就更新，不會疊加
CREATE UNIQUE INDEX UX_PackingGuardDailyErrors_Key
    ON mes.PackingGuardDailyErrors (RecordDate, DepartmentID, Station, MethodName, StepName);

-- 依日期區間排名用
CREATE INDEX IX_PackingGuardDailyErrors_RecordDate
    ON mes.PackingGuardDailyErrors (RecordDate)
    INCLUDE (FactoryCode, DepartmentID, Station, MethodName, StepName, MissedCount, TimeoutCount);
