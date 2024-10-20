# Pack:
- name: Name of game system what showing for users
- codename: Code name of game system
- image-name: preview of system what showing for users
- type: Can be "game-system", "addon", "resource", "adventure"
- reference: Used for "addon" and "adventure" to assign to parent system
- owner: User who create this system
- redactors: List of user who can change or create content in this system


# Table:
- name: Name of table. Used for show in game view.
- codename: Used for navigate and agreagate.
- owner: User who create the table
- type: Can be only "table"
- reference: Has a codename of reference package. Can take codenames of game-systems or addons.
- reference-type: Type of reference pack. game-system or addon.
- common
    - search-fields: Array of strings. Show what fields used for search. Example: ["name", "damage", "description"]
    - short-view: Dictionary of parametres what means how to show it for users. {"alignment": "vertical", "fields": ["image", "name"]}
    - table-icon: String with name of icon
    - table-display: This settings set up how to show notes in main view. Can be only "list" or "table"
- params
    - properties: Dictionary of strings using for create properties with formatting.
    - macros: Dictionary of macroses.
    - schema: Tree with codenames. Using for formatting note
    - table-fields: Array with fields and his settings


# Image:
- name: Name what shows for users
- codename: Codename used for search and link images
- owner: User who upload this image
- schema: For composite pictures


# User:
## User document schema

- username: Nickname
- password-hash: Hash of password what user for check login 
- rights: List of accesses
- blocked: String with date after user can sign in
- waiting
    - registration: System wait when user register new account with this login
    - approval: System wait when admin or server-admin approve this registration
- relationship
    - black-list: List of users who can't write for this user

## User rights
### Content rights

- any-create      | This access using as all create rights

- create-pack     |
- create-table    | 
- create-note     |
- create-resource | All create access also gain access for delete created content
- create-addon    |
- create-world    |
- create-games    |

- any-delete      | This access using as all delete rights

- delete-pack     |
- delete-table    | 
- delete-note     |
- delete-resource | This accesses need only for delete someone else's content
- delete-addon    |
- delete-world    |
- delete-games    |

### Accounts rights
- any-account
- approve-requests
- add-to-queue
- delete-user
- ban-user

### Can have only server admin
- server-admin          | Any rights
- cant-be-blocked


# Message:
- text: Text of message what using for showing
- from: Who send with message
- to: Where was the message sent
- time: Dispatch time