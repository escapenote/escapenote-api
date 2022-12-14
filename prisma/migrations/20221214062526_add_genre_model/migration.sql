/*
  Warnings:

  - You are about to drop the column `closingHour` on the `cafes` table. All the data in the column will be lost.
  - You are about to drop the column `openingHour` on the `cafes` table. All the data in the column will be lost.
  - You are about to drop the column `genre` on the `themes` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE `cafes` DROP COLUMN `closingHour`,
    DROP COLUMN `openingHour`,
    ADD COLUMN `openingHours` JSON NULL;

-- AlterTable
ALTER TABLE `themes` DROP COLUMN `genre`;

-- CreateTable
CREATE TABLE `genre` (
    `id` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `_GenreToTheme` (
    `A` VARCHAR(191) NOT NULL,
    `B` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `_GenreToTheme_AB_unique`(`A`, `B`),
    INDEX `_GenreToTheme_B_index`(`B`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `_GenreToTheme` ADD CONSTRAINT `_GenreToTheme_A_fkey` FOREIGN KEY (`A`) REFERENCES `genre`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `_GenreToTheme` ADD CONSTRAINT `_GenreToTheme_B_fkey` FOREIGN KEY (`B`) REFERENCES `themes`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
