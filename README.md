### Readme
---

#### Description 
Virtual table for tabletop rpgs

#### Feauters roadmap for MVP
- [x] Auth and registration
- [x] Creating game systems
- [ ] Creating categories for game systems
- [ ] Creating notes by categories
- [ ] Creating games
- [ ] Starting games
- [ ] Full warkable game server
- [ ] Saving statea of game servers

#### Description for elementa of roadmap
- Auth and registration
Registration and authorization:
   - Users can register and log in using their login and password through API endpoints.
   - Upon successful login, users receive an authentication token.
   - The token is used as the primary means of user authentication for all API methods.
Registration methods:
   - "allowed": Anyone can register.
   - "forbidden": Only an administrator can register users.
   - "on_request": Users can submit a registration request that must be approved by an administrator.
MVP will only support the first two registration methods.
