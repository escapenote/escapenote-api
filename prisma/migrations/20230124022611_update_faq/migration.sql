-- AlterTable
ALTER TABLE `faq` ADD COLUMN `position` INTEGER NOT NULL DEFAULT 0,
    MODIFY `answer` TEXT NULL;
