-- AlterTable
ALTER TABLE `cafes` ADD COLUMN `view` INTEGER NOT NULL DEFAULT 0,
    MODIFY `intro` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `view` INTEGER NOT NULL DEFAULT 0;