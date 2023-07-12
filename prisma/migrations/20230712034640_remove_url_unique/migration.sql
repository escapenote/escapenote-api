-- DropIndex
DROP INDEX `blog_reviews_url_key` ON `blog_reviews`;

-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';
