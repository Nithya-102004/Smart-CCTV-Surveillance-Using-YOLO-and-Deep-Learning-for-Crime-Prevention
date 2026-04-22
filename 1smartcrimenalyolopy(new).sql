-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Feb 15, 2025 at 10:23 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `2smartcrimenalpy`
--

-- --------------------------------------------------------

--
-- Table structure for table `entrytb`
--

CREATE TABLE `entrytb` (
  `id` int(10) NOT NULL auto_increment,
  `UserName` varchar(250) NOT NULL,
  `Date` varchar(250) NOT NULL,
  `Time` varchar(250) NOT NULL,
  `Status` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `entrytb`
--

INSERT INTO `entrytb` (`id`, `UserName`, `Date`, `Time`, `Status`) VALUES
(1, 'rakesh001', '2025-02-15', '15:18:44', 'Entry'),
(2, 'rakesh001', '2025-02-15', '15:20:00', 'Entry');

-- --------------------------------------------------------

--
-- Table structure for table `regtb`
--

CREATE TABLE `regtb` (
  `id` bigint(10) NOT NULL auto_increment,
  `Name` varchar(250) NOT NULL,
  `Mobile` varchar(250) NOT NULL,
  `Address` varchar(500) NOT NULL,
  `UserName` varchar(500) NOT NULL,
  `CrimeID` varchar(250) NOT NULL,
  `CrimeInfo` varchar(500) NOT NULL,
  `Image` varchar(500) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `regtb`
--

INSERT INTO `regtb` (`id`, `Name`, `Mobile`, `Address`, `UserName`, `CrimeID`, `CrimeInfo`, `Image`) VALUES
(1, 'rakesh', '9486365535', 'No 16, Samnath Plaza, Madurai Main Road, Melapudhur', 'rakesh001', 'cr001', 'theft', 'static/user/rakesh001.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `unktb`
--

CREATE TABLE `unktb` (
  `id` bigint(20) NOT NULL auto_increment,
  `Date` varchar(250) NOT NULL,
  `Time` varchar(250) NOT NULL,
  `Image` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `unktb`
--

