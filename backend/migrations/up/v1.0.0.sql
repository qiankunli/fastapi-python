CREATE TABLE IF NOT EXISTS  `resource` (
    `id` varchar(36) NOT NULL COMMENT '资源id',
    `parent_id` varchar(36) DEFAULT NULL COMMENT '父资源id',
    `queue` varchar(32) NOT NULL COMMENT '分组',
    `name` varchar(50) DEFAULT 'default' NOT NULL COMMENT '名称',
    `type` varchar(50) NOT NULL COMMENT '类型',
    `extension` varchar(50) NOT NULL COMMENT '扩展名',
    `meta_data` json DEFAULT NULL COMMENT '元数据',
    `storage_url` varchar(255) NOT NULL COMMENT '存储地址',
    `config` json DEFAULT NULL COMMENT '转换配置',
    `text` text DEFAULT NULL COMMENT '转换结果',
    `text_url` varchar(255) DEFAULT NULL COMMENT 'text存储地址',
    `create_time` datetime DEFAULT (now()) COMMENT '创建时间',
    `update_time` datetime DEFAULT (now()) COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `ix_parent_id` (`parent_id`),
    KEY `ix_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


