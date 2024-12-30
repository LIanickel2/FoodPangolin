-- 更新訂單表的狀態字段，添加已拒絕狀態
ALTER TABLE orders MODIFY COLUMN status ENUM(
    '待確認',   -- 客戶剛下單
    '待接單',   -- 餐廳已確認，等待外送員接單
    '配送中',   -- 外送員已接單，正在配送
    '已送達',   -- 外送員已送達
    '已完成',   -- 顧客已確認收貨
    '已拒絕'    -- 餐廳拒絕訂單
) NOT NULL DEFAULT '待確認';
