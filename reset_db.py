from app import models, db

if __name__ == '__main__':
    models.ItemRankAudit.query.delete()
    models.ItemRank.query.delete()
    models.LockedItemRank.query.delete()
    models.User.query.delete()
    models.ItemList.query.delete()
    models.LockedItemList.query.delete()
    models.UserRoles.query.delete()
    models.Item.query.delete()

    db.session.commit()

