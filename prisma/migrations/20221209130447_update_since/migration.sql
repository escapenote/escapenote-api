/*
  Warnings:

  - You are about to alter the column `since` on the `cafes` table. The data in that column could be lost. The data in that column will be cast from `VarChar(191)` to `DateTime(3)`.

*/
-- AlterTable
ALTER TABLE `cafes` MODIFY `since` DATETIME(3) NULL;
