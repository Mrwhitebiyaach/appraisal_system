-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: appraisal_system
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acad_years`
--

DROP TABLE IF EXISTS `acad_years`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `acad_years` (
  `year_id` int NOT NULL AUTO_INCREMENT,
  `acad_years` varchar(45) DEFAULT NULL,
  `form_id` int DEFAULT NULL,
  `user_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`year_id`),
  UNIQUE KEY `year_id_UNIQUE` (`year_id`),
  UNIQUE KEY `form_id_UNIQUE` (`form_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acad_years`
--

LOCK TABLES `acad_years` WRITE;
/*!40000 ALTER TABLE `acad_years` DISABLE KEYS */;
INSERT INTO `acad_years` VALUES (1,'2024/25',932757,'123456'),(2,'2021/22',286196,'123456'),(3,'2032/33',246856,'123456'),(4,'2031/32',911545,'123456'),(5,'2024/25',130525,'124'),(6,'2024/25',515988,'125'),(7,'2024/25',895485,'321'),(10,'2021/22',768631,'123'),(11,'2027/28',802018,'123'),(12,'2023/24',708474,'123'),(14,'2024/25',329472,'123'),(15,'2024/25',527559,'619'),(16,'2024/25',905592,'99999'),(17,'2025/26',449389,'99999');
/*!40000 ALTER TABLE `acad_years` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appraisals`
--

DROP TABLE IF EXISTS `appraisals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appraisals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userid` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `approval_date` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `form_id` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `acad_year` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appraisals`
--

LOCK TABLES `appraisals` WRITE;
/*!40000 ALTER TABLE `appraisals` DISABLE KEYS */;
INSERT INTO `appraisals` VALUES (34,'99999','approved','2025-06-30 02:57:58','2025-06-29 21:11:25','2025-06-29 21:27:58','905592','2024/25');
/*!40000 ALTER TABLE `appraisals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certifications`
--

DROP TABLE IF EXISTS `certifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certifications` (
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(495) DEFAULT NULL,
  `uploads` varchar(245) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certifications`
--

LOCK TABLES `certifications` WRITE;
/*!40000 ALTER TABLE `certifications` DISABLE KEYS */;
INSERT INTO `certifications` VALUES ('515988','awd',NULL,NULL),('527559','awda',NULL,NULL),('449389','awd','uploads/cert_449389_1751026742_0_Academic_Calendar_first_half_2025.pdf',NULL),('905592','edit','uploads/cert_905592_1751230967_0_Academic_Calendar_first_half_2025.pdf',NULL),('905592','edit','uploads/cert_905592_1751230967_1_bill.pdf',NULL);
/*!40000 ALTER TABLE `certifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contribution_to_society`
--

DROP TABLE IF EXISTS `contribution_to_society`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contribution_to_society` (
  `form_id` varchar(45) DEFAULT NULL,
  `semester` varchar(45) DEFAULT NULL,
  `activity` varchar(495) DEFAULT NULL,
  `points` varchar(45) DEFAULT NULL,
  `order_cpy` varchar(495) DEFAULT NULL,
  `uploads` varchar(425) DEFAULT NULL,
  `details` varchar(45) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contribution_to_society`
--

LOCK TABLES `contribution_to_society` WRITE;
/*!40000 ALTER TABLE `contribution_to_society` DISABLE KEYS */;
INSERT INTO `contribution_to_society` VALUES ('515988','V','awd','3','awd',NULL,NULL,NULL),('527559','V','awdad','5','awd',NULL,NULL,NULL),('449389','II','awd','3','awd','uploads/contrib_449389_1751026742_1_Academic_Calendar_first_half_2025.pdf','awd','1'),('905592','I','awdawd','3','awd','uploads/contrib_905592_1751230967_1_bill.pdf','awsssss','1'),('905592','II','2222','3','22','uploads/contrib_905592_1751230967_2_poster_appraisalsystem.pdf','dawd','2');
/*!40000 ALTER TABLE `contribution_to_society` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `copyright`
--

DROP TABLE IF EXISTS `copyright`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `copyright` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(495) DEFAULT NULL,
  `month` varchar(45) DEFAULT NULL,
  `reg_no` varchar(555) DEFAULT NULL,
  `filed_pub_grant` varchar(45) DEFAULT NULL,
  `category` varchar(415) DEFAULT NULL,
  `uploads` varchar(425) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `copyright`
--

LOCK TABLES `copyright` WRITE;
/*!40000 ALTER TABLE `copyright` DISABLE KEYS */;
INSERT INTO `copyright` VALUES (NULL,'515988','awd','awd','awd',NULL,NULL,NULL),(NULL,'527559','wad','wada','wdaa',NULL,NULL,NULL),('1','449389','awd','awda','wdaw','Filed','National','uploads/copyright_449389_1751026742_0_Academic_Calendar_first_half_2025.pdf'),('1','905592','1','161','1','Published','International','uploads/copyright_905592_1751230967_0_Academic_Calendar_first_half_2025.pdf'),('2','905592','212','21221','3','Granted','National','uploads/copyright_905592_1751230967_1_poster_appraisalsystem.pdf');
/*!40000 ALTER TABLE `copyright` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_table`
--

DROP TABLE IF EXISTS `custom_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_table` (
  `id` int NOT NULL AUTO_INCREMENT,
  `form_id` varchar(45) NOT NULL,
  `srno` int NOT NULL,
  `columns_data` text,
  `headers` text,
  `uploads` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `table_title` varchar(425) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_form_id` (`form_id`),
  KEY `idx_form_srno` (`form_id`,`srno`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_table`
--

LOCK TABLES `custom_table` WRITE;
/*!40000 ALTER TABLE `custom_table` DISABLE KEYS */;
INSERT INTO `custom_table` VALUES (5,'449389',1,'{\"New Column 1\": \"adw\", \"New Column2\": \"wda11\"}','[\"New Column 1\", \"New Column2\", \"Document\"]','{\"Document\": \"uploads/custom_449389_1751100389_1_Document_Academic_Calendar_first_half_2025.pdf\"}','2025-06-28 09:23:08','2025-06-28 09:23:08','Custom Table 11'),(6,'449389',2,'{\"New Column 1\": \"awd\", \"New Column2\": \"dwa\"}','[\"New Column 1\", \"New Column2\", \"Document\"]','{\"Document\": \"uploads/custom_449389_1751100389_2_Document_bill.pdf\"}','2025-06-28 09:23:08','2025-06-28 09:23:08','Custom Table 11'),(9,'905592',1,'{\"Name\": \"dwa\", \"Role\": \"awd\"}','[\"Name\", \"Role\", \"Document\"]','{\"Document\": \"uploads/custom_905592_1751231100_1_Document_Academic_Calendar_first_half_2025.pdf\"}','2025-06-29 21:05:00','2025-06-29 21:05:00','trail'),(10,'905592',2,'{\"Name\": \"awd\", \"Role\": \"daw\"}','[\"Name\", \"Role\", \"Document\"]','{\"Document\": \"uploads/custom_905592_1751231100_2_Document_bill.pdf\"}','2025-06-29 21:05:00','2025-06-29 21:05:00','trail');
/*!40000 ALTER TABLE `custom_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department_act`
--

DROP TABLE IF EXISTS `department_act`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department_act` (
  `form_id` varchar(45) DEFAULT NULL,
  `semester` varchar(45) DEFAULT NULL,
  `activity` varchar(495) DEFAULT NULL,
  `points` varchar(45) DEFAULT NULL,
  `order_cpy` varchar(495) DEFAULT NULL,
  `uploads` varchar(295) DEFAULT NULL,
  `assessment` varchar(495) DEFAULT NULL,
  `feedback` varchar(495) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department_act`
--

LOCK TABLES `department_act` WRITE;
/*!40000 ALTER TABLE `department_act` DISABLE KEYS */;
INSERT INTO `department_act` VALUES ('515988','ODD','awd','3','dwa',NULL,NULL,NULL,'1'),('515988','ODD','dwa','1','dwa',NULL,NULL,NULL,'2'),('527559','ODD','awdada','3','dwasda',NULL,NULL,NULL,'1'),('905592','ODD','xyz','3','awd','uploads/2023_december_ethical-hacking-and-forensicrev-2019-c-scheme.pdf',NULL,NULL,'1'),('449389','ODD','awd','3','aw','uploads/dept_449389_1_1751026643_bill.pdf',NULL,NULL,'1'),('449389','EVEN','dwa','3','asdw','uploads/dept_449389_2_1751026643_poster_appraisalsystem.pdf',NULL,NULL,'2');
/*!40000 ALTER TABLE `department_act` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_verification`
--

DROP TABLE IF EXISTS `email_verification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_verification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user` (`user_id`),
  UNIQUE KEY `unique_email` (`email`),
  UNIQUE KEY `unique_token` (`token`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_verification`
--

LOCK TABLES `email_verification` WRITE;
/*!40000 ALTER TABLE `email_verification` DISABLE KEYS */;
INSERT INTO `email_verification` VALUES (1,'888','mayanksalvi1908@apsit.edu.in','Im1heWFua3NhbHZpMTkwOEBhcHNpdC5lZHUuaW4i.aDcc-w.2wSbUXhXkAvzlT13nmQ6Q4pvqRM','2025-05-29 19:56:03','2025-05-28 19:56:03'),(2,'99999','mayanksalvi180@apsit.edu.in','Im1heWFua3NhbHZpMTgwQGFwc2l0LmVkdS5pbiI.aDcr9g.ThKT-KQFIaZzvm1wXFyD2CGbR3M','2025-05-29 20:59:59','2025-05-28 20:59:58');
/*!40000 ALTER TABLE `email_verification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `external_projects`
--

DROP TABLE IF EXISTS `external_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `external_projects` (
  `form_id` varchar(45) DEFAULT NULL,
  `role` varchar(495) DEFAULT NULL,
  `desc` varchar(495) DEFAULT NULL,
  `contribution` varchar(495) DEFAULT NULL,
  `university` varchar(495) DEFAULT NULL,
  `duration` varchar(495) DEFAULT NULL,
  `comments` varchar(495) DEFAULT NULL,
  `upload` varchar(415) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `external_projects`
--

LOCK TABLES `external_projects` WRITE;
/*!40000 ALTER TABLE `external_projects` DISABLE KEYS */;
INSERT INTO `external_projects` VALUES ('515988','awd','awd','adwd','wdad','waw','d',NULL,NULL),('527559','awd','awda','dawd','dada','awda','wd',NULL,NULL),('449389','dawda','wawd','wd','awda','da','wd','uploads/external_449389_1751026742_1_Academic_Calendar_first_half_2025.pdf','1'),('905592','wad','awda','wda','dawd','dwdwd','awd','uploads/external_905592_1751230967_1_poster_appraisalsystem.pdf','1'),('905592','dwa','dwad','wda','dwad','222','dwa','uploads/external_905592_1751230967_2_bill.pdf','2');
/*!40000 ALTER TABLE `external_projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `form_id` varchar(45) NOT NULL,
  `feedback` varchar(425) DEFAULT NULL,
  `principle_feedback` varchar(425) DEFAULT NULL,
  `r1` varchar(45) DEFAULT NULL,
  `r2` varchar(45) DEFAULT NULL,
  `r3` varchar(45) DEFAULT NULL,
  `r4` varchar(45) DEFAULT NULL,
  `r5` varchar(45) DEFAULT NULL,
  `r6` varchar(45) DEFAULT NULL,
  `r7` varchar(45) DEFAULT NULL,
  `r8` varchar(45) DEFAULT NULL,
  `r9` varchar(45) DEFAULT NULL,
  `r10` varchar(45) DEFAULT NULL,
  `r_avg` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES ('449389','',NULL,'1','2','1','1','1','1','1','1','1','1','2'),('515988','abcd',NULL,'4','4','4','4','4','4','4','4','4','4','8'),('905592','awd','awd2','1','1','1','1','1','1','1','1','1','1','2');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form1_tot`
--

DROP TABLE IF EXISTS `form1_tot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form1_tot` (
  `form_id` int NOT NULL,
  `total` varchar(45) DEFAULT NULL,
  `teaching` varchar(45) DEFAULT NULL,
  `feedback` varchar(45) DEFAULT NULL,
  `hodas1` varchar(45) DEFAULT NULL,
  `hodas2` varchar(45) DEFAULT NULL,
  `hodfeed1` varchar(425) DEFAULT NULL,
  `hodfeed2` varchar(425) DEFAULT NULL,
  `prinas1` varchar(45) DEFAULT NULL,
  `prinas2` varchar(45) DEFAULT NULL,
  `prinfeed1` varchar(425) DEFAULT NULL,
  `prinfeed2` varchar(425) DEFAULT NULL,
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form1_tot`
--

LOCK TABLES `form1_tot` WRITE;
/*!40000 ALTER TABLE `form1_tot` DISABLE KEYS */;
INSERT INTO `form1_tot` VALUES (130525,'0','0','0',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(449389,'64','24','20','0','0','','',NULL,NULL,NULL,NULL),(515988,'28','18','10','18','10','wwwwwwww','wwwwwwwwwwwwwwwwww',NULL,NULL,NULL,NULL),(527559,'33','13','20',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(905592,'54','19','20','15','15','www','ww','6','6','111','222');
/*!40000 ALTER TABLE `form1_tot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form2_tot`
--

DROP TABLE IF EXISTS `form2_tot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form2_tot` (
  `form_id` int NOT NULL,
  `total` varchar(45) DEFAULT NULL,
  `dept` varchar(45) DEFAULT NULL,
  `institute` varchar(45) DEFAULT NULL,
  `hodas3` varchar(45) DEFAULT NULL,
  `hodas4` varchar(45) DEFAULT NULL,
  `hodfeed3` varchar(425) DEFAULT NULL,
  `hodfeed4` varchar(425) DEFAULT NULL,
  `prinas3` varchar(45) DEFAULT NULL,
  `prinas4` varchar(45) DEFAULT NULL,
  `prinfeed3` varchar(425) DEFAULT NULL,
  `prinfeed4` varchar(425) DEFAULT NULL,
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form2_tot`
--

LOCK TABLES `form2_tot` WRITE;
/*!40000 ALTER TABLE `form2_tot` DISABLE KEYS */;
INSERT INTO `form2_tot` VALUES (449389,'12','6','6','0','0','','',NULL,NULL,NULL,NULL),(515988,'6','4','2','3','2','wwwwwww','wwwwwwwwwwwwww',NULL,NULL,NULL,NULL),(527559,'6','3','3',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(905592,'6','3','3','15','10','ww','ww','5','7','333','444');
/*!40000 ALTER TABLE `form2_tot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form3_assessment`
--

DROP TABLE IF EXISTS `form3_assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form3_assessment` (
  `form_id` varchar(45) NOT NULL,
  `self_assessment_marks` varchar(45) DEFAULT '0',
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form3_assessment`
--

LOCK TABLES `form3_assessment` WRITE;
/*!40000 ALTER TABLE `form3_assessment` DISABLE KEYS */;
INSERT INTO `form3_assessment` VALUES ('449389','2'),('515988','3'),('527559','10'),('905592','9');
/*!40000 ALTER TABLE `form3_assessment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form3_tot`
--

DROP TABLE IF EXISTS `form3_tot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form3_tot` (
  `form_id` int NOT NULL,
  `total` varchar(45) DEFAULT NULL,
  `acr` varchar(45) DEFAULT NULL,
  `society` varchar(45) DEFAULT NULL,
  `hodas5` varchar(45) DEFAULT NULL,
  `hodas6` varchar(45) DEFAULT NULL,
  `hodfeed5` varchar(425) DEFAULT NULL,
  `hodfeed6` varchar(425) DEFAULT NULL,
  `prinas5` varchar(45) DEFAULT NULL,
  `prinas6` varchar(45) DEFAULT NULL,
  `prinfeed5` varchar(425) DEFAULT NULL,
  `prinfeed6` varchar(425) DEFAULT NULL,
  `finalacr` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form3_tot`
--

LOCK TABLES `form3_tot` WRITE;
/*!40000 ALTER TABLE `form3_tot` DISABLE KEYS */;
INSERT INTO `form3_tot` VALUES (449389,'5','2','3','10','10','','awd',NULL,NULL,NULL,NULL,'6'),(515988,'6','3','3','10','2','wwwww','addw',NULL,NULL,NULL,NULL,'9'),(527559,'15','10','5',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(905592,'15','9','6','6','9','1ww','ww','6','6','555','666','4');
/*!40000 ALTER TABLE `form3_tot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_status`
--

DROP TABLE IF EXISTS `form_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userid` varchar(50) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `principal_submitted` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userid` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_status`
--

LOCK TABLES `form_status` WRITE;
/*!40000 ALTER TABLE `form_status` DISABLE KEYS */;
INSERT INTO `form_status` VALUES (1,'99999','approved',1,'2025-06-08 16:08:56','2025-06-08 16:08:56');
/*!40000 ALTER TABLE `form_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `institute_act`
--

DROP TABLE IF EXISTS `institute_act`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `institute_act` (
  `form_id` varchar(45) DEFAULT NULL,
  `semester` varchar(45) DEFAULT NULL,
  `activity` varchar(495) DEFAULT NULL,
  `points` varchar(45) DEFAULT NULL,
  `order_cpy` varchar(495) DEFAULT NULL,
  `uploads` varchar(255) DEFAULT NULL,
  `assessment` varchar(495) DEFAULT NULL,
  `feedback` varchar(495) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `institute_act`
--

LOCK TABLES `institute_act` WRITE;
/*!40000 ALTER TABLE `institute_act` DISABLE KEYS */;
INSERT INTO `institute_act` VALUES ('515988','ODD','awd','2','adw',NULL,NULL,NULL,'1'),('527559','ODD','dawda','3','dsadwad',NULL,NULL,NULL,'1'),('905592','ODD','awd','3','wad','uploads/Academic_Calendar_first_half_2025.pdf',NULL,NULL,'1'),('449389','EVEN','dwa','3','dw','uploads/inst_449389_1_1751026643_Academic_Calendar_first_half_2025.pdf',NULL,NULL,'1'),('449389','ODD','dwa','3','ss','uploads/inst_449389_2_1751026643_bill.pdf',NULL,NULL,'2');
/*!40000 ALTER TABLE `institute_act` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mem_uni`
--

DROP TABLE IF EXISTS `mem_uni`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mem_uni` (
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(495) DEFAULT NULL,
  `roles` varchar(495) DEFAULT NULL,
  `designation` varchar(495) DEFAULT NULL,
  `upload` varchar(295) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mem_uni`
--

LOCK TABLES `mem_uni` WRITE;
/*!40000 ALTER TABLE `mem_uni` DISABLE KEYS */;
INSERT INTO `mem_uni` VALUES ('515988','awd','awd','awd',NULL,NULL),('527559','awd','awda','wd',NULL,NULL),('449389','dwad','wda','daw','uploads/committee_449389_1751026742_1_bill.pdf','1'),('905592','dwa','dwa','aw','uploads/committee_905592_1751230967_1_Academic_Calendar_first_half_2025.pdf','1');
/*!40000 ALTER TABLE `mem_uni` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members_conference`
--

DROP TABLE IF EXISTS `members_conference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members_conference` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(425) DEFAULT NULL,
  `designation` varchar(425) DEFAULT NULL,
  `upload` varchar(215) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members_conference`
--

LOCK TABLES `members_conference` WRITE;
/*!40000 ALTER TABLE `members_conference` DISABLE KEYS */;
INSERT INTO `members_conference` VALUES ('1','449389','awd','awd','uploads/conf_449389_1751026742_1_bill.pdf'),('1','905592','ddaw','da','uploads/conf_905592_1751230967_1_Academic_Calendar_first_half_2025.pdf'),('2','905592','a','a','uploads/conf_905592_1751230967_2_bill.pdf');
/*!40000 ALTER TABLE `members_conference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `moocs`
--

DROP TABLE IF EXISTS `moocs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `moocs` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(445) DEFAULT NULL,
  `month` varchar(435) DEFAULT NULL,
  `duration` varchar(45) DEFAULT NULL,
  `completion` varchar(455) DEFAULT NULL,
  `upload` varchar(415) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moocs`
--

LOCK TABLES `moocs` WRITE;
/*!40000 ALTER TABLE `moocs` DISABLE KEYS */;
INSERT INTO `moocs` VALUES ('1','515988','awd','awd','wdda','No',NULL),('1','527559','awda','awd','awd','Yes',NULL),('1','449389','awd','awd','awd','No','uploads/moocs_449389_1751028460_1_poster_appraisalsystem.pdf'),('2','449389','awd','dwa','wda','No','uploads/moocs_449389_1751028460_2_Academic_Calendar_first_half_2025.pdf'),('1','905592','awd','awd','222','Yes','uploads/moocs_905592_1751230967_1_poster_appraisalsystem.pdf'),('2','905592','dwa','dwa','ss','No','uploads/moocs_905592_1751230967_2_Academic_Calendar_first_half_2025.pdf');
/*!40000 ALTER TABLE `moocs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `numeric_points_attained`
--

DROP TABLE IF EXISTS `numeric_points_attained`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `numeric_points_attained` (
  `srno` int DEFAULT NULL,
  `form_id` int DEFAULT NULL,
  `academic_review1` int DEFAULT NULL,
  `academic_review2` int DEFAULT NULL,
  `avg_score` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `numeric_points_attained`
--

LOCK TABLES `numeric_points_attained` WRITE;
/*!40000 ALTER TABLE `numeric_points_attained` DISABLE KEYS */;
INSERT INTO `numeric_points_attained` VALUES (1,905592,18,12,15),(1,449389,20,20,20);
/*!40000 ALTER TABLE `numeric_points_attained` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patents`
--

DROP TABLE IF EXISTS `patents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patents` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(552) DEFAULT NULL,
  `month` varchar(45) DEFAULT NULL,
  `reg_no` varchar(425) DEFAULT NULL,
  `filed_pub_grant` varchar(45) DEFAULT NULL,
  `category` varchar(45) DEFAULT NULL,
  `uploads` varchar(425) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patents`
--

LOCK TABLES `patents` WRITE;
/*!40000 ALTER TABLE `patents` DISABLE KEYS */;
INSERT INTO `patents` VALUES ('1','449389','dwad','awda','wdawd','Filed','International','uploads/patent_449389_1751026742_0_poster_appraisalsystem.pdf'),('1','905592','111','111','11','Published','International','uploads/patent_905592_1751230967_0_bill.pdf'),('2','905592','222212','21111','3','Published','International','uploads/patent_905592_1751230967_1_Academic_Calendar_first_half_2025.pdf');
/*!40000 ALTER TABLE `patents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_person`
--

DROP TABLE IF EXISTS `resource_person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_person` (
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(425) DEFAULT NULL,
  `dept` varchar(425) DEFAULT NULL,
  `name_oi` varchar(425) DEFAULT NULL,
  `num_op` varchar(425) DEFAULT NULL,
  `upload` varchar(415) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_person`
--

LOCK TABLES `resource_person` WRITE;
/*!40000 ALTER TABLE `resource_person` DISABLE KEYS */;
INSERT INTO `resource_person` VALUES ('515988','awd','awd','awd','12',NULL,NULL),('527559','wdawd','wdawd','awda','0',NULL,NULL),('449389','awd','awd','awda','','uploads/resource_449389_1751026742_1_bill.pdf','1'),('905592','awd','awda','ed','5','uploads/resource_905592_1751230967_1_bill.pdf','1'),('905592','awdw','awd','awd','3','uploads/resource_905592_1751230967_2_bill.pdf','2');
/*!40000 ALTER TABLE `resource_person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `self_imp`
--

DROP TABLE IF EXISTS `self_imp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `self_imp` (
  `form_id` varchar(45) DEFAULT NULL,
  `title` varchar(4522) DEFAULT NULL,
  `month` varchar(4225) DEFAULT NULL,
  `name_of_conf` varchar(4225) DEFAULT NULL,
  `issn` varchar(425) DEFAULT NULL,
  `co_auth` varchar(222) DEFAULT NULL,
  `imp_conference` varchar(225) DEFAULT NULL,
  `num_of_citations` varchar(425) DEFAULT NULL,
  `rating` varchar(425) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL,
  `uploads` varchar(415) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `self_imp`
--

LOCK TABLES `self_imp` WRITE;
/*!40000 ALTER TABLE `self_imp` DISABLE KEYS */;
INSERT INTO `self_imp` VALUES ('515988','awd','awd','awd','awd','awd','',NULL,NULL,NULL,NULL),('527559','awd','wdaw','dawd','awd','awdaw','',NULL,NULL,NULL,NULL),('449389','awd','awd','awd','awd','awda','awd','da','awd','1','uploads/selfimp_449389_1751026742_1_bill.pdf'),('905592','111','2','3','4','5','6','7','8','1','uploads/selfimp_905592_1751230967_1_bill.pdf');
/*!40000 ALTER TABLE `self_imp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `short_term_training`
--

DROP TABLE IF EXISTS `short_term_training`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `short_term_training` (
  `srno` int DEFAULT NULL,
  `form_id` int DEFAULT NULL,
  `name` varchar(425) DEFAULT NULL,
  `technology` varchar(919) DEFAULT NULL,
  `duration` varchar(75) DEFAULT NULL,
  `date` varchar(85) DEFAULT NULL,
  `organizing_institute` varchar(425) DEFAULT NULL,
  `mode` varchar(45) DEFAULT NULL,
  `upload` varchar(525) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `short_term_training`
--

LOCK TABLES `short_term_training` WRITE;
/*!40000 ALTER TABLE `short_term_training` DISABLE KEYS */;
INSERT INTO `short_term_training` VALUES (1,449389,'dwad','awd','awd','awda','wdawd','Offline','uploads/training_449389_1751026742_0_Academic_Calendar_first_half_2025.pdf'),(1,905592,'222','222','22','222','222','Online','uploads/training_905592_1751230967_0_Academic_Calendar_first_half_2025.pdf'),(2,905592,'33','3','3','3','33','Online','uploads/training_905592_1751230967_1_bill.pdf');
/*!40000 ALTER TABLE `short_term_training` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `special_mentions`
--

DROP TABLE IF EXISTS `special_mentions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `special_mentions` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(415) DEFAULT NULL,
  `roles` varchar(215) DEFAULT NULL,
  `uploads` varchar(415) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `special_mentions`
--

LOCK TABLES `special_mentions` WRITE;
/*!40000 ALTER TABLE `special_mentions` DISABLE KEYS */;
INSERT INTO `special_mentions` VALUES ('1','449389','awd','awd','uploads/special_449389_1751026742_1_poster_appraisalsystem.pdf'),('1','905592','awd','awd','uploads/special_905592_1751230967_1_poster_appraisalsystem.pdf');
/*!40000 ALTER TABLE `special_mentions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students_feedback`
--

DROP TABLE IF EXISTS `students_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students_feedback` (
  `form_id` int DEFAULT NULL,
  `semester` varchar(45) DEFAULT NULL,
  `course_code` varchar(45) DEFAULT NULL,
  `total_points` int DEFAULT NULL,
  `points_obtained` varchar(45) DEFAULT NULL,
  `uploads` varchar(255) DEFAULT NULL,
  `assessment` varchar(45) DEFAULT NULL,
  `srno` int DEFAULT NULL,
  KEY `form_id_idx` (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students_feedback`
--

LOCK TABLES `students_feedback` WRITE;
/*!40000 ALTER TABLE `students_feedback` DISABLE KEYS */;
INSERT INTO `students_feedback` VALUES (515988,'I','Physics',5,'2',NULL,NULL,1),(527559,'I','Chemistry',5,'4',NULL,NULL,1),(905592,'II','Mathematics-II',5,'4','uploads/feedback_905592_1_1751230725_bill.pdf',NULL,1),(449389,'II','Mathematics-II',5,'5','uploads/feedback_449389_1_1751055668_Academic_Calendar_first_half_2025.pdf',NULL,1),(449389,'IV','Network Lab',5,'3','uploads/feedback_449389_2_1751056116_poster_appraisalsystem.pdf',NULL,2);
/*!40000 ALTER TABLE `students_feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `swayam`
--

DROP TABLE IF EXISTS `swayam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `swayam` (
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL,
  `name` varchar(495) DEFAULT NULL,
  `month` varchar(45) DEFAULT NULL,
  `duration` varchar(45) DEFAULT NULL,
  `completion` varchar(495) DEFAULT NULL,
  `upload` varchar(415) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `swayam`
--

LOCK TABLES `swayam` WRITE;
/*!40000 ALTER TABLE `swayam` DISABLE KEYS */;
INSERT INTO `swayam` VALUES ('1','515988','awd','dawd','awd','Yes',NULL),('1','527559','awda','da','wda','Yes',NULL),('1','449389','awd','awd','awd','Yes','uploads/swayam_449389_1751029254_1_Academic_Calendar_first_half_2025.pdf'),('2','449389','awd','awd','awd','No','uploads/swayam_449389_1751029254_2_bill.pdf'),('1','905592','dwww','wwww','333333','Yes','uploads/swayam_905592_1751230967_1_bill.pdf'),('2','905592','sas','as','ss','No','uploads/swayam_905592_1751230967_2_poster_appraisalsystem.pdf');
/*!40000 ALTER TABLE `swayam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teaching_process`
--

DROP TABLE IF EXISTS `teaching_process`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teaching_process` (
  `form_id` int DEFAULT NULL,
  `semester` varchar(45) DEFAULT NULL,
  `course_code` varchar(45) DEFAULT NULL,
  `classes_scheduled` int DEFAULT NULL,
  `classes_held` int DEFAULT NULL,
  `totalpoints` int DEFAULT NULL,
  `assessment` varchar(45) DEFAULT NULL,
  `srno` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teaching_process`
--

LOCK TABLES `teaching_process` WRITE;
/*!40000 ALTER TABLE `teaching_process` DISABLE KEYS */;
INSERT INTO `teaching_process` VALUES (515988,'I','Mathematics-I',5,4,0,NULL,1),(515988,'I','Physics',5,3,0,NULL,2),(527559,'I','Chemistry',6,3,0,NULL,1),(905592,'I','Mathematics-I',12,9,4,NULL,1),(449389,'I','Physics Lab',9,3,4,NULL,1);
/*!40000 ALTER TABLE `teaching_process` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `total`
--

DROP TABLE IF EXISTS `total`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `total` (
  `form_id` int NOT NULL,
  `acad_years` varchar(45) DEFAULT NULL,
  `total` varchar(45) DEFAULT NULL,
  `hodtotal` varchar(45) DEFAULT NULL,
  `user_id` varchar(45) DEFAULT NULL,
  `dept` varchar(45) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `principle_total` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `total`
--

LOCK TABLES `total` WRITE;
/*!40000 ALTER TABLE `total` DISABLE KEYS */;
INSERT INTO `total` VALUES (123456,'2024/25','60','68','128','IT','Roshna Sangle',NULL),(449389,'2025/26','81','20','99999','IT','Mayank Ashok Salvi',NULL),(515988,'2024/25','70','45','125','IT','Vishal Badgujar',NULL),(527559,'2024/25','54',NULL,'619','IT','dhanashree salvi',NULL),(654321,'2023/24','72','70','213','IT','omkar',NULL),(905592,'2024/25','75','70','99999','IT','Mayank Ashok Salvi','36');
/*!40000 ALTER TABLE `total` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `userid` int NOT NULL,
  `gmail` varchar(455) NOT NULL,
  `password` varchar(455) NOT NULL,
  `role` varchar(425) NOT NULL,
  `dept` varchar(45) NOT NULL,
  `name` varchar(495) NOT NULL,
  `designation` varchar(495) DEFAULT NULL,
  `d_o_j` varchar(45) DEFAULT NULL,
  `dob` varchar(45) DEFAULT NULL,
  `edu_q` varchar(495) DEFAULT NULL,
  `exp` varchar(495) DEFAULT NULL,
  `profile_image` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `userid_UNIQUE` (`userid`),
  UNIQUE KEY `gmail_UNIQUE` (`gmail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'principal@apsit.edu.in','scrypt:32768:8:1$I6NCVLtRu0zkLZGf$75186da8031eb42497f0320d5d377f1d3b8b05baab855cdd8e349461152455c696c175b62de08bdb7e791f1adfc16f58c22e7ce71efd8afcd786c2fc7894341c','Principal','NULL','xyz','Principal','2024-09-01','2004-12-03','phd','10 years',NULL),(123,'mayanksalvi@apsit.edu.in','Salvi@123','Faculty','IT','mayank salvi','Assistant Professor','2024-09-29','2024-09-25','btech','nothing',NULL),(125,'Roshnasangle@apsit.edu.in','salvi@123','Faculty','IT','Roshna Sangle','Assistant Professor','2024-09-30','2024-10-07','btech','3 years','static/profile_images\\125_SmartSelect_20250217_224404_Gallery.jpg'),(128,'Shraddhabirje@apsit.edu.in','Salvi@123','Faculty','IT','Shraddha Birje','Assistant Professor','2024-10-01','2024-10-07','be','nothing\r\n',NULL),(166,'Mandarganjapurkar@apsit.edu.in','abcd1234','Faculty','IT','Mandar Ganjapurkar','student','2024-09-25','2004-12-03','12th pass','nothing',NULL),(213,'hod1@apsit.edu.in','scrypt:32768:8:1$I6NCVLtRu0zkLZGf$75186da8031eb42497f0320d5d377f1d3b8b05baab855cdd8e349461152455c696c175b62de08bdb7e791f1adfc16f58c22e7ce71efd8afcd786c2fc7894341c','Higher Authority','IT','omkar','Head of Department','2024-10-06','2024-09-30','phd','9 years',NULL),(321,'aniruddha@apsit.edu.in','Salvi@123','Faculty','CS','Mandar Ganjapurkar','Professor','2024-09-30','2024-10-06','btech ','3 years ',NULL),(412,'dhanashreemayank@gmail.com','mayank@123','Faculty','CS','mayank','student','2024-09-03','2024-10-06','btech','4 years',NULL),(456,'rrr@apsit.edu.in','Salvi@123','Faculty','MECH','m','Professor','2024-10-24','2024-10-31','i','i',NULL),(619,'dhanashreesalvi180@apsit.edu.in','Salvi@123','Faculty','IT','ashok salvi','Professor','2025-05-08','1998-05-09','trail','trial',NULL),(12345,'gandhar@apsit.edu.in','Salvi@123','Faculty','MECH','gandhar rane','Professor','2019-06-28','1997-08-20','PHD','very good',NULL),(99999,'mayanksalvi180@apsit.edu.in','scrypt:32768:8:1$I6NCVLtRu0zkLZGf$75186da8031eb42497f0320d5d377f1d3b8b05baab855cdd8e349461152455c696c175b62de08bdb7e791f1adfc16f58c22e7ce71efd8afcd786c2fc7894341c','Faculty','IT','Mayank Ashok Salvi','Professor','2025-05-02','2025-05-01','trail','trail','static/profile_images\\99999_sample_breed2.jpg'),(654321,'hod1@gmail.com','scrypt:32768:8:1$I6NCVLtRu0zkLZGf$75186da8031eb42497f0320d5d377f1d3b8b05baab855cdd8e349461152455c696c175b62de08bdb7e791f1adfc16f58c22e7ce71efd8afcd786c2fc7894341c','Head of Dept.','IT','mayank','HOD','2024-09-01','2004-12-03','Phd','9 years',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webinar`
--

DROP TABLE IF EXISTS `webinar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webinar` (
  `name` varchar(495) DEFAULT NULL,
  `technology` varchar(495) DEFAULT NULL,
  `duration` varchar(495) DEFAULT NULL,
  `date` varchar(495) DEFAULT NULL,
  `int_ext` varchar(495) DEFAULT NULL,
  `name_of_institute` varchar(495) DEFAULT NULL,
  `upload` varchar(415) DEFAULT NULL,
  `srno` varchar(45) DEFAULT NULL,
  `form_id` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webinar`
--

LOCK TABLES `webinar` WRITE;
/*!40000 ALTER TABLE `webinar` DISABLE KEYS */;
INSERT INTO `webinar` VALUES ('awd','awd','awdaw','','','awd',NULL,'1','515988'),('awd','awd','awda','wd','Internal','awd',NULL,'1','527559'),('awd','awda','wdaw','daw','Internal','awd','uploads/webinar_449389_1751026742_1_Academic_Calendar_first_half_2025.pdf','1','449389'),('awd','444444444444','44444444','awd','External','adw','uploads/webinar_905592_1751230967_1_Academic_Calendar_first_half_2025.pdf','1','905592'),('dwa','dwa','dwa','sw','Internal','dwa','uploads/webinar_905592_1751230967_2_bill.pdf','2','905592');
/*!40000 ALTER TABLE `webinar` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-30  3:20:36
