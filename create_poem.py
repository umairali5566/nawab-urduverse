from core.models import Author
from poetry.models import Poetry

author = Author.objects.get(slug='alama-iqbal')
poem = Poetry.objects.create(
    title='Ø§Ø²Ù„Ø§Ù†',
    author=author,
    content='<p><br /> Ù†ÛÛŒÚº ØªÛŒØ±Ø§ Ù†Ø´ÛŒÙ…Ù† Ù‚ØµØ± Ø³Ù„Ø·Ø§Ù†ÛŒ Ú©Û’ Ú¯Ù†Ø¨Ø¯ Ù¾Ø±<br /> ØªÙˆ Ø´Ø§ÛÛŒÚº ÛÛ’ Ø¨Ø³ÛŒØ±Ø§ Ú©Ø± Ù¾ÛØ§Ú‘ÙˆÚº Ú©ÛŒ Ú†Ù¹Ø§Ù†ÙˆÚº Ù…ÛŒÚº</p>',
    poetry_type='shayari',
    mood='philosophical',
    slug='zln'
)
poem.save()
print('Created poem ID:', poem.id, 'Slug:', poem.slug)