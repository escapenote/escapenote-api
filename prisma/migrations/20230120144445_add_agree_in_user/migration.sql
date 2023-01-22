-- AlterTable
ALTER TABLE `cafes` MODIFY `intro` TEXT NOT NULL DEFAULT '';

-- AlterTable
ALTER TABLE `users` ADD COLUMN `agreeMarketing` BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN `agreeOlder14Years` BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN `agreePrivacy` BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN `agreeTerms` BOOLEAN NOT NULL DEFAULT false;
