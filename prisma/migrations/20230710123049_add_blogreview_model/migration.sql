-- CreateTable
CREATE TABLE `blog_reviews` (
    `id` VARCHAR(191) NOT NULL,
    `cafeId` VARCHAR(191) NULL,
    `themeId` VARCHAR(191) NULL,
    `title` VARCHAR(191) NOT NULL,
    `desc` VARCHAR(300) NOT NULL DEFAULT '',
    `url` VARCHAR(191) NOT NULL,
    `thumbnail` VARCHAR(191) NOT NULL DEFAULT '',
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `blog_reviews_url_key`(`url`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `blog_reviews` ADD CONSTRAINT `blog_reviews_cafeId_fkey` FOREIGN KEY (`cafeId`) REFERENCES `cafes`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `blog_reviews` ADD CONSTRAINT `blog_reviews_themeId_fkey` FOREIGN KEY (`themeId`) REFERENCES `themes`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;
