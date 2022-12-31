-- AlterTable
ALTER TABLE `cafes` MODIFY `intro` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `activity` INTEGER NOT NULL DEFAULT 0;
