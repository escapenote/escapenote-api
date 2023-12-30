-- CreateTable
CREATE TABLE `monitoring` (
    `id` VARCHAR(191) NOT NULL,
    `scrapperId` VARCHAR(191) NULL,
    `cruuentThemes` JSON NULL,
    `scrappedThemes` JSON NULL,
    `differentThemes` JSON NULL,
    `status` ENUM('SOMETHING_WRONG', 'NOTHING_WRONG') NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `monitoring_scrapperId_key`(`scrapperId`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `monitoring` ADD CONSTRAINT `monitoring_scrapperId_fkey` FOREIGN KEY (`scrapperId`) REFERENCES `scrappers`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;
