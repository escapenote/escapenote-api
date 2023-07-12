-- AlterTable
ALTER TABLE `blog_reviews` MODIFY `url` VARCHAR(300) NOT NULL;

-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';
