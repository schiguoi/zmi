## Zendesk KB Migration Tools

The tools migrate knowledge base content from one Zendesk Help Center to another. The migrated content include articles, comments, votes, and subscriptions. It doesn't support migrating community content.

The tools add and update the content incrementally based on the timestamp of the last sync.

**Limitation**: The tools don't migrate non-inline attachments or rewrite links to attachments in articles.

### Terms of use

This project is a private open-source project. It's not supported by Zendesk in any way. See the [license](https://github.com/chucknado/zmi/blob/master/LICENSE) for the terms of use.


### Requirements

- [Python 3.6 or higher](https://www.python.org/)
- [requests](http://docs.python-requests.org/en/master/)
- [arrow](https://arrow.readthedocs.io/en/latest/)

### Set up

1. Manually create matching categories and sections in the destination KB.

	If the articles have translations, make sure to create matching category and section translations in the destination KB.

2. In **/data/section_map.json**, define a dictionary of section ids from the source KB and their corresponding ids in the destination KB. The sections can be in any category. The map is used for migrating the articles to the correct sections in the destination KB.

	```
	{
      "115002917448": 360000007167,
      "206223848": 360000007068,
      ...
    }
	```
3. In **/data/user_segment_map.json** define a dictionary of user segment ids from the source KB and their corresponding ids in the destination KB.  Articles visible to everyone don't have a user segment, add `"None": null` to account for this. When migrating articles within the same instance this is optional.

	```
	{
      "None": null,
      "115002917448": 360000007167,
      "206223848": 360000007068,
      ...
    }
	```

4. In **/data/permission_group_map.json** define a dictionary of permissiong group ids from the source KB and their corresponding ids in the destination KB. This is optional if migrating to another brand in the same instance.

5. Create a general "Team" user in the target Help Center and make the user an agent. You'll assign the user id to in the **settings.ini** file.

	Articles in HC can't be authored by end users. If an author leaves the company, they're demoted to end user in Zendesk. Trying to recreate the article elsewhere with the same author causes an error.

6. Specify all the values in the **settings.ini** file.

	```
	[DEFAULT]
    cross_instance=True
    src_kb=acme
    dst_kb=bravo
    locale=en-us
    team_user=13589481088
    notify_articles=False
	```

7. Create an **auth.ini** file at the same level as the settings.ini file with your Zendesk subdomain, username and API token:

	```
	[SRC]
    kb=acme
    username=email@example.com
    token=apitoken

    [DST]
    kb=bravo
    username=email@example.com
    token=apitoken
	```

### Initial sync

Run the following scripts in order. You can perform this procedure as many times are needed on any schedule. 

**Note**: Don't sync the subscriptions until after the HC goes live and the content has been synced the final time. Because users are notified when somebody adds an article to a section or adds a comment to an article, syncing the subscriptions before a content sync could be a bad experience for users.

1. In your command-line interface, navigate to the **zmi** folder.

2. Run `$ python3 sync_articles.py`.

3. Run `$ python3 sync_comments_articles.py`.

4. Run the following scripts in any order:
    - `$ python3 sync_votes_articles.py`
    - `$ python3 sync_votes_comments.py`


### Final sync

1. Run the regular sync scripts one last time.

2. Move any article translations by running:
    - `$ python3 move_translations.py`

3. Activate the destination Help Center.

4. Run the subscription scripts:
    - `$ python3 sync_subscriptions_sections.py`
    - `$ python3 sync_subscriptions_articles.py`

5. Add the ids in **/data/js_redirect.txt** to the DOC REDIRECTS function in the **script.js** file in the source HC theme.

    See **redirect_script.js** in the source files of this project for an example of the script.

6. Run `$ python3 delete_articles.py`.

    Articles must be deleted, not just restricted by user segment, to be able to redirect from the 404 page. Deleted articles in HC are soft deleted and can be restored.

Don't make any more syncs after the syncing the subscriptions.


### Post migration

Update any external links to the moved content.

If a source section is now empty, you can delete it. If you decide to delete it, you can set up a redirect to the new section.

**To add redirects to the section landing page**

1. Add the source and destination section ids to the DOC REDIRECTS function in the **script.js** file in the source HC theme.

	See **redirect_script.js** in the source files of this project for an example of the script.

2. Manually delete the source section.
