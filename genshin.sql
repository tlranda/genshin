-- MySQL dump 10.13  Distrib 8.0.22, for macos10.15 (x86_64)
--
-- Host: localhost    Database: genshin
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `genshin`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `genshin` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `genshin`;

--
-- Table structure for table `active_streaks`
--

DROP TABLE IF EXISTS `active_streaks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `active_streaks` (
  `userID` int NOT NULL,
  `class` tinyint NOT NULL,
  `rarity` tinyint NOT NULL,
  `streak` int DEFAULT '0',
  PRIMARY KEY (`userID`,`class`,`rarity`),
  CONSTRAINT `active_streaks_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `banners`
--

DROP TABLE IF EXISTS `banners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banners` (
  `class` tinyint NOT NULL,
  `version` int NOT NULL,
  `name` varchar(80) DEFAULT NULL,
  `start` date DEFAULT NULL,
  `end` date DEFAULT NULL,
  `comment` varchar(500) DEFAULT NULL,
  `probability5` float DEFAULT '0.0006',
  `ev5` float DEFAULT '0.016',
  `pity5` int DEFAULT '90',
  `probability4` float DEFAULT '0.051',
  `ev4` float DEFAULT '0.13',
  `pity4` int DEFAULT '10',
  `probability3` float DEFAULT '0.943',
  `ev3` float DEFAULT '0.854',
  PRIMARY KEY (`class`,`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `broken_streaks`
--

DROP TABLE IF EXISTS `broken_streaks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `broken_streaks` (
  `rollID` int NOT NULL,
  `streak` int DEFAULT NULL,
  PRIMARY KEY (`rollID`),
  CONSTRAINT `broken_streaks_ibfk_1` FOREIGN KEY (`rollID`) REFERENCES `rolls` (`rollID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drops`
--

DROP TABLE IF EXISTS `drops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drops` (
  `class` tinyint NOT NULL,
  `version` int NOT NULL,
  `itemID` int NOT NULL,
  `is_promoted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`class`,`version`,`itemID`),
  KEY `itemID` (`itemID`),
  CONSTRAINT `drops_ibfk_1` FOREIGN KEY (`class`, `version`) REFERENCES `banners` (`class`, `version`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `drops_ibfk_2` FOREIGN KEY (`itemID`) REFERENCES `gacha_items` (`itemID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gacha_items`
--

DROP TABLE IF EXISTS `gacha_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gacha_items` (
  `itemID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `rarity` tinyint DEFAULT NULL,
  `type` enum('character','weapon') DEFAULT NULL,
  `subtype` enum('mondstadt','liyue','inazuma','sumeru','fontaine','natlan','snezhnaya','bow','catalyst','claymore','polearm','sword') DEFAULT NULL,
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `pity`
--

DROP TABLE IF EXISTS `pity`;
/*!50001 DROP VIEW IF EXISTS `pity`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `pity` AS SELECT 
 1 AS `rollID`,
 1 AS `name`,
 1 AS `bannername`,
 1 AS `itemname`,
 1 AS `rarity`,
 1 AS `type`,
 1 AS `subtype`,
 1 AS `streak`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `rolls`
--

DROP TABLE IF EXISTS `rolls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rolls` (
  `rollID` int NOT NULL AUTO_INCREMENT,
  `userID` int DEFAULT NULL,
  `class` tinyint DEFAULT NULL,
  `version` int DEFAULT NULL,
  `itemID` int DEFAULT NULL,
  PRIMARY KEY (`rollID`),
  KEY `userID` (`userID`),
  KEY `class` (`class`,`version`),
  KEY `itemID` (`itemID`),
  CONSTRAINT `rolls_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `rolls_ibfk_2` FOREIGN KEY (`class`, `version`) REFERENCES `banners` (`class`, `version`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `rolls_ibfk_3` FOREIGN KEY (`itemID`) REFERENCES `gacha_items` (`itemID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`tlranda`@`localhost`*/ /*!50003 TRIGGER `streak_tracker` BEFORE INSERT ON `rolls` FOR EACH ROW BEGIN
DECLARE r INT DEFAULT 0;
DECLARE id INT DEFAULT 0;
SELECT rarity FROM gacha_items WHERE itemID = NEW.itemID INTO r;
SELECT IFNULL(MAX(rollID),0)+1 FROM rolls INTO id;
SET FOREIGN_KEY_CHECKS=0;
IF r=3 THEN
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 4;
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 5;
INSERT INTO broken_streaks SELECT id, streak+1 FROM active_streaks WHERE userID = NEW.userID AND class = NEW.class AND rarity = 3;
UPDATE active_streaks SET streak = 0 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 3;
ELSE IF r=4 THEN
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 3;
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 5;
INSERT INTO broken_streaks SELECT id, streak+1 FROM active_streaks WHERE userID = NEW.userID AND class = NEW.class AND rarity = 4;
UPDATE active_streaks SET streak = 0 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 4;
ELSE
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 3;
UPDATE active_streaks SET streak = streak + 1 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 4;
INSERT INTO broken_streaks SELECT id, streak+1 FROM active_streaks WHERE userID = NEW.userID AND class = NEW.class AND rarity = 5;
UPDATE active_streaks SET streak = 0 WHERE userID = NEW.userID AND class = NEW.class AND rarity = 5;
END IF;
END IF;
SET FOREIGN_KEY_CHECKS=1;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`tlranda`@`localhost`*/ /*!50003 TRIGGER `initialize_users` AFTER INSERT ON `users` FOR EACH ROW BEGIN
CALL fill_streaks(1);
CALL fill_streaks(2);
CALL fill_streaks(3);
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `genshin`
--

USE `genshin`;

--
-- Final view structure for view `pity`
--

/*!50001 DROP VIEW IF EXISTS `pity`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`tlranda`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `pity` AS select `rolls`.`rollID` AS `rollID`,`users`.`name` AS `name`,`banners`.`name` AS `bannername`,`gacha_items`.`name` AS `itemname`,`gacha_items`.`rarity` AS `rarity`,`gacha_items`.`type` AS `type`,`gacha_items`.`subtype` AS `subtype`,`broken_streaks`.`streak` AS `streak` from ((((`broken_streaks` join `rolls` on((`broken_streaks`.`rollID` = `rolls`.`rollID`))) join `gacha_items` on((`rolls`.`itemID` = `gacha_items`.`itemID`))) join `users` on((`rolls`.`userID` = `users`.`userID`))) join `banners` on(((`banners`.`class` = `rolls`.`class`) and (`banners`.`version` = `rolls`.`version`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-12-12 11:00:52
