-- CreateTable
CREATE TABLE `cafe_reviews` (
    `id` VARCHAR(191) NOT NULL,
    `rating` DOUBLE NOT NULL DEFAULT 5,
    `text` TEXT NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `cafeId` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `theme_reviews` (
    `id` VARCHAR(191) NOT NULL,
    `rating` DOUBLE NOT NULL DEFAULT 5,
    `success` BOOLEAN NOT NULL DEFAULT false,
    `level` INTEGER NOT NULL DEFAULT 0,
    `fear` INTEGER NOT NULL DEFAULT 0,
    `activity` INTEGER NOT NULL DEFAULT 0,
    `text` TEXT NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `themeId` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `cafe_reviews` ADD CONSTRAINT `cafe_reviews_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `cafe_reviews` ADD CONSTRAINT `cafe_reviews_cafeId_fkey` FOREIGN KEY (`cafeId`) REFERENCES `cafes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `theme_reviews` ADD CONSTRAINT `theme_reviews_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `theme_reviews` ADD CONSTRAINT `theme_reviews_themeId_fkey` FOREIGN KEY (`themeId`) REFERENCES `themes`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;
