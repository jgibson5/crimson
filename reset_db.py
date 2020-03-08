from app import models, db

if __name__ == '__main__':
    models.User.query.delete()
    models.ItemList.query.delete()
    models.LockedItemList.query.delete()
    models.UserRoles.query.delete()
    models.ItemRank.query.delete()
    models.LockedItemRank.query.delete()
    models.ItemRankAudit.query.delete()

    db.session.commit()

