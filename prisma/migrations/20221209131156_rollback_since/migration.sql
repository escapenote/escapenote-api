/*
  Warnings:

  - Made the column `since` on table `cafes` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE `cafes` MODIFY `since` VARCHAR(191) NOT NULL DEFAULT '';
