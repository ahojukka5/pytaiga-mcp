# Taiga REST API Documentation

**Source**: <https://docs.taiga.io/api.html>  
**Last Updated**: 2024-04-03  
**Downloaded**: 2025-11-12

---

## Table of Contents

1. [General Notes](#1-general-notes)
2. [Endpoints Summary](#2-endpoints-summary)
3. [Auth](#3-auth)
4. [Applications](#4-applications)
5. [Application Tokens](#5-application-tokens)
6. [Resolver](#6-resolver)
7. [Searches](#7-searches)
8. [User Storage](#8-user-storage)
9. [Project Templates](#9-project-templates)
10. [Projects](#10-projects)
11. [Memberships/Invitations](#11-membershipsinvitations)
12. [Roles](#12-roles)
13. [Milestones](#13-milestones)
14. [Epics](#14-epics)
15. [Epic Status](#15-epic-status)
16. [Epic Custom Attribute](#16-epic-custom-attribute)
17. [Epic Custom Attributes Values](#17-epic-custom-attributes-values)
18. [User Stories](#18-user-stories)
19. [User Story Status](#19-user-story-status)
20. [Points](#20-points)
21. [User Story Custom Attribute](#21-user-story-custom-attribute)
22. [User Story Custom Attributes Values](#22-user-story-custom-attributes-values)
23. [Tasks](#23-tasks)
24. [Task Status](#24-task-status)
25. [Task Custom Attribute](#25-task-custom-attribute)
26. [Task Custom Attributes Values](#26-task-custom-attributes-values)
27. [Issues](#27-issues)
28. [Issue Status](#28-issue-status)
29. [Issue Types](#29-issue-types)
30. [Priorities](#30-priorities)
31. [Severities](#31-severities)
32. [Issue Custom Attribute](#32-issue-custom-attribute)
33. [Issue Custom Attributes Values](#33-issue-custom-attributes-values)
34. [Wiki Pages](#34-wiki-pages)
35. [Wiki Links](#35-wiki-links)
36. [History](#36-history)
37. [Users](#37-users)
38. [Notify Policies](#38-notify-policies)
39. [Feedback](#39-feedback)
40. [Export/Import](#40-exportimport)
41. [Webhooks](#41-webhooks)
42. [Timelines](#42-timelines)
43. [Locales](#43-locales)
44. [Stats](#44-stats)
45. [Importers](#45-importers)
46. [Contact](#46-contact)
47. [Objects Summary](#47-objects-summary)
48. [Project Templates Detail](#48-project-templates-detail)
49. [Contrib Plugins](#49-contrib-plugins)

---

## 1. GENERAL NOTES

> **About Taiga instance and URLs used in this document**  
> All API calls used in the documentation are referred to a local Taiga instance API running on `localhost:8000`, so if you use another instance remember to change the URL. For example, if you want to perform the tests against our own instance, you should use `https://api.taiga.io/api/v1` instead of `http://localhost:8000/api/v1`.

### 1.1. Authentication

#### 1.1.1. Standard token authentication

To authenticate requests an HTTP header called "Authorization" should be added. Its format should be:

```
Authorization: Bearer ${AUTH_TOKEN}
```

This token can be received through the login API.

**Example Bash script to obtain auth token:**

```bash
#!/bin/bash
# Request username and password for connecting to Taiga
read -p "Username or email: " USERNAME
read -r -s -p "Password: " PASSWORD

DATA=$(jq --null-input \
        --arg username "$USERNAME" \
        --arg password "$PASSWORD" \
        '{ type: "normal", username: $username, password: $password }')

# Get AUTH_TOKEN
USER_AUTH_DETAIL=$( curl -X POST \
  -H "Content-Type: application/json" \
  -d "$DATA" \
  https://api.taiga.io/api/v1/auth 2>/dev/null )

AUTH_TOKEN=$( echo ${USER_AUTH_DETAIL} | jq -r '.auth_token' )

# Exit if AUTH_TOKEN is not available
if [ -z ${AUTH_TOKEN} ]; then
    echo "Error: Incorrect username and/or password supplied"
    exit 1
else
    echo "auth_token is ${AUTH_TOKEN}"
fi

# Proceed to use API calls as desired
```

**Note**: This token has an expiration time so you must update it with a refresh API call.

#### 1.1.2. Application token authentication

Application tokens are designed for allowing external apps to use the Taiga API. They are associated with an existing user and an Application. The authorization header format is:

```
Authorization: Application ${AUTH_TOKEN}
```

The process consists of:

1. Checking if there is an existing application token for the requesting user
2. Requesting an authorization code if it doesn't exist yet
3. Validating the authorization code to obtain the final token
4. Deciphering the token

### 1.2. OCC - Optimistic concurrency control

In Taiga, multiple operations can be happening at the same time for an element, so every modifying request should include a valid version parameter.

- If users update the same attributes, the API will accept the first request and deny the second (invalid version).
- If users update different attributes, the API is smart enough to accept both requests since the changes don't affect modified attributes.

The version parameter is considered valid if it contains the current version for the element. It will be incremented automatically if the modification is successful.

### 1.3. Pagination

By default, the API will always return paginated results and includes the following headers:

- `x-paginated`: boolean indicating if pagination is being used
- `x-paginated-by`: number of results per page
- `x-pagination-count`: total number of results
- `x-pagination-current`: current page
- `x-pagination-next`: next results
- `x-pagination-prev`: previous results

Disabling pagination can be accomplished by setting an extra HTTP header:

```
x-disable-pagination: True
```

### 1.4. Internationalization

The API returns some content translated. You can specify the language with an extra HTTP header:

```
Accept-Language: {LanguageId}
```

The LanguageId can be chosen from the value list of available languages. You can get them using the locales API.

### 1.5. Throttling

If the API is configured with throttling, you have to take care of responses with 429 (Too many requests) status code, which means you have reached the throttling limit.

### 1.6. Read only fields

All fields ending in `_extra_info` (e.g., `assigned_to_extra_info`, `is_private_extra_info`, `owner_extra_info`, `project_extra_info`, `status_extra_info`, `user_story_extra_info`) are read-only fields.

---

## 2. ENDPOINTS SUMMARY

### 2.1. Auth

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/auth | POST | Login |
| /api/v1/auth/refresh | POST | Refresh auth token |
| /api/v1/auth/register | POST | Register user |

### 2.2. Applications

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/applications/{applicationId} | GET | Get application |
| /api/v1/applications/{applicationId}/token | GET | Get application token |

### 2.3. Application Tokens

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/application-tokens | GET | List application tokens |
| /api/v1/application-tokens/{applicationTokenId} | GET | Get application token |
| /api/v1/application-tokens/{applicationTokenId} | DELETE | Delete application token |
| /api/v1/application-tokens/authorize | POST | Authorize application token |
| /api/v1/application-tokens/validate | POST | Validate application token |

### 2.4. Resolver

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/resolver | GET | Resolve references and slugs |

### 2.5. Searches

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/search | GET | Search in a project |

### 2.6. User storage

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/user-storage | GET | List user storage data |
| /api/v1/user-storage | POST | Create user storage data |
| /api/v1/user-storage/{key} | GET | Get user storage data |
| /api/v1/user-storage/{key} | PUT | Modify user storage data |
| /api/v1/user-storage/{key} | PATCH | Modify partially user storage data |
| /api/v1/user-storage/{key} | DELETE | Delete user storage data |

### 2.7. Project templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/project-templates | GET | List project templates |
| /api/v1/project-templates | POST | Create project template |
| /api/v1/project-templates/{projectTemplateId} | GET | Get project template |
| /api/v1/project-templates/{projectTemplateId} | PUT | Modify project template |
| /api/v1/project-templates/{projectTemplateId} | PATCH | Modify partially project template |
| /api/v1/project-templates/{projectTemplateId} | DELETE | Delete project template |

### 2.8. Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/projects | GET | List projects |
| /api/v1/projects | POST | Create project |
| /api/v1/projects/{projectId} | GET | Get project |
| /api/v1/projects/by_slug?slug={projectSlug} | GET | Get project |
| /api/v1/projects/{projectId} | PUT | Modify project |
| /api/v1/projects/{projectId} | PATCH | Modify partially a project |
| /api/v1/projects/{projectId} | DELETE | Delete a project |
| /api/v1/projects/bulk_update_order | POST | Update projects order for logged in user |
| /api/v1/projects/{projectId}/modules | GET | Get project modules configuration |
| /api/v1/projects/{projectId}/modules | PATCH | Modify partially project modules configuration |
| /api/v1/projects/{projectId}/stats | GET | Get project stats |
| /api/v1/projects/{projectId}/issues_stats | GET | Get project issue stats |
| /api/v1/projects/{projectId}/tags_colors | GET | Get project tags colors |
| /api/v1/projects/{projectId}/create_tag | POST | Create project tag |
| /api/v1/projects/{projectId}/edit_tag | POST | Edit project tag |
| /api/v1/projects/{projectId}/delete_tag | POST | Delete project tag |
| /api/v1/projects/{projectId}/mix_tags | POST | Mix project tags |
| /api/v1/projects/{projectId}/like | POST | Like a project |
| /api/v1/projects/{projectId}/unlike | POST | Unlike a project |
| /api/v1/projects/{projectId}/fans | GET | Get project fans |
| /api/v1/projects/{projectId}/watch | POST | Watch a project |
| /api/v1/projects/{projectId}/unwatch | POST | Unwatch a project |
| /api/v1/projects/{projectId}/watchers | GET | Get project watchers |
| /api/v1/projects/{projectId}/create_template | POST | Create project template |
| /api/v1/projects/{projectId}/leave | POST | Leave project |
| /api/v1/projects/{projectId}/change_logo | POST | Change logo |
| /api/v1/projects/{projectId}/remove_logo | POST | Remove logo |
| /api/v1/projects/{projectId}/transfer_validate_token | POST | Transfer validate token |
| /api/v1/projects/{projectId}/transfer_request | POST | Transfer request |
| /api/v1/projects/{projectId}/transfer_start | POST | Transfer start |
| /api/v1/projects/{projectId}/transfer_accept | POST | Transfer accept |
| /api/v1/projects/{projectId}/transfer_reject | POST | Transfer reject |
| /api/v1/projects/{projectId}/duplicate | POST | Duplicate project |

### 2.9. Memberships/Invitations

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/memberships | GET | List memberships |
| /api/v1/memberships | POST | Create membership |
| /api/v1/memberships/bulk_create | POST | Create bulk memberships |
| /api/v1/memberships/{membershipId} | GET | Get membership |
| /api/v1/memberships/{membershipId} | PUT | Modify membership |
| /api/v1/memberships/{membershipId} | PATCH | Modify partially a membership |
| /api/v1/memberships/{membershipId} | DELETE | Delete a membership |
| /api/v1/memberships/{membershipId}/resend_invitation | POST | Resend invitation |
| /api/v1/invitations/{invitationUuid} | POST | Get invitation by anonymous user |

### 2.10. Roles

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/roles | GET | List roles |
| /api/v1/roles | POST | Create role |
| /api/v1/roles/{roleId} | GET | Get role |
| /api/v1/roles/{roleId} | PUT | Modify role |
| /api/v1/roles/{roleId} | PATCH | Modify partially a role |
| /api/v1/roles/{roleId} | DELETE | Delete a role |

### 2.11. Milestones

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/milestones | GET | List milestones |
| /api/v1/milestones | POST | Create milestone |
| /api/v1/milestones/{milestoneId} | GET | Get milestone |
| /api/v1/milestones/{milestoneId} | PUT | Modify milestone |
| /api/v1/milestones/{milestoneId} | PATCH | Modify partially a milestone |
| /api/v1/milestones/{milestoneId} | DELETE | Delete a milestone |
| /api/v1/milestones/{milestoneId}/stats | GET | Get milestone stats |
| /api/v1/milestones/{milestoneId}/watch | POST | Watch a milestone |
| /api/v1/milestones/{milestoneId}/unwatch | POST | Stop watching a milestone |
| /api/v1/milestones/{milestoneId}/watchers | GET | Get milestone watchers |

### 2.12. Epics

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/epics | GET | List epics |
| /api/v1/epics | POST | Create epic |
| /api/v1/epics/{epicId} | GET | Get epic |
| /api/v1/epics/by_ref?ref={epicRef}&project={projectId} | GET | Get epic |
| /api/v1/epics/{epicId} | PUT | Modify epic |
| /api/v1/epics/{epicId} | PATCH | Modify partially an epic |
| /api/v1/epics/{epicId} | DELETE | Delete an epic |
| /api/v1/epics/{epicId}/related_userstories | GET | List epic related userstories |
| /api/v1/epics/{epicId}/related_userstories | POST | Create epic related user story |
| /api/v1/epics/{epicId}/related_userstories/{userStoryId} | GET | Get epic related userstory |
| /api/v1/epics/{epicId}/related_userstories/{userStoryId} | PUT | Modify epic related user story |
| /api/v1/epics/{epicId}/related_userstories/{userStoryId} | PATCH | Modify partially epic related user story |
| /api/v1/epics/{epicId}/related_userstories/{userStoryId} | DELETE | Delete epic related user story |
| /api/v1/epics/{epicId}/related_userstories/bulk_create | POST | Create epic related user stories on bulk |
| /api/v1/epics/bulk_create | POST | Create epics on bulk mode |
| /api/v1/epics/filters_data?project={projectId} | GET | Get filters data |

### 2.16. User stories

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/userstories | GET | List user stories |
| /api/v1/userstories | POST | Create user story |
| /api/v1/userstories/{userStoryId} | GET | Get user story |
| /api/v1/userstories/by_ref?ref={userStoryRef}&project={userStoryId} | GET | Get user story |
| /api/v1/userstories/{userStoryId} | PUT | Modify user story |
| /api/v1/userstories/{userStoryId} | PATCH | Modify partially a user story |
| /api/v1/userstories/{userStoryId} | DELETE | Delete a user story |
| /api/v1/userstories/bulk_create | POST | Create user stories in bulk mode |
| /api/v1/userstories/bulk_update_backlog_order | POST | Update user stories order for backlog in bulk |

### 2.21. Tasks

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/tasks | GET | List tasks |
| /api/v1/tasks | POST | Create task |
| /api/v1/tasks/{taskId} | GET | Get task |
| /api/v1/tasks/by_ref?ref={taskRef}&project={projectId} | GET | Get task |
| /api/v1/tasks/{taskId} | PUT | Modify task |
| /api/v1/tasks/{taskId} | PATCH | Modify partially a task |
| /api/v1/tasks/{taskId} | DELETE | Delete a task |
| /api/v1/tasks/bulk_create | POST | Create tasks on bulk mode |
| /api/v1/tasks/filters_data?project={projectId} | GET | Get filters data |
| /api/v1/tasks/{taskId}/upvote | POST | Add star to a task |
| /api/v1/tasks/{taskId}/downvote | POST | Remove star from task |
| /api/v1/tasks/{taskId}/voters | GET | Get task voters |

### 2.25. Issues

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/issues | GET | List issues |
| /api/v1/issues | POST | Create issue |
| /api/v1/issues/{issueId} | GET | Get issue |
| /api/v1/issues/by_ref?ref={issueRef}&project={projectId} | GET | Get issue |
| /api/v1/issues/{issueId} | PUT | Modify issue |
| /api/v1/issues/{issueId} | PATCH | Modify partially an issue |
| /api/v1/issues/{issueId} | DELETE | Delete an issue |
| /api/v1/issues/bulk_create | POST | Create issues in bulk mode |
| /api/v1/issues/filters_data?project={projectId} | GET | Get filters data |
| /api/v1/issues/{issueId}/upvote | POST | Add vote to an issue |
| /api/v1/issues/{issueId}/downvote | POST | Remove your vote to an issue |

### 2.32. Wiki pages

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/wiki | GET | List wiki pages |
| /api/v1/wiki | POST | Create wiki page |
| /api/v1/wiki/{wikiId} | GET | Get wiki page |
| /api/v1/wiki/by_slug?slug={wikiPageSlug}&project={projectId} | GET | Get wiki page |
| /api/v1/wiki/{wikiPageId} | PUT | Modify wiki page |
| /api/v1/wiki/{wikiPageId} | PATCH | Modify partially a wiki page |
| /api/v1/wiki/{wikiPageId} | DELETE | Delete a wiki page |
| /api/v1/wiki/{wikiPageId}/watch | POST | Watch a wiki page |
| /api/v1/wiki/{wikiPageId}/unwatch | POST | Stop watching a wiki page |
| /api/v1/wiki/{wikiPageId}/watchers | GET | Get wiki page watchers |
| /api/v1/wiki/attachments | GET | List wiki page attachments |
| /api/v1/wiki/attachments | POST | Create wiki page attachments |
| /api/v1/wiki/attachments/{wikiPageAttachmentId} | GET | Get wiki page attachments |
| /api/v1/wiki/attachments/{wikiPageAttachmentId} | PUT | Modify wiki page attachments |
| /api/v1/wiki/attachments/{wikiPageAttachmentId} | PATCH | Modify partially wiki page attachments |
| /api/v1/wiki/attachments/{wikiPageAttachmentId} | DELETE | Delete wiki page attachments |

---

## 23. TASKS

### 23.1. List

To list tasks send a GET request with the following parameters:

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -s https://api.taiga.io/api/v1/tasks
```

The HTTP response is a 200 OK and the response body is a JSON list of task objects.

The results can be filtered using the following parameters:

- `project`: project id
- `milestone`: milestone id
- `user_story`: user story id
- `status`: status id
- `assigned_to`: assigned to user id
- `tags`: tags (comma-separated list)

### 23.2. Create

To create a task send a POST request with the following data:

**Required fields:**

- `project`: project id (integer)
- `subject`: subject (string)

**Optional fields:**

- `description`: description (string)
- `user_story`: user story id (integer)
- `milestone`: milestone id (integer)
- `status`: status id (integer)
- `assigned_to`: assigned to user id (integer)
- `tags`: tags (array of strings)
- `is_blocked`: is blocked (boolean)
- `blocked_note`: blocked note (string)
- `taskboard_order`: taskboard order (integer)
- `us_order`: user story order (integer)
- `external_reference`: external reference (array)

**Example:**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{
        "project": 1,
        "subject": "New task",
        "description": "Task description",
        "user_story": 5,
        "status": 1,
        "assigned_to": 3
      }' \
  -s https://api.taiga.io/api/v1/tasks
```

When the creation is successful, the HTTP response is a 201 Created and the response body is a JSON task object.

### 23.3. Get

To get a task send a GET request specifying the task id in the URL:

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -s https://api.taiga.io/api/v1/tasks/1
```

The HTTP response is a 200 OK and the response body is a JSON task object.

### 23.5. Edit

To edit a task send a PUT or a PATCH specifying the task id in the URL. In a PATCH request you just need to send the modified data, in a PUT one the whole object must be sent.

```bash
curl -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -d '{
        "subject": "Updated task subject",
        "description": "Updated description"
      }' \
  -s https://api.taiga.io/api/v1/tasks/1
```

When the edit is successful, the HTTP response is a 200 OK and the response body is a JSON task object.

### 23.6. Delete

To delete a task send a DELETE request specifying the task id in the URL:

```bash
curl -X DELETE \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -s https://api.taiga.io/api/v1/tasks/1
```

When the deletion is successful, the HTTP response is a 204 NO CONTENT with an empty body response.

---

## Key Notes for Task Operations

### Task Creation Parameters

The Taiga REST API `/api/v1/tasks` endpoint accepts the following parameters for POST requests:

**Required:**

- `project` (integer): The project ID
- `subject` (string): The task subject/title

**Optional:**

- `description` (string): Detailed description of the task
- `user_story` (integer): Link task to a user story by ID
- `milestone` (integer): Assign task to a milestone/sprint
- `status` (integer): Task status ID
- `assigned_to` (integer): User ID to assign the task to
- `tags` (array): List of tag strings
- `is_blocked` (boolean): Whether the task is blocked
- `blocked_note` (string): Note explaining why task is blocked
- `taskboard_order` (integer): Order on taskboard
- `us_order` (integer): Order within user story
- `external_reference` (array): External references

### Task Modification

Both PUT and PATCH methods are supported for task updates:

- **PATCH**: Send only the fields you want to modify
- **PUT**: Send the complete task object

Include the `version` parameter for optimistic concurrency control to prevent conflicting updates.

---

## Additional Resources

- **Official Taiga API Documentation**: <https://docs.taiga.io/api.html>
- **Taiga Community**: <https://community.taiga.io/>
- **Taiga GitHub**: <https://github.com/taigaio>

---

**Note**: This is a simplified version of the full API documentation. For complete details on all endpoints, object structures, and advanced features, refer to the original documentation at <https://docs.taiga.io/api.html>
