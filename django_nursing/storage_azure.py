from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'bmsnursingcollege' # <storage_account_name>
    account_key = 'JHo6QkJ2X//upvMQ2C2a8CK0YjQCrZUXgcCPtDA78BQ93sx80q+ngeBLuv+ox3PJlq3Q8QD8FVWA+AStWYfoYQ==' # <storage_account_key>
    azure_container = 'media'
    expiration_secs = 600

class AzureStaticStorage(AzureStorage):
    account_name = 'bmsnursingcollege' # <storage_account_name>
    account_key = 'JHo6QkJ2X//upvMQ2C2a8CK0YjQCrZUXgcCPtDA78BQ93sx80q+ngeBLuv+ox3PJlq3Q8QD8FVWA+AStWYfoYQ==' # <storage_account_key>
    azure_container = 'static'
    expiration_secs = None