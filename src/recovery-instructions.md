# Hawaii Smart Energy Project Export Files

## Prerequisites
You need to be logged in to your Google account to access these files.

## File Recovery

1. Download files.

2. Concatenate parts, if necessary, using

    `cat DB.1 DB.2 DB.3 > DB.gz`

3. Gzip decompress using

    `gzip -d DB.gz`

## Database Restoration

Load data into the database.

    sudo -u postgres psql DB < DB.sql

Replace __DB__ with the appropriate database filename.

## Available Files
