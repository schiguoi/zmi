import arrow

from helpers import read_data, write_data, get_settings, package_article, verify_author, write_js_redirects
import api

settings = get_settings()
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['articles'])
section_map = read_data('section_map')
article_map = read_data('article_map')
user_segment_map = read_data('user_segment_map')
permission_group_map = read_data('permission_group_map')
exceptions = read_data('exceptions')

for section in section_map:
    # # test-only section (ref docs) -> comment out for sync
    # if section != "206223768":
    #     continue
    dst_section = section_map[section]
    print('\nGetting articles in section {}...'.format(section))
    url = '{}/{}/sections/{}/articles.json'.format(settings['src_root'], settings['locale'], section)
    articles = api.get_resource_list(url)
    for src_article in articles:
        if settings['cross_instance']:
            dst_user_segment = user_segment_map[str(src_article['user_segment_id'])]
            dst_permission_group = permission_group_map[str(src_article['permission_group_id'])]
            src_article['user_segment_id'] = dst_user_segment
            src_article['permission_group_id'] = dst_permission_group
        if str(src_article['id']) in exceptions:
            print('{} is an exception. Skipping...'.format(src_article['id']))
            continue
        if last_sync < arrow.get(src_article['created_at']):
            print('- adding article {} to destination section {}'.format(src_article['id'], dst_section))
            src_article['author_id'] = verify_author(src_article['author_id'], settings['team_user'], settings['dst_kb'], settings['cross_instance'])
            url = '{}/{}/sections/{}/articles.json'.format(settings['dst_root'], settings['locale'], dst_section)
            payload = package_article(src_article, notify=settings['notify_articles'])
            new_article = api.post_resource(url, payload)
            if new_article is False:
                print('Skipping article {}'.format(src_article['id']))
                continue
            article_map[str(src_article['id'])] = new_article['id']
            continue
        if last_sync < arrow.get(src_article['edited_at']):
            print('- updating article {} in destination section {}'.format(src_article['id'], dst_section))
            dst_article = article_map[str(src_article['id'])]
            url = '{}/articles/{}/translations/{}.json'.format(settings['dst_root'], dst_article, settings['locale'])
            payload = package_article(src_article, put=True)
            response = api.put_resource(url, payload)
            if response is False:
                print('Skipping article {}'.format(src_article['id']))
            continue
        print('- article {} is up-to-date in destination section {}'.format(src_article['id'], dst_section))

utc = arrow.utcnow()
sync_dates['articles'] = utc.format()
write_data(sync_dates, 'sync_dates')
write_data(article_map, 'article_map')
write_js_redirects(article_map)
