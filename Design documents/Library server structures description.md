Package:
- name: Name of game system what showing for users
- codename: Code name of game system
- image-name: preview of system what showing for users
- type: Can be "game-system", "addon", "resource", "adventure"
- reference: Used for "addon" and "adventure" to assign to parent system
- owner: User who create this system
- redactors: List of user who can change or create content in this system


Table:
- name
- codename
- owner
- type
- reference
- table
    - search-fields
    - short-view
    - table-icon
    - table-display
    - properties
    - macros
    - schema
    - table-fields


Image:
- name: Name what shows for users
- codename: Codename used for search and link images
- owner: User who upload this image
- schema: For composite pictures


User:
- username: Nickname
- password-hash: Hash of password what user for check login 
- role: Basic role for get info abour what user can do
- waiting
    - registration: System wait when user register new account with this login
    - approval: System wait when admin or server-admin approve this registration
- relationship
    - black-list: List of users who can't write for this user


Message:
- text: Text of message what using for showing
- from: Who send with message
- to: Where was the message sent
- time: Dispatch time