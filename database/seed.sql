-- 图书管理系统测试数据
USE library_management;

-- 插入管理员用户
INSERT INTO users (username, email, password_hash, real_name, phone, role, status) VALUES
('admin', 'admin@library.com', 'pbkdf2:sha256:600000$...$...', '管理员', '13800000000', 'admin', 'active');

-- 插入图书管理员
INSERT INTO users (username, email, password_hash, real_name, phone, role, status) VALUES
('librarian', 'librarian@library.com', 'pbkdf2:sha256:600000$...$...', '图书管理员', '13800000001', 'librarian', 'active');

-- 插入普通用户
INSERT INTO users (username, email, password_hash, real_name, phone, role, status) VALUES
('user1', 'user1@library.com', 'pbkdf2:sha256:600000$...$...', '用户1', '13800000002', 'user', 'active'),
('user2', 'user2@library.com', 'pbkdf2:sha256:600000$...$...', '用户2', '13800000003', 'user', 'active'),
('user3', 'user3@library.com', 'pbkdf2:sha256:600000$...$...', '用户3', '13800000004', 'user', 'active');

-- 插入图书分类
INSERT INTO categories (name, description) VALUES
('计算机科学', '计算机相关书籍'),
('文学', '文学作品与小说'),
('历史', '历史书籍和传记'),
('科学', '自然科学相关书籍'),
('艺术', '艺术与设计书籍'),
('商业', '商业与管理书籍');

-- 插入图书数据
INSERT INTO books (isbn, title, author, publisher, publish_date, category_id, description, total_count, available_count, status) VALUES
('978-7-111-64057-7', 'Python编程', 'Guido van Rossum', '人民邮电出版社', '2021-01-15', 1, 'Python语言学习指南', 5, 5, 'available'),
('978-7-111-64058-4', 'JavaScript高级编程', 'Nicholas C. Zakas', '人民邮电出版社', '2021-02-20', 1, 'JavaScript深度学习资料', 4, 4, 'available'),
('978-7-111-64059-1', '活着', '余华', '北京十月文艺出版社', '2012-08-01', 2, '现代文学经典作品', 3, 3, 'available'),
('978-7-111-64060-7', '人类简史', '尤瓦尔·赫拉利', '中信出版社', '2014-11-01', 3, '从大历史的角度认识人类', 6, 6, 'available'),
('978-7-111-64061-4', '终身学习', '戴尔·卡内基', '中国华侨出版社', '2015-03-15', 5, '学习方法与成长指南', 4, 4, 'available'),
('978-7-111-64062-1', '精益创业', '埃里克·莱斯', '中信出版社', '2012-09-01', 6, '创业方法论与实践', 5, 5, 'available');
