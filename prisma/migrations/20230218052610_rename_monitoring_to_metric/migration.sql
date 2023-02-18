/*
  Warnings:

  - You are about to drop the `monitoring` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE `monitoring` DROP FOREIGN KEY `monitoring_scrapperId_fkey`;

-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- DropTable
DROP TABLE `monitoring`;

-- CreateTable
CREATE TABLE `metrics` (
    `id` VARCHAR(191) NOT NULL,
    `scrapperId` VARCHAR(191) NULL,
    `cruuentThemes` JSON NULL,
    `scrappedThemes` JSON NULL,
    `differentThemes` JSON NULL,
    `status` ENUM('SOMETHING_WRONG', 'NOTHING_WRONG') NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `metrics_scrapperId_key`(`scrapperId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `metrics` ADD CONSTRAINT `metrics_scrapperId_fkey` FOREIGN KEY (`scrapperId`) REFERENCES `scrappers`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;
