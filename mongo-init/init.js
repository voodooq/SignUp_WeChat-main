/**
 * MongoDB 初始化脚本
 * 创建索引 + 插入必要的初始数据
 */

// 切换到目标数据库
db = db.getSiblingDB('sign_wechat');

print('=== 开始初始化 sign_wechat 数据库 ===');

// ========== 创建索引 ==========

// 用户表：openid 唯一索引
db.sign_users.createIndex({ openid: 1 }, { unique: true });
print('✓ sign_users 索引创建完成');

// 报名记录表
db.sign_registrations.createIndex({ openid: 1 });
db.sign_registrations.createIndex({ ticket_no: 1 }, { unique: true });
db.sign_registrations.createIndex({ id_card_hash: 1 }, { unique: true });
db.sign_registrations.createIndex({ payment_status: 1 });
db.sign_registrations.createIndex({ create_time: -1 });
print('✓ sign_registrations 索引创建完成');

// 计数器表
db.sign_counters.createIndex({ key: 1 }, { unique: true });
print('✓ sign_counters 索引创建完成');

// 成绩表：准考证号+项目名称联合唯一索引
db.sign_scores.createIndex({ ticket_no: 1, event_name: 1 }, { unique: true });
db.sign_scores.createIndex({ ticket_no: 1 });
print('✓ sign_scores 索引创建完成');

// 设置表
db.sign_settings.createIndex({ key: 1 }, { unique: true });
print('✓ sign_settings 索引创建完成');

// 学校表
db.sign_schools.createIndex({ name: 1 }, { unique: true });
print('✓ sign_schools 索引创建完成');

// 图片表
db.sign_banners.createIndex({ position: 1, sort_order: 1 });
db.sign_event_images.createIndex({ sort_order: 1 });
db.sign_notice_images.createIndex({ sort_order: 1 });
print('✓ 图片表索引创建完成');

// ========== 插入初始数据 ==========

// 必考项目（首次部署必须有）
var eventsCount = db.sign_events.countDocuments({});
if (eventsCount === 0) {
    db.sign_events.insertMany([
        {
            name: '1000米',
            fee: 0,
            code: '01',
            status: 'active',
            sort_order: 0,
            is_required: true,
            create_time: Date.now()
        },
        {
            name: '800米',
            fee: 0,
            code: '02',
            status: 'active',
            sort_order: 1,
            is_required: true,
            create_time: Date.now()
        },
        {
            name: '掷实心球',
            fee: 0,
            code: '03',
            status: 'active',
            sort_order: 2,
            is_required: false,
            create_time: Date.now()
        },
        {
            name: '立定跳远',
            fee: 0,
            code: '04',
            status: 'active',
            sort_order: 3,
            is_required: false,
            create_time: Date.now()
        },
        {
            name: '1分钟跳绳',
            fee: 0,
            code: '05',
            status: 'active',
            sort_order: 4,
            is_required: false,
            create_time: Date.now()
        },
        {
            name: '坐位体前屈',
            fee: 0,
            code: '06',
            status: 'active',
            sort_order: 5,
            is_required: false,
            create_time: Date.now()
        }
    ]);
    print('✓ 初始赛事项目数据插入完成');
} else {
    print('- 赛事项目数据已存在，跳过插入');
}

// 默认设置
var settingsCount = db.sign_settings.countDocuments({});
if (settingsCount === 0) {
    db.sign_settings.insertMany([
        { key: 'event_title', value: '体育中考', created_at: Date.now(), updated_at: Date.now() },
        { key: 'event_location', value: '比赛场馆', created_at: Date.now(), updated_at: Date.now() },
        { key: 'event_date', value: '', created_at: Date.now(), updated_at: Date.now() },
        { key: 'registration_deadline', value: '', created_at: Date.now(), updated_at: Date.now() },
    ]);
    print('✓ 初始设置数据插入完成');
} else {
    print('- 设置数据已存在，跳过插入');
}

print('=== 数据库初始化完成 ===');
