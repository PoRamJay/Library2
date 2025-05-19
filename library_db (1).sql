-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 19, 2025 at 12:25 PM
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
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `username`, `password_hash`) VALUES
(2, 'A', 'scrypt:32768:8:1$0uLBMcYb4Grhc5FQ$46727bafb3e88b22e9ab0c0f8844225fe4febac774e6bc8c0cfddc72ecefaffe34bb5ee83b5aef0c4c14aff334e09afbd824225a6528883eb218452978731cc5');

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
  `isbn` bigint(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`id`, `title`, `author`, `year_published`, `genre`, `isbn`) VALUES
(1, 'Enchanted to meet you', 'Meg Cabot', 2023, 'Romance Novel', 9788346310789),
(2, 'Peter and the Wolf', 'Sergei Prokofiev', 1936, 'Fiction', 9780446310382),
(3, 'The Great Gatsby', 'F. Scott Fitzgerald', 1925, 'Classic Literature', 9780743273565),
(4, 'To Kill a Mockingbird', 'Harper Lee', 1960, 'Fiction', 9780446310789),
(5, '1984', 'George Orwell', 1949, 'Dystopian Fiction', 9780451524935);

-- --------------------------------------------------------

--
-- Table structure for table `collections`
--

CREATE TABLE `collections` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `language` varchar(2) DEFAULT 'en',
  `isdue` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `collections`
--

INSERT INTO `collections` (`id`, `name`, `user_id`, `language`, `isdue`) VALUES
(1, 'Mango', 1, 'en', 0),
(2, 'Meg', 1, 'en', 0),
(3, 'Something', 1, 'en', 0),
(5, 'Italianis', 1, 'it', 0),
(6, 'Things', 3, 'en', 0),
(7, 'Stuff', 3, 'pt', 0),
(8, 'Death notes', 5, 'en', 1),
(9, 'YNs', 5, 'en', 0);

-- --------------------------------------------------------

--
-- Table structure for table `collection_books`
--

CREATE TABLE `collection_books` (
  `collection_id` int(11) NOT NULL,
  `book_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `collection_books`
--

INSERT INTO `collection_books` (`collection_id`, `book_id`) VALUES
(1, 1),
(1, 2),
(3, 4),
(8, 1),
(8, 5);

-- --------------------------------------------------------

--
-- Table structure for table `support_requests`
--

CREATE TABLE `support_requests` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`) VALUES
(1, 'Minimco', 'scrypt:32768:8:1$p3EOt35OaKIsdcJL$fa25957b111d47cb15ca7ed8ff197e43003f3d56d282e403295c41b789a78ff6856904346529333a5cd59cb60205f9c6d5294fad80b8460b78d7f83769e7e370'),
(2, 'Minim', 'scrypt:32768:8:1$4Um5jGuK4br1WoWQ$1fe3aaacd83eff548751de28a216e5dbfe2530f1e58898a2c22cf706f04bfa04ae2e43eed5cd0dc8f8834e4880e68cd2cf221e13461d5ad5eda9b731ded085cb'),
(3, 'Min', 'scrypt:32768:8:1$aY6HTIW0ivVThHT3$49752b2ed2c6ea491b200056c2f64b46c5423b5a0dac4c4c4384d7f4ce5e1361d0fb33a8938777f20e0b646b95cad5b290e3ebb33626154f5c3069411fb3962c'),
(4, 'd', 'scrypt:32768:8:1$pXOgnWU0i1vprs9Q$657f913e03735a21abf6c8f4c9bf0f9d2c6bb91feeb29c6121d9d5f46b78e74e6cbf5c1dc42ef33b66da773c7b1bbf2cefd532ccd7e0bf4d500251f3fe40bbdc'),
(5, 'Light', 'scrypt:32768:8:1$Mj9xmbWGxlNzKU6x$ca83bacbbe2960d074f174e1dac7a8d22ae70d13700807d1093a5b1a9b20f0c905364c5e3c75c5e94f662bc5d22353e256e31238b38963d1726178d881e60a44');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `collections`
--
ALTER TABLE `collections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `collection_books`
--
ALTER TABLE `collection_books`
  ADD PRIMARY KEY (`collection_id`,`book_id`),
  ADD KEY `book_id` (`book_id`);

--
-- Indexes for table `support_requests`
--
ALTER TABLE `support_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `books`
--
ALTER TABLE `books`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `collections`
--
ALTER TABLE `collections`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `support_requests`
--
ALTER TABLE `support_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `collections`
--
ALTER TABLE `collections`
  ADD CONSTRAINT `collections_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `collection_books`
--
ALTER TABLE `collection_books`
  ADD CONSTRAINT `collection_books_ibfk_1` FOREIGN KEY (`collection_id`) REFERENCES `collections` (`id`),
  ADD CONSTRAINT `collection_books_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`);

--
-- Constraints for table `support_requests`
--
ALTER TABLE `support_requests`
  ADD CONSTRAINT `support_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
