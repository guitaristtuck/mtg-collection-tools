# Archidekt API Notes

## Log In
POST https://archidekt.com/api/rest-auth/login/
payload:
```
{
  "username": "guitaristtuck",
  "password": "xxxxxx"
}
```

response:
```
{
  "access_token": "xxxx",
  "refresh_token": "xxxx",
  "user": {
    "id": 243732,
    "username": "guitaristtuck",
    "first_name": "",
    "last_name": "",
    "decks": [
      {
        "name": "api testing deck",
        "id": 13166484,
        "private": true,
        "featured": "",
        "customFeatured": "",
        "viewCount": 1
      },
      {
        "name": "Cuddly Cacti V2",
        "id": 12758195,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/otj/52eef0d6-24b7-40b7-8403-e8e863d0cd55_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 104
      },
      {
        "name": "Big Bonk Counters - V2",
        "id": 8611180,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/mic/bd7e1645-ea8f-41c4-b3ee-58f44fc5c574_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 124
      },
      {
        "name": "Cuddly Cacti",
        "id": 9785697,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/otj/52eef0d6-24b7-40b7-8403-e8e863d0cd55_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 159
      },
      {
        "name": "Tatyova testing",
        "id": 12581759,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/dsc/13a902f7-2711-4769-9866-762195c3d0fb_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 53
      },
      {
        "name": "Captain Sharkman",
        "id": 11761074,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/dft/0957c90f-e10d-40f8-a4be-9e9ef623dd43_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 162
      },
      {
        "name": "Captain Sharkman (commander mechanic example)",
        "id": 11761031,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/dft/0957c90f-e10d-40f8-a4be-9e9ef623dd43_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 39
      },
      {
        "name": "I drink your milkshake",
        "id": 10754829,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/blb/97e0d6ca-eed9-4b57-a34a-0105c41b20b9_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 80
      },
      {
        "name": "I steal all your good cards",
        "id": 10754754,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/otc/03a7e79f-625a-49ac-9cb1-e1fe5f51f5a0_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 24
      },
      {
        "name": "I'll be back",
        "id": 10754647,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/fdn/51710b19-68e3-4853-901f-e618bde61161_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 37
      },
      {
        "name": "Eat hamster bitch (Oathbreaker)",
        "id": 10422576,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/clb/928036c9-11b8-493e-b9f2-8fbd3487cd19_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 79
      },
      {
        "name": "More Pain, More Cards V2",
        "id": 8623566,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/dmc/af0db1d6-5cb1-4917-8e8f-69d5dc184404_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 62
      },
      {eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MDg4NzczMCwiaWF0IjoxNzQ3NDMxNzMwLCJqdGkiOiJjODQ1Mjg3NjZmOGQ0ZDQwYjAwYjJjZjdkMTg4NzIwYyIsInVzZXJfaWQiOjI0MzczMn0.3AEUd1YCrtCaOxxd1y0BcgSGhH7PhKmwRtlJnEAkkRIrd-images/dmc/af0db1d6-5cb1-4917-8e8f-69d5dc184404_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 236
      },
      {
        "name": "I am once again asking for you to feel the Bern",
        "id": 8611097,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/who/da1838aa-591f-4694-b772-beaab94587c3_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 60
      },
      {
        "name": "Super Gift Deck",
        "id": 8530989,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/c16/97fa8615-2b6c-445a-bcaf-44a7e847bf65_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 42
      },
      {
        "name": "Big Bonk Counters",
        "id": 8517427,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/mic/bd7e1645-ea8f-41c4-b3ee-58f44fc5c574_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 34
      },
      {
        "name": "Eat hamster, bitch",
        "id": 8195249,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/clb/928036c9-11b8-493e-b9f2-8fbd3487cd19_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 40
      },
      {
        "name": "Attack of the Simpletons",
        "id": 7686016,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/c21/e07b8142-6a49-46e7-b862-41f89a59b894_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 136
      },
      {
        "name": "Change Places!",
        "id": 7685918,
        "private": false,
        "featured": "https://storage.googleapis.com/archidekt-card-images/jmp/b238485f-ef67-4295-892b-a10235368f74_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 126
      },
      {
        "name": "Copy of - Buffs by Hans",
        "id": 7701767,
        "private": true,
        "featured": "https://storage.googleapis.com/archidekt-card-images/dmc/af0db1d6-5cb1-4917-8e8f-69d5dc184404_art_crop.jpg",
        "customFeatured": "",
        "viewCount": 1
      }
    ],
    "profile": {
      "birth_date": null,
      "bio": "",
      "location": "United States",eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MDg4NzczMCwiaWF0IjoxNzQ3NDMxNzMwLCJqdGkiOiJjODQ1Mjg3NjZmOGQ0ZDQwYjAwYjJjZjdkMTg4NzIwYyIsInVzZXJfaWQiOjI0MzczMn0.3AEUd1YCrtCaOxxd1y0BcgSGhH7PhKmwRtlJnEAkkRI
      "is_collection_public": true,
      "contactable": false,
      "newsletterable": false,
      "comment_notification_emailable": true
    },
    "notificationCount": 2,
    "uniqueId": "4e1d48e303a65da7cd892ce16ee695a79c6e12ed25557f1c0d82a93e4dbe9b67",
    "patreonAccount": null,
    "accountSettings": {
      "id": 243720,
      "siteKeybinds": 0,
      "siteTheme": 1,
      "deckView": 0,
      "deckStack": 0,
      "deckPrice": 1,
      "deckPrices": [
        1,
        2
      ],
      "deckSorting": 0,
      "deckToolbar": 2,
      "deckLocking": 1,
      "searchUnique": 1,
      "searchGame": 1,
      "searchView": 0,
      "searchWidth": 2,
      "collectionPrice": 1,
      "collectionGame": 1,
      "collectionFlags": 0,
      "noArchidektNotifications": false,
      "noUseDefaultCategories": true,
      "user": 243732
    },
    "rootFolder": 346306
  },
  "token": "xxxxx"
}
```

## Create Folder
POST https://archidekt.com/api/decks/folders/
payload:
```
{
  "name":"testing 123",
  "private":true,
  "parentFolder":"98377"
}
```
response:
```
{
  "id":969047,
  "name":"somedeck",
  "parentFolder":346306,
  "private":true
}
```

## List Folders
GET https://archidekt.com/api/decks/folders/{rootFolder}/
rootFolder: get from login
response:
```
{
  "id": 346306,
  "name": "Home",
  "parentFolder": null,
  "private": false,
  "owner": {
    "id": 243732,
    "username": "guitaristtuck",
    "avatar": "https://storage.googleapis.com/topdekt-user/avatars/default/avatar_colorless.svg"
  },
  "subfolders": [
    {
      "id": 800219,
      "name": "Archive",
      "createdAt": "2025-01-05T16:34:47.468000Z",
      "private": false
    },
    {
      "id": 800218,
      "name": "Currently Built",
      "createdAt": "2025-01-05T16:33:24.165272Z",
      "private": false
    },
    {
      "id": 800220,
      "name": "New Ideas",
      "createdAt": "2025-01-05T16:35:00.583042Z",
      "private": false
    }
  ],
  "decks": [
    {
      "id": 12758195,
      "name": "Cuddly Cacti V2",
      "updatedAt": "2025-04-28T19:17:24.136563Z",
      "createdAt": "2025-04-26T15:34:19.112974Z",
      "deckFormat": 3,
      "edhBracket": null,
      "featured": "https://storage.googleapis.com/archidekt-card-images/otj/52eef0d6-24b7-40b7-8403-e8e863d0cd55_art_crop.jpg",
      "customFeatured": "",
      "viewCount": 104,
      "private": false,
      "unlisted": false,
      "theorycrafted": false,
      "game": null,
      "hasDescription": false,
      "tags": [],
      "parentFolderId": 346306,
      "owner": {
        "id": 243732,
        "username": "guitaristtuck",
        "avatar": "https://storage.googleapis.com/topdekt-user/avatars/default/avatar_colorless.svg",
        "moderator": false,
        "pledgeLevel": null,
        "roles": []
      },
      "colors": {
        "W": 0,
        "U": 0,
        "B": 0,
        "R": 0,
        "G": 54
      },
      "cardPackage": null
    }
  ],
  "count": 1,
  "next": null
}
```

## Create Deck
POST https://archidekt.com/api/decks/v2/
payload:
```
{
  "name": "api testing deck",
  "deckFormat": 3,
  "edhBracket": null,
  "description": "",
  "featured": "",
  "playmat": "",
  "private": true,
  "unlisted": true,
  "theorycrafted": false,
  "game": 1,
  "parent_folder": 346306,
  "cardPackage": null,
  "extras": {
    "decksToInclude": [],
    "commandersToAdd": [],
    "forceCardsToSingleton": false,
    "ignoreCardsOutOfCommanderIdentity": true
  }
}
```
response:
201
```
{
    "owner": {
        "id": 243732,
        "username": "guitaristtuck",
        "avatar": "https://storage.googleapis.com/topdekt-user/avatars/default/avatar_colorless.svg",
        "moderator": false,
        "pledgeLevel": null,
        "roles": []
    },
    "name": "api testing deck",
    "updatedAt": "2025-05-16T04:50:32.219205Z",
    "deckFormat": 3,
    "edhBracket": null,
    "id": 13166484,
    "colors": {
        "W": 0,
        "U": 0,
        "B": 0,
        "R": 0,
        "G": 0
    },
    "featured": "",
    "customFeatured": "",
    "viewCount": 0,
    "private": true,
    "tags": [],
    "cardPackage": null,
    "unlisted": true,
    "theorycrafted": false,
    "game": 1
}
```
