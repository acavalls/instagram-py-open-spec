# social Specification

## Purpose

Lets users connect with each other: follow and unfollow, see a feed built
from the users they follow, discover accounts through suggestions, visit
profile pages with public stats, and browse who someone follows. It owns
the follow relationship and feed aggregation; stories build on it later.

## Requirements

### Requirement: Follow relationship data
The system SHALL store a follow relationship with a UUID identifier, a
follower, a followed user and a creation timestamp. A (follower, following)
pair MUST be unique and a user MUST NOT follow themselves.

#### Scenario: Follow persisted
- **WHEN** a user follows another user
- **THEN** the system stores the relationship with a UUID identifier and a creation timestamp

#### Scenario: Self-follow rejected
- **WHEN** a user attempts to follow themselves
- **THEN** the system rejects it with the error "You cannot follow yourself"

#### Scenario: Duplicate follow rejected
- **WHEN** a user attempts to follow a user they already follow
- **THEN** the system rejects it with the error "Already following this user"

### Requirement: Follow and unfollow actions
The system SHALL allow a logged-in user to follow and unfollow any other
user through the web UI via an HTMX button that toggles in place and
confirms with a toast.

#### Scenario: Web follow via HTMX
- **WHEN** a logged-in user clicks the follow button on a profile
- **THEN** the button toggles to the following state and the toast "Followed successfully" is shown

#### Scenario: Web unfollow via HTMX
- **WHEN** a logged-in user clicks the following button
- **THEN** the button toggles back to the follow state and the toast "Unfollowed successfully" is shown

#### Scenario: Web follow failure shows the cause
- **WHEN** a follow or unfollow action fails (self-follow, duplicate, or unknown relationship)
- **THEN** the button keeps its current state and an error toast shows the failure reason

### Requirement: Followed-users feed
The system SHALL show a logged-in user a home feed of posts from the users
they follow, ordered newest first and loaded through HTMX infinite scroll.
When the user follows nobody, the feed SHALL show an empty state inviting
them to share their first photo. When the user follows people but none of
them has posts, the feed SHALL show a secondary empty state instead of post
cards.

#### Scenario: Feed shows followed users' posts
- **WHEN** a logged-in user visits the home page
- **THEN** the system shows post cards of the users they follow, newest first

#### Scenario: Feed ordered newest first with pagination
- **WHEN** the feed has more posts than the page size
- **THEN** the system loads the remaining posts page by page through the infinite scroll sentinel

#### Scenario: Empty feed state
- **WHEN** a logged-in user with no follows and no followed posts visits the home page
- **THEN** the system shows an empty feed state with an icon, the title "Share Photos", a subtitle and a call to action

#### Scenario: Feed with follows but no posts shows the secondary empty state
- **WHEN** a logged-in user with follows but no followed posts visits the home page
- **THEN** the system shows the secondary empty state "No posts yet" instead of post cards

### Requirement: User suggestions
The home feed sidebar SHALL suggest up to five users to follow, excluding
the logged-in user and everyone they already follow, preferring the newest
accounts. Each suggestion SHALL show the avatar, the username and a follow
button. The sidebar SHALL also render a current-user block for the logged-in
user and a footer with the links About, Help, API, Privacy, Terms and a
copyright line. When no candidates exist the panel SHALL show a
"No suggestions available." message.

#### Scenario: Suggestions exclude followed users and self
- **WHEN** the sidebar renders suggestions
- **THEN** the logged-in user and their follows do not appear among the suggestions

#### Scenario: Suggestions limited to newest accounts
- **WHEN** more candidates than the limit exist
- **THEN** the system shows only the five newest accounts

#### Scenario: Suggestion rows show avatar and follow button
- **WHEN** the sidebar renders a suggestion
- **THEN** the row shows the suggested user's avatar, their username and a follow button

#### Scenario: Sidebar renders the current-user block and footer
- **WHEN** the home feed sidebar renders
- **THEN** it shows the current-user block and the footer links About, Help, API, Privacy, Terms with a copyright line

#### Scenario: No candidates shows the empty message
- **WHEN** the sidebar renders suggestions and no candidates exist
- **THEN** the panel shows the "No suggestions available." message

### Requirement: User profile page
The system SHALL show a profile page for every user at
`/web/profile/<uuid>/` with their posts newest first, loaded through HTMX
infinite scroll, and counters of posts, followers and following. An unknown
identifier MUST respond 404. On their own profile the owner sees the edit and
delete controls on their posts; on other profiles the visitor sees the follow
button reflecting the current relationship. The sidebar (defined in the
web-ui capability) SHALL link to the logged-in user's own profile page. A
profile without posts SHALL show an empty grid message instead of grid items.

#### Scenario: Own profile shows stats and editable grid
- **WHEN** a user visits their own profile page
- **THEN** the system shows their posts, followers and following counters, with edit and delete controls on their own posts

#### Scenario: Other user profile shows stats and follow state
- **WHEN** a user visits another user's profile page
- **THEN** the system shows the profile's posts and counters and a follow button reflecting whether the visitor already follows them

#### Scenario: Unknown profile responds 404
- **WHEN** a client requests the profile page of a non-existent user
- **THEN** the system responds 404

#### Scenario: Topbar links to own profile
- **WHEN** a logged-in user views any authenticated web page
- **THEN** the sidebar shows a Profile link pointing to their own profile page

#### Scenario: Profile grid loads more posts on scroll
- **WHEN** the browser reaches the profile grid sentinel and requests the next page with the HTMX header
- **THEN** the system responds with only the next window of grid items plus the next sentinel (or the end marker), without the page shell

#### Scenario: Profile grid without posts shows an empty message
- **WHEN** a user visits the profile page of a user with no posts
- **THEN** the system shows an empty grid message instead of grid items

### Requirement: Following list
A profile SHALL offer a modal listing the users that profile follows,
searchable by username or name.

#### Scenario: Following list shows followed users
- **WHEN** a visitor opens the following list of a profile
- **THEN** the system shows the users that profile follows

#### Scenario: Following list search filters
- **WHEN** a visitor types a query in the following list search
- **THEN** the system shows only the followed users whose username or name matches the query
