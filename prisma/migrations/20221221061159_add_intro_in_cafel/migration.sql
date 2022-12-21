/*
  Warnings:

  - Made the column `images` on table `cafes` required. This step will fail if there are existing NULL values in that column.
  - Made the column `openingHours` on table `cafes` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE `cafes` ADD COLUMN `intro` TEXT NOT NULL DEFAULT '',
    MODIFY `images` JSON NOT NULL,
    MODIFY `openingHours` JSON NOT NULL;
