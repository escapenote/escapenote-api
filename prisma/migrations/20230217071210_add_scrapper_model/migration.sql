-- AlterTable
ALTER TABLE `cafes` MODIFY `status` ENUM('PROCESSING', 'PUBLISHED', 'DELETED') NOT NULL DEFAULT 'PROCESSING';

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `displayName` VARCHAR(191) NOT NULL DEFAULT '',
    MODIFY `status` ENUM('PROCESSING', 'PUBLISHED', 'DELETED') NOT NULL DEFAULT 'PROCESSING';

-- CreateTable
CREATE TABLE `scrappers` (
    `id` VARCHAR(191) NOT NULL,
    `url` VARCHAR(191) NOT NULL,
    `comment` VARCHAR(191) NOT NULL DEFAULT '',
    `cafeId` VARCHAR(191) NULL,
    `groupSelector` VARCHAR(191) NOT NULL DEFAULT '',
    `themeSelector` VARCHAR(191) NOT NULL DEFAULT '',
    `themePostProcessing` VARCHAR(191) NOT NULL DEFAULT '',
    `branchSelector` VARCHAR(191) NOT NULL DEFAULT '',
    `branchPostProcessing` VARCHAR(191) NOT NULL DEFAULT '',
    `status` ENUM('PROCESSING', 'PUBLISHED', 'DELETED') NOT NULL DEFAULT 'PROCESSING',
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `scrappers_cafeId_key`(`cafeId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `scrappers` ADD CONSTRAINT `scrappers_cafeId_fkey` FOREIGN KEY (`cafeId`) REFERENCES `cafes`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;
