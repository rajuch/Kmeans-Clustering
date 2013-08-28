delimiter $$

CREATE TABLE `clean_keywords` (
  `id` int(11) NOT NULL,
  `word` varchar(45) COLLATE utf8_bin NOT NULL,
  `count` varchar(45) COLLATE utf8_bin NOT NULL,
  `df` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index2` (`word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin$$





delimiter $$

CREATE TABLE `keywords` (
  `id` int(11) NOT NULL,
  `word` varchar(45) COLLATE utf8_bin NOT NULL,
  `repo_id` int(11) DEFAULT NULL,
  `tf` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index2` (`word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin$$
delimiter $$

CREATE TABLE `repository` (
  `id` int(11) NOT NULL,
  `name` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `url` varchar(100) COLLATE utf8_bin NOT NULL,
  `description` varchar(2000) COLLATE utf8_bin DEFAULT NULL,
  `author` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `language` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `timestamp` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index2` (`url`),
  KEY `index3` (`author`),
  KEY `index4` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin$$
