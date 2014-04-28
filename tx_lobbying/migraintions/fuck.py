# Trick Django into thinking this app uses old South migrations. The hack in the
# [discussion] no longer works, so I'm doing this shit instead. If I try the
# hack, I get:
#
#     django.db.migrations.loader.BadMigrationError: Migration views in app tx_lobbying.migraintaions has no Migration class
#
# [discussion]: https://groups.google.com/forum/#!topic/django-developers/PWPj3etj3-U
raise ImportError('south')
