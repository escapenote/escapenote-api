/*
  Warnings:

  - You are about to drop the column `since` on the `cafes` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE `cafes` DROP COLUMN `since`;

-- AlterTable
ALTER TABLE `themes` ADD COLUMN `openDate` VARCHAR(191) NOT NULL DEFAULT '';
