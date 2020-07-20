import arrow

from helpers import read_data, write_data, get_settings
import api


settings = get_settings()
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['attachments'])
article_map = read_data('article_map')
attachment_map = read_data('attachment_map')
attachment_article_map = read_data('attachment_article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting attachments in article {}...'.format(src_article))
    url = '{}/{}/articles/{}/attachments.json'.format(settings['src_root'], settings['locale'], src_article)
    attachments = api.get_resource_list(url, list_name='article_attachments', paginate=False)
    if not attachments:
        print('- no attachments found')
        continue
    for src_attachment in attachments:
        if last_sync < arrow.get(src_attachment['created_at']):
            print('- adding new attachment {} to article {}'.format(src_attachment['file_name'], dst_article))
            print(src_attachment)
            url = '{}/articles/{}/attachments.json'.format(settings['dst_root'], dst_article)
            new_attachment = api.post_attachment(url, src_attachment)
            if new_attachment is False:
                print('Skipping attachment {}'.format(src_attachment['file_name']))
                continue
            attachment_map[str(src_attachment['id'])] = new_attachment['id']
            attachment_article_map[str(src_attachment['id'])] = src_article
            continue
        print('- attachment {} is up to date'.format(src_attachment['file_name']))

utc = arrow.utcnow()
sync_dates['attachments'] = utc.format()
write_data(sync_dates, 'sync_dates')
write_data(attachment_map, 'attachment_map')
write_data(attachment_article_map, 'attachment_article_map')
