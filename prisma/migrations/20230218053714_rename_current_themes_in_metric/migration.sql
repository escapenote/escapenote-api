/*
  Warnings:

  - You are about to drop the column `cruuentThemes` on the `metrics` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE `metrics` DROP COLUMN `cruuentThemes`,
    ADD COLUMN `currentThemes` JSON NULL;
