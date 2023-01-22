from prisma import models


class User(models.User, warn_subclass=False):
    pass
