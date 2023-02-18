/*
  Warnings:

  - You are about to drop the column `cruuentThemes` on the `metrics` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE `cafe_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `metrics` DROP COLUMN `cruuentThemes`,
    ADD COLUMN `currentThemes` JSON NULL;

-- AlterTable
ALTER TABLE `theme_reviews` MODIFY `text` TEXT NOT NULL DEFAULT '';
