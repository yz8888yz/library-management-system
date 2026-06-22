-- 图书管理系统数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS library_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_management;

-- 1. 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(80) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(120) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    real_name VARCHAR(100) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '电话号码',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '用户角色: admin, librarian, user',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '账户状态: active, inactive, suspended',
    borrow_count INT NOT NULL DEFAULT 0 COMMENT '借阅次数',
    overdue_count INT NOT NULL DEFAULT 0 COMMENT '逾期次数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login DATETIME COMMENT '最后登录时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 图书分类表
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '分类名称',
    description TEXT COMMENT '分类描述',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图书分类表';

-- 3. 图书表
CREATE TABLE books (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '图书ID',
    isbn VARCHAR(20) UNIQUE NOT NULL COMMENT 'ISBN编号',
    title VARCHAR(255) NOT NULL COMMENT '图书标题',
    author VARCHAR(100) NOT NULL COMMENT '作者',
    publisher VARCHAR(100) COMMENT '出版社',
    publish_date DATE COMMENT '出版日期',
    category_id INT NOT NULL COMMENT '分类ID',
    description TEXT COMMENT '图书描述',
    cover_url VARCHAR(500) COMMENT '封面URL',
    total_count INT NOT NULL DEFAULT 0 COMMENT '总数量',
    available_count INT NOT NULL DEFAULT 0 COMMENT '可用数量',
    borrow_count INT NOT NULL DEFAULT 0 COMMENT '被借阅次数',
    status VARCHAR(20) NOT NULL DEFAULT 'available' COMMENT '状态: available, unavailable, deprecated',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_isbn (isbn),
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_category (category_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图书表';

-- 4. 借阅记录表
CREATE TABLE borrow_records (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    book_id INT NOT NULL COMMENT '图书ID',
    borrow_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '借阅日期',
    due_date DATETIME NOT NULL COMMENT '应归还日期',
    return_date DATETIME COMMENT '实际归还日期',
    renew_count INT NOT NULL DEFAULT 0 COMMENT '续借次数',
    max_renew_count INT NOT NULL DEFAULT 3 COMMENT '最大续借次数',
    status VARCHAR(20) NOT NULL DEFAULT 'borrowed' COMMENT '状态: borrowed, returned, overdue, lost',
    fine FLOAT NOT NULL DEFAULT 0 COMMENT '罚款金额',
    fine_paid BOOLEAN NOT NULL DEFAULT FALSE COMMENT '罚款是否已支付',
    remarks TEXT COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='借阅记录表';

-- 创建索引以优化查询性能
CREATE INDEX idx_borrow_user_status ON borrow_records(user_id, status);
CREATE INDEX idx_borrow_book_status ON borrow_records(book_id, status);
