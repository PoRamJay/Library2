-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 19, 2025 at 07:59 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `library_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

CREATE TABLE `books` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `year_published` int(11) DEFAULT NULL,
  `genre` varchar(100) DEFAULT NULL,
  `isbn` bigint(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`id`, `title`, `author`, `year_published`, `genre`, `isbn`, `status`) VALUES
(1, 'Enchanted to meet you', 'Meg Cabot', 2023, 'Romance Novel', 9781234567897, 'borrowed'),
(2, 'Peter and the Wolf', 'Sergei Prokofiev', 1936, 'Fiction', 9781222737897, 'borrowed'),
(3, 'The Great Gatsby', 'F. Scott Fitzgerald', 1925, 'Classic Literature', 9780743273565, 'borrowed'),
(4, 'To Kill a Mockingbird', 'Harper Lee', 1960, 'Fiction', 9780446310789, 'borrowed'),
(5, '1984', 'George Orwell', 1949, 'Dystopian Fiction', 9780451524935, 'borrowed'),
(6, 'Science book', 'Albert Einstein', 1967, 'Science', 9181234567857, 'available'),
(7, 'Nine', 'El-Amein', 2001, 'History', 9181934567852, 'borrowed');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `books`
--
ALTER TABLE `books`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
