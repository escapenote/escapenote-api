-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `cafes` ADD COLUMN `blogReviewsCount` INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `blogReviewsCount` INTEGER NOT NULL DEFAULT 0;
