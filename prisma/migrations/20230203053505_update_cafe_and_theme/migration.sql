-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `cafes` ADD COLUMN `reviewsCount` INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN `reviewsRating` DOUBLE NOT NULL DEFAULT 0.0;

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `reviewsActivity` DOUBLE NOT NULL DEFAULT 0.0,
    ADD COLUMN `reviewsCount` INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN `reviewsFear` DOUBLE NOT NULL DEFAULT 0.0,
    ADD COLUMN `reviewsLevel` DOUBLE NOT NULL DEFAULT 0.0,
    ADD COLUMN `reviewsRating` DOUBLE NOT NULL DEFAULT 0.0;